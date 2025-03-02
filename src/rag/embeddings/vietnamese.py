from typing import Dict, Any, List, Optional, Union
import numpy as np
from langchain.embeddings.base import Embeddings

from src.utils.logging import get_logger

logger = get_logger(__name__)

class VietnameseOptimizedEmbeddings(Embeddings):
    """
    Embeddings optimized for Vietnamese text.
    
    This class enhances standard embeddings by:
    1. Using multilingual models that understand Vietnamese
    2. Applying preprocessing specific to Vietnamese
    3. Supporting hybrid approaches for better accuracy
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        preprocessing: bool = True,
        use_hybrid: bool = True,
        device: Optional[str] = None
    ):
        """
        Initialize Vietnamese-optimized embeddings.
        
        Args:
            model_name: Name of the embedding model
            preprocessing: Whether to apply Vietnamese-specific preprocessing
            use_hybrid: Whether to use hybrid approach (combining different embeddings)
            device: Device to use ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.preprocessing = preprocessing
        self.use_hybrid = use_hybrid
        
        # Import here to avoid loading models unnecessarily
        from sentence_transformers import SentenceTransformer
        
        # Set device (CPU or GPU)
        from src.config.settings import settings
        self.device = device or ("cuda" if settings.USE_GPU else "cpu")
        
        logger.info(f"Initializing Vietnamese embeddings with model {model_name} on {self.device}")
        
        # Load the model
        self.model = SentenceTransformer(model_name, device=self.device)
        
        # Load secondary model for hybrid approach if enabled
        self.secondary_model = None
        if use_hybrid:
            # PhoBERT or a model specifically fine-tuned for Vietnamese
            secondary_model_name = "vinai/phobert-base"
            try:
                from transformers import AutoModel, AutoTokenizer
                self.secondary_tokenizer = AutoTokenizer.from_pretrained(secondary_model_name)
                self.secondary_model = AutoModel.from_pretrained(secondary_model_name)
                self.secondary_model.to(self.device)
                logger.info(f"Loaded secondary model {secondary_model_name} for hybrid embeddings")
            except Exception as e:
                logger.warning(f"Failed to load secondary model: {str(e)}")
                self.use_hybrid = False
    
    def _preprocess_vietnamese(self, text: str) -> str:
        """
        Apply Vietnamese-specific preprocessing.
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not self.preprocessing:
            return text
        
        # Simple preprocessing
        # In a production system, use a proper Vietnamese tokenizer/preprocessor
        
        # Replace common Vietnamese diacritics issues
        replacements = {
            "òa": "oà", "óa": "oá", "ỏa": "oả", "õa": "oã", "ọa": "oạ",
            "òe": "oè", "óe": "oé", "ỏe": "oẻ", "õe": "oẽ", "ọe": "oẹ",
            "ùy": "uỳ", "úy": "uý", "ủy": "uỷ", "ũy": "uỹ", "ụy": "uỵ"
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _get_secondary_embedding(self, text: str) -> List[float]:
        """
        Get embeddings from the secondary model.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        import torch
        
        # Preprocess and tokenize
        inputs = self.secondary_tokenizer(
            text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=512
        )
        
        # Move inputs to the same device as the model
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.secondary_model(**inputs)
        
        # Use [CLS] token embedding as the sentence embedding
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
        
        return embedding.tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        # Preprocess texts
        if self.preprocessing:
            texts = [self._preprocess_vietnamese(text) for text in texts]
        
        # Get primary embeddings
        primary_embeddings = self.model.encode(texts)
        
        # If not using hybrid approach, return primary embeddings
        if not self.use_hybrid or self.secondary_model is None:
            return primary_embeddings.tolist()
        
        # Get secondary embeddings and combine
        combined_embeddings = []
        for i, text in enumerate(texts):
            try:
                secondary_embedding = self._get_secondary_embedding(text)
                
                # Combine embeddings (simple concatenation with normalization)
                primary = np.array(primary_embeddings[i])
                secondary = np.array(secondary_embedding)
                
                # Resize to same dimension if needed
                if len(primary) != len(secondary):
                    # Use the smaller dimension
                    min_dim = min(len(primary), len(secondary))
                    primary = primary[:min_dim]
                    secondary = secondary[:min_dim]
                
                # Weighted average (50-50 by default)
                combined = 0.5 * primary + 0.5 * secondary
                
                # Normalize
                combined = combined / np.linalg.norm(combined)
                
                combined_embeddings.append(combined.tolist())
            except Exception as e:
                logger.warning(f"Error in secondary embedding: {str(e)}, falling back to primary")
                combined_embeddings.append(primary_embeddings[i].tolist())
        
        return combined_embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        # For queries, the process is the same as for documents
        return self.embed_documents([text])[0]

def get_vietnamese_embeddings() -> VietnameseOptimizedEmbeddings:
    """Factory function to create Vietnamese optimized embeddings."""
    return VietnameseOptimizedEmbeddings(
        use_hybrid=True
    )
