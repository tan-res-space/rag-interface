"""
Multi-Modal Embedding Adapter

Advanced embedding adapter that supports multiple content types and modalities.
Handles text, audio metadata, speaker characteristics, and contextual information.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import json
import hashlib

from rag_integration_service.application.ports.secondary.ml_model_port import MLModelPort as BaseEmbeddingAdapter
from rag_integration_service.domain.value_objects.embedding_type import EmbeddingType

logger = logging.getLogger(__name__)


class ContentModality(Enum):
    """Supported content modalities."""
    TEXT = "text"
    AUDIO_METADATA = "audio_metadata"
    SPEAKER_PROFILE = "speaker_profile"
    CONTEXTUAL = "contextual"
    HYBRID = "hybrid"


class MultiModalContent:
    """Container for multi-modal content."""
    
    def __init__(
        self,
        text: str,
        modality: ContentModality = ContentModality.TEXT,
        audio_metadata: Optional[Dict[str, Any]] = None,
        speaker_profile: Optional[Dict[str, Any]] = None,
        contextual_data: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.modality = modality
        self.audio_metadata = audio_metadata or {}
        self.speaker_profile = speaker_profile or {}
        self.contextual_data = contextual_data or {}


class MultiModalEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    Multi-modal embedding adapter for diverse content types.
    
    Generates embeddings that incorporate multiple modalities including
    text content, audio characteristics, speaker profiles, and context.
    """

    def __init__(
        self,
        text_adapter: BaseEmbeddingAdapter,
        enable_audio_features: bool = True,
        enable_speaker_features: bool = True,
        enable_contextual_features: bool = True,
        feature_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize multi-modal embedding adapter.
        
        Args:
            text_adapter: Base text embedding adapter
            enable_audio_features: Whether to include audio metadata features
            enable_speaker_features: Whether to include speaker profile features
            enable_contextual_features: Whether to include contextual features
            feature_weights: Weights for different feature types
        """
        self.text_adapter = text_adapter
        self.enable_audio_features = enable_audio_features
        self.enable_speaker_features = enable_speaker_features
        self.enable_contextual_features = enable_contextual_features
        
        # Default feature weights
        self.feature_weights = feature_weights or {
            "text": 0.6,
            "audio": 0.15,
            "speaker": 0.15,
            "contextual": 0.1
        }
        
        # Normalize weights
        total_weight = sum(self.feature_weights.values())
        self.feature_weights = {k: v / total_weight for k, v in self.feature_weights.items()}
        
        logger.info(f"Initialized multi-modal adapter with weights: {self.feature_weights}")

    async def generate_embedding(
        self,
        text: str,
        embedding_type: EmbeddingType = EmbeddingType.ERROR,
        content: Optional[MultiModalContent] = None
    ) -> List[float]:
        """
        Generate multi-modal embedding.
        
        Args:
            text: Primary text content
            embedding_type: Type of embedding
            content: Multi-modal content container
            
        Returns:
            Multi-modal embedding vector
        """
        try:
            # Create content container if not provided
            if content is None:
                content = MultiModalContent(text)
            
            # Generate base text embedding
            text_embedding = await self.text_adapter.generate_embedding(text, embedding_type)
            
            # Generate feature embeddings
            feature_embeddings = {}
            
            # Audio features
            if self.enable_audio_features and content.audio_metadata:
                feature_embeddings["audio"] = self._generate_audio_features(content.audio_metadata)
            
            # Speaker features
            if self.enable_speaker_features and content.speaker_profile:
                feature_embeddings["speaker"] = self._generate_speaker_features(content.speaker_profile)
            
            # Contextual features
            if self.enable_contextual_features and content.contextual_data:
                feature_embeddings["contextual"] = self._generate_contextual_features(content.contextual_data)
            
            # Combine all embeddings
            multimodal_embedding = self._combine_multimodal_embeddings(
                text_embedding, feature_embeddings
            )
            
            logger.debug(f"Generated multi-modal embedding with {len(feature_embeddings)} modalities")
            return multimodal_embedding
            
        except Exception as e:
            logger.error(f"Failed to generate multi-modal embedding: {e}")
            # Fallback to text-only embedding
            return await self.text_adapter.generate_embedding(text, embedding_type)

    async def generate_batch_embeddings(
        self,
        texts: List[str],
        embedding_type: EmbeddingType = EmbeddingType.ERROR,
        contents: Optional[List[MultiModalContent]] = None
    ) -> List[List[float]]:
        """
        Generate multi-modal embeddings for multiple texts.
        
        Args:
            texts: List of texts
            embedding_type: Type of embedding
            contents: List of multi-modal content containers
            
        Returns:
            List of multi-modal embedding vectors
        """
        try:
            embeddings = []
            
            # Ensure contents list matches texts length
            if contents is None:
                contents = [MultiModalContent(text) for text in texts]
            elif len(contents) != len(texts):
                logger.warning("Contents length doesn't match texts length")
                contents = contents + [MultiModalContent(texts[i]) for i in range(len(contents), len(texts))]
            
            # Generate embeddings
            for i, text in enumerate(texts):
                content = contents[i] if i < len(contents) else MultiModalContent(text)
                embedding = await self.generate_embedding(text, embedding_type, content)
                embeddings.append(embedding)
            
            logger.debug(f"Generated {len(embeddings)} multi-modal embeddings in batch")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch multi-modal embeddings: {e}")
            # Fallback to text-only embeddings
            return await self.text_adapter.generate_batch_embeddings(texts, embedding_type)

    def _generate_audio_features(self, audio_metadata: Dict[str, Any]) -> List[float]:
        """
        Generate audio feature vector from metadata.
        
        Args:
            audio_metadata: Audio metadata dictionary
            
        Returns:
            Audio feature vector
        """
        try:
            features = []
            
            # Audio quality features
            quality = audio_metadata.get("quality", "medium")
            quality_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "excellent": 1.0}
            features.append(quality_map.get(quality, 0.5))
            
            # Background noise level
            noise_level = audio_metadata.get("background_noise", "medium")
            noise_map = {"low": 0.1, "medium": 0.5, "high": 0.8, "very_high": 1.0}
            features.append(noise_map.get(noise_level, 0.5))
            
            # Speaker clarity
            clarity = audio_metadata.get("speaker_clarity", "clear")
            clarity_map = {"unclear": 0.2, "somewhat_clear": 0.4, "clear": 0.7, "very_clear": 1.0}
            features.append(clarity_map.get(clarity, 0.7))
            
            # Number of speakers (normalized)
            num_speakers = audio_metadata.get("number_of_speakers", 1)
            features.append(min(num_speakers / 10.0, 1.0))  # Normalize to 0-1
            
            # Overlapping speech indicator
            overlapping = audio_metadata.get("overlapping_speech", False)
            features.append(1.0 if overlapping else 0.0)
            
            # Pad to standard size (64 features)
            while len(features) < 64:
                features.append(0.0)
            
            return features[:64]  # Ensure exactly 64 features
            
        except Exception as e:
            logger.error(f"Failed to generate audio features: {e}")
            return [0.0] * 64

    def _generate_speaker_features(self, speaker_profile: Dict[str, Any]) -> List[float]:
        """
        Generate speaker feature vector from profile.
        
        Args:
            speaker_profile: Speaker profile dictionary
            
        Returns:
            Speaker feature vector
        """
        try:
            features = []
            
            # Speaker experience level
            experience = speaker_profile.get("experience_level", "intermediate")
            exp_map = {"beginner": 0.2, "intermediate": 0.5, "advanced": 0.8, "expert": 1.0}
            features.append(exp_map.get(experience, 0.5))
            
            # Native language indicator
            native_lang = speaker_profile.get("native_language", "unknown")
            # Simple encoding for common languages
            lang_features = [0.0] * 10
            lang_map = {
                "english": 0, "spanish": 1, "french": 2, "german": 3, "chinese": 4,
                "japanese": 5, "korean": 6, "arabic": 7, "hindi": 8, "other": 9
            }
            if native_lang.lower() in lang_map:
                lang_features[lang_map[native_lang.lower()]] = 1.0
            features.extend(lang_features)
            
            # Accent strength
            accent = speaker_profile.get("accent_strength", "moderate")
            accent_map = {"none": 0.0, "slight": 0.25, "moderate": 0.5, "strong": 0.75, "very_strong": 1.0}
            features.append(accent_map.get(accent, 0.5))
            
            # Speaking rate
            rate = speaker_profile.get("speaking_rate", "normal")
            rate_map = {"very_slow": 0.1, "slow": 0.3, "normal": 0.5, "fast": 0.7, "very_fast": 0.9}
            features.append(rate_map.get(rate, 0.5))
            
            # Pad to standard size (64 features)
            while len(features) < 64:
                features.append(0.0)
            
            return features[:64]  # Ensure exactly 64 features
            
        except Exception as e:
            logger.error(f"Failed to generate speaker features: {e}")
            return [0.0] * 64

    def _generate_contextual_features(self, contextual_data: Dict[str, Any]) -> List[float]:
        """
        Generate contextual feature vector.
        
        Args:
            contextual_data: Contextual data dictionary
            
        Returns:
            Contextual feature vector
        """
        try:
            features = []
            
            # Domain/topic features
            domain = contextual_data.get("domain", "general")
            domain_map = {
                "general": 0, "technical": 1, "medical": 2, "legal": 3, "financial": 4,
                "educational": 5, "entertainment": 6, "news": 7, "business": 8, "other": 9
            }
            domain_features = [0.0] * 10
            if domain.lower() in domain_map:
                domain_features[domain_map[domain.lower()]] = 1.0
            features.extend(domain_features)
            
            # Complexity level
            complexity = contextual_data.get("complexity", "medium")
            comp_map = {"simple": 0.2, "medium": 0.5, "complex": 0.8, "very_complex": 1.0}
            features.append(comp_map.get(complexity, 0.5))
            
            # Formality level
            formality = contextual_data.get("formality", "neutral")
            form_map = {"informal": 0.2, "neutral": 0.5, "formal": 0.8, "very_formal": 1.0}
            features.append(form_map.get(formality, 0.5))
            
            # Specialized knowledge required
            specialized = contextual_data.get("requires_specialized_knowledge", False)
            features.append(1.0 if specialized else 0.0)
            
            # Pad to standard size (64 features)
            while len(features) < 64:
                features.append(0.0)
            
            return features[:64]  # Ensure exactly 64 features
            
        except Exception as e:
            logger.error(f"Failed to generate contextual features: {e}")
            return [0.0] * 64

    def _combine_multimodal_embeddings(
        self,
        text_embedding: List[float],
        feature_embeddings: Dict[str, List[float]]
    ) -> List[float]:
        """
        Combine text embedding with feature embeddings.
        
        Args:
            text_embedding: Base text embedding
            feature_embeddings: Dictionary of feature embeddings
            
        Returns:
            Combined multi-modal embedding
        """
        try:
            # Start with weighted text embedding
            combined = [x * self.feature_weights["text"] for x in text_embedding]
            
            # Add feature embeddings
            for feature_type, embedding in feature_embeddings.items():
                weight = self.feature_weights.get(feature_type, 0.0)
                if weight > 0:
                    # Resize feature embedding to match text embedding dimension
                    resized_embedding = self._resize_embedding(embedding, len(text_embedding))
                    
                    # Add weighted feature embedding
                    for i in range(len(combined)):
                        combined[i] += weight * resized_embedding[i]
            
            # Normalize the combined embedding
            magnitude = sum(x * x for x in combined) ** 0.5
            if magnitude > 0:
                combined = [x / magnitude for x in combined]
            
            return combined
            
        except Exception as e:
            logger.error(f"Failed to combine multi-modal embeddings: {e}")
            return text_embedding

    def _resize_embedding(self, embedding: List[float], target_size: int) -> List[float]:
        """
        Resize embedding to target size using interpolation or padding.
        
        Args:
            embedding: Source embedding
            target_size: Target embedding size
            
        Returns:
            Resized embedding
        """
        if len(embedding) == target_size:
            return embedding
        
        if len(embedding) > target_size:
            # Downsample using averaging
            step = len(embedding) / target_size
            resized = []
            for i in range(target_size):
                start_idx = int(i * step)
                end_idx = int((i + 1) * step)
                avg_value = sum(embedding[start_idx:end_idx]) / (end_idx - start_idx)
                resized.append(avg_value)
            return resized
        else:
            # Upsample using repetition and interpolation
            resized = embedding.copy()
            while len(resized) < target_size:
                resized.extend(embedding[:target_size - len(resized)])
            return resized[:target_size]

    async def get_model_info(self) -> Dict[str, Any]:
        """Get multi-modal model information."""
        base_info = await self.text_adapter.get_model_info()
        
        multimodal_info = {
            "adapter_type": "multimodal",
            "enabled_features": {
                "audio": self.enable_audio_features,
                "speaker": self.enable_speaker_features,
                "contextual": self.enable_contextual_features
            },
            "feature_weights": self.feature_weights,
            "base_adapter": base_info
        }
        
        return multimodal_info

    async def health_check(self) -> bool:
        """Check health of multi-modal adapter."""
        try:
            return await self.text_adapter.health_check()
        except Exception as e:
            logger.error(f"Multi-modal adapter health check failed: {e}")
            return False

    # Implement abstract methods by delegating to text adapter
    async def get_model_name(self) -> str:
        """Get model name."""
        return await self.text_adapter.get_model_name()

    async def get_model_version(self) -> str:
        """Get model version."""
        return await self.text_adapter.get_model_version()

    async def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return await self.text_adapter.get_embedding_dimension()

    async def get_max_sequence_length(self) -> int:
        """Get maximum sequence length."""
        return await self.text_adapter.get_max_sequence_length()

    async def get_max_batch_size(self) -> int:
        """Get maximum batch size."""
        return await self.text_adapter.get_max_batch_size()

    async def validate_text(self, text: str) -> bool:
        """Validate text input."""
        return await self.text_adapter.validate_text(text)

    async def preprocess_text(self, text: str) -> str:
        """Preprocess text."""
        return await self.text_adapter.preprocess_text(text)

    async def estimate_tokens(self, text: str) -> int:
        """Estimate token count."""
        return await self.text_adapter.estimate_tokens(text)

    async def warm_up(self) -> bool:
        """Warm up the model."""
        return await self.text_adapter.warm_up()
