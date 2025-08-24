
import re
import pandas as pd
import torch
import nltk
from nltk.metrics.distance import edit_distance
from sentence_transformers import SentenceTransformer, util
nltk.download('punkt')

def load_sentences(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r'\s+', ' ', text)
    return [s.strip() for s in re.split(r'\.\s+|\.$', text) if s.strip()]

def compute_ser(asr, final):
    """
    Compute Sentence Edit Rate (SER) between ASR hypothesis and final reference.
    
    SER = (Edit Distance / Reference Length) × 100
    
    This follows standard speech recognition evaluation practices where:
    - Edit distance captures all operations (insertions, deletions, substitutions)
    - Reference length provides the normalization factor
    - Individual metrics are provided for detailed analysis
    - Move operations detect word reorderings
    
    Args:
        asr (str): ASR hypothesis sentence
        final (str): Final reference sentence
        
    Returns:
        tuple: (insert_pct, delete_pct, move_pct, edit_pct, ser)
    """
    draft_tokens = nltk.word_tokenize(asr.lower())
    final_tokens = nltk.word_tokenize(final.lower())

    # Calculate individual operation counts for detailed analysis
    insertions = len([w for w in final_tokens if w not in draft_tokens])
    deletions = len([w for w in draft_tokens if w not in final_tokens])
    
    # Calculate move operations: words that exist in both but in different relative positions
    common_words = set(draft_tokens) & set(final_tokens)
    moved_words = 0
    
    for word in common_words:
        # Get all positions of this word in both sentences
        asr_positions = [i for i, w in enumerate(draft_tokens) if w == word]
        final_positions = [i for i, w in enumerate(final_tokens) if w == word]
        
        # For words that appear once in each sentence, check if position changed significantly
        if len(asr_positions) == 1 and len(final_positions) == 1:
            # Calculate relative positions (0.0 to 1.0)
            asr_rel_pos = asr_positions[0] / len(draft_tokens) if len(draft_tokens) > 0 else 0
            final_rel_pos = final_positions[0] / len(final_tokens) if len(final_tokens) > 0 else 0
            
            # If relative position changed by more than 10%, consider it a move
            if abs(asr_rel_pos - final_rel_pos) > 0.1:
                moved_words += 1
        
        # For words with multiple occurrences, use a simpler heuristic
        elif len(asr_positions) > 1 or len(final_positions) > 1:
            # Count as moved if the word appears different number of times at different positions
            if len(asr_positions) != len(final_positions):
                moved_words += min(len(asr_positions), len(final_positions))
    
    # Calculate edit distance (captures all operations)
    edit_distance_ops = edit_distance(draft_tokens, final_tokens)
    
    # Use reference length for normalization (standard in speech recognition)
    reference_length = len(final_tokens) or 1
    hypothesis_length = len(draft_tokens) or 1
    
    # Calculate percentages for detailed breakdown
    insert_pct = (insertions / reference_length) * 100
    delete_pct = (deletions / hypothesis_length) * 100  # Deletions relative to hypothesis
    move_pct = (moved_words / reference_length) * 100   # Moves relative to reference
    
    # SER: Normalized edit distance (standard approach)
    ser = (edit_distance_ops / reference_length) * 100
    
    # For backward compatibility, provide edit_pct as normalized edit distance
    edit_pct = ser
    
    return insert_pct, delete_pct, move_pct, edit_pct, ser

def main():
    asr_sentences = load_sentences("src/ser_similarity_matrix_bundle/asr_draft.txt")
    final_sentences = load_sentences("src/ser_similarity_matrix_bundle/final_draft.txt")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    asr_embeddings = model.encode(asr_sentences, convert_to_tensor=True)
    final_embeddings = model.encode(final_sentences, convert_to_tensor=True)

    cosine_scores = util.cos_sim(asr_embeddings, final_embeddings).cpu().numpy()

    results = []
    threshold = 0.7
    for i, asr in enumerate(asr_sentences):
        for j, final in enumerate(final_sentences):
            score = cosine_scores[i][j]
            if score > threshold:
                insert_pct, delete_pct, move_pct, edit_pct, ser = compute_ser(asr, final)
                results.append({
                    "ASR Sentence": asr,
                    "Final Sentence": final,
                    "Similarity": round(score, 3),
                    "Insert %": round(insert_pct, 2),
                    "Delete %": round(delete_pct, 2),
                    "Move %": round(move_pct, 2),
                    "Edit %": round(edit_pct, 2),
                    "Sentence Edit Rate (SER)": round(ser, 2)
                })

    df = pd.DataFrame(results)
    df.to_csv("sentence_edit_rate_output.csv", index=False)
    print("✅ SER matrix saved to 'sentence_edit_rate_output.csv'")

if __name__ == "__main__":
    main()
