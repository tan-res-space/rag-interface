"""
SER (Sentence Edit Rate) Calculation Service

Domain service for computing comprehensive SER metrics for quality assessment.
Adapted from reference implementation with enhanced features for speaker bucket management.
"""

import re
from typing import List, Tuple, Set, Dict, Any
from decimal import Decimal

from ..value_objects.ser_metrics import SERMetrics


class SERCalculationService:
    """
    Domain service for computing SER (Sentence Edit Rate) metrics.
    
    This service implements comprehensive SER computation logic, providing detailed
    analysis of insertions, deletions, moves, and overall edit rates for ASR quality assessment.
    """
    
    def __init__(self):
        """Initialize SER calculation service."""
        pass
    
    def calculate_ser(self, asr_text: str, reference_text: str) -> SERMetrics:
        """
        Calculate comprehensive SER metrics for a text pair.
        
        SER = (Edit Distance / Reference Length) × 100
        
        Args:
            asr_text: ASR hypothesis text
            reference_text: Reference/corrected text
            
        Returns:
            SERMetrics: Comprehensive metrics including SER, insertions, deletions, moves
        """
        # Normalize and tokenize texts
        asr_tokens = self._tokenize_text(self._normalize_text(asr_text))
        ref_tokens = self._tokenize_text(self._normalize_text(reference_text))
        
        # Calculate edit distance and individual operation counts
        edit_distance = self._calculate_edit_distance(asr_tokens, ref_tokens)
        insertions = self._count_insertions(asr_tokens, ref_tokens)
        deletions = self._count_deletions(asr_tokens, ref_tokens)
        moves = self._count_moves(asr_tokens, ref_tokens)
        
        # Calculate lengths
        reference_length = len(ref_tokens) or 1  # Avoid division by zero
        hypothesis_length = len(asr_tokens) or 1
        
        # Calculate percentages
        insert_pct = (insertions / reference_length) * 100
        delete_pct = (deletions / hypothesis_length) * 100
        move_pct = (moves / reference_length) * 100
        
        # SER: Normalized edit distance
        ser_score = (edit_distance / reference_length) * 100
        
        return SERMetrics.create(
            ser_score=float(ser_score),
            insert_percentage=float(insert_pct),
            delete_percentage=float(delete_pct),
            move_percentage=float(move_pct),
            edit_distance=edit_distance,
            reference_length=reference_length,
            hypothesis_length=hypothesis_length
        )
    
    def calculate_batch_ser(self, text_pairs: List[Tuple[str, str]]) -> List[SERMetrics]:
        """
        Calculate SER metrics for multiple text pairs efficiently.
        
        Args:
            text_pairs: List of (asr_text, reference_text) tuples
            
        Returns:
            List[SERMetrics]: SER metrics for each pair
        """
        return [
            self.calculate_ser(asr_text, ref_text)
            for asr_text, ref_text in text_pairs
        ]
    
    def compare_ser_metrics(self, original_metrics: SERMetrics, corrected_metrics: SERMetrics) -> Dict[str, Any]:
        """
        Compare two SER metrics to assess improvement.
        
        Args:
            original_metrics: Original ASR SER metrics
            corrected_metrics: RAG-corrected SER metrics
            
        Returns:
            Dictionary with comparison results
        """
        improvement = original_metrics.ser_score - corrected_metrics.ser_score
        improvement_percentage = corrected_metrics.calculate_improvement_percentage(original_metrics)
        
        return {
            "original_ser": float(original_metrics.ser_score),
            "corrected_ser": float(corrected_metrics.ser_score),
            "improvement": float(improvement),
            "improvement_percentage": float(improvement_percentage),
            "is_significant_improvement": corrected_metrics.has_significant_improvements_over(original_metrics),
            "original_quality_level": original_metrics.get_quality_level(),
            "corrected_quality_level": corrected_metrics.get_quality_level(),
            "quality_level_improved": (
                corrected_metrics.get_quality_level() != original_metrics.get_quality_level() and
                corrected_metrics.ser_score < original_metrics.ser_score
            )
        }
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent processing.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation for word-level comparison
        text = re.sub(r'[^\w\s]', '', text)
        
        return text.strip()
    
    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        return text.split()
    
    def _calculate_edit_distance(self, tokens1: List[str], tokens2: List[str]) -> int:
        """
        Calculate edit distance between two token sequences using dynamic programming.
        
        Args:
            tokens1: First token sequence
            tokens2: Second token sequence
            
        Returns:
            Edit distance
        """
        m, n = len(tokens1), len(tokens2)
        
        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize base cases
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if tokens1[i-1] == tokens2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # deletion
                        dp[i][j-1],    # insertion
                        dp[i-1][j-1]   # substitution
                    )
        
        return dp[m][n]
    
    def _count_insertions(self, asr_tokens: List[str], ref_tokens: List[str]) -> int:
        """Count words that appear in reference but not in ASR (insertions)."""
        asr_set = set(asr_tokens)
        return len([word for word in ref_tokens if word not in asr_set])
    
    def _count_deletions(self, asr_tokens: List[str], ref_tokens: List[str]) -> int:
        """Count words that appear in ASR but not in reference (deletions)."""
        ref_set = set(ref_tokens)
        return len([word for word in asr_tokens if word not in ref_set])
    
    def _count_moves(self, asr_tokens: List[str], ref_tokens: List[str]) -> int:
        """
        Count words that exist in both sentences but in different relative positions.
        
        This implements a heuristic for detecting word reorderings.
        """
        common_words = set(asr_tokens) & set(ref_tokens)
        moved_words = 0
        
        for word in common_words:
            # Get all positions of this word in both sentences
            asr_positions = [i for i, w in enumerate(asr_tokens) if w == word]
            ref_positions = [i for i, w in enumerate(ref_tokens) if w == word]
            
            # For words that appear once in each sentence, check if position changed significantly
            if len(asr_positions) == 1 and len(ref_positions) == 1:
                # Calculate relative positions (0.0 to 1.0)
                asr_rel_pos = asr_positions[0] / len(asr_tokens) if len(asr_tokens) > 0 else 0
                ref_rel_pos = ref_positions[0] / len(ref_tokens) if len(ref_tokens) > 0 else 0
                
                # If relative position changed by more than 10%, consider it a move
                if abs(asr_rel_pos - ref_rel_pos) > 0.1:
                    moved_words += 1
            
            # For words with multiple occurrences, use frequency difference as proxy
            elif len(asr_positions) > 1 or len(ref_positions) > 1:
                if len(asr_positions) != len(ref_positions):
                    moved_words += min(len(asr_positions), len(ref_positions))
        
        return moved_words
    
    def calculate_speaker_average_ser(self, ser_metrics_list: List[SERMetrics]) -> Decimal:
        """
        Calculate average SER score for a speaker from multiple metrics.
        
        Args:
            ser_metrics_list: List of SER metrics for the speaker
            
        Returns:
            Average SER score
        """
        if not ser_metrics_list:
            return Decimal('0')
        
        total_ser = sum(metrics.ser_score for metrics in ser_metrics_list)
        average_ser = total_ser / len(ser_metrics_list)
        
        return average_ser.quantize(Decimal('0.01'))  # Round to 2 decimal places
    
    def get_quality_distribution(self, ser_metrics_list: List[SERMetrics]) -> Dict[str, int]:
        """
        Get distribution of quality levels from SER metrics.
        
        Args:
            ser_metrics_list: List of SER metrics
            
        Returns:
            Dictionary with quality level counts
        """
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for metrics in ser_metrics_list:
            quality_level = metrics.get_quality_level()
            distribution[quality_level] += 1
        
        return distribution
