
from langchain_ollama.chat_models import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings
from typing import Dict

class LLMManager:
    """
    Manager class that provides access to different LLM models.
    This class only provides model instances; the actual LLM calling is handled separately.
    """
    def __init__(self):
        # Initialize models dictionary to store instances
        self.models: Dict[str, ChatOllama | OllamaEmbeddings] = {}
    
    def get_qwen(self) -> ChatOllama:
        """
        Get the Qwen 14B model instance.
        
        Returns:
            ChatOllama instance for Qwen 14B
        """
        if "qwen3_14b" not in self.models:
            self.models["qwen3_14b"] = ChatOllama(model="qwen3:14b")
        return self.models["qwen3_14b"]
    
    def get_gemma(self) -> ChatOllama:
        """
        Get the Gemma latest model instance.
        
        Returns:
            ChatOllama instance for Gemma
        """
        if "gemma3_latest" not in self.models:
            self.models["gemma3_latest"] = ChatOllama(model="gemma3:latest")
        return self.models["gemma3_latest"]
    
    def get_nomic_embeddings(self) -> OllamaEmbeddings:
        """
        Get the Nomic embeddings model instance.
        
        Returns:
            OllamaEmbeddings instance for Nomic
        """
        if "nomic_embed" not in self.models:
            self.models["nomic_embed"] = OllamaEmbeddings(model="nomic-embed-text:latest")
        return self.models["nomic_embed"]
    
    def get_codellama(self) -> ChatOllama:
        """
        Get the CodeLlama 13B model instance.
        
        Returns:
            ChatOllama instance for CodeLlama
        """
        if "codellama_13b" not in self.models:
            self.models["codellama_13b"] = ChatOllama(model="codellama:13b")
        return self.models["codellama_13b"]
    
    def get_llama(self) -> ChatOllama:
        """
        Get the Llama 3.2 latest model instance.
        
        Returns:
            ChatOllama instance for Llama 3.2
        """
        if "llama3_2_latest" not in self.models:
            self.models["llama3_2_latest"] = ChatOllama(model="llama3.2:latest")
        return self.models["llama3_2_latest"]

# Create a singleton instance for easy import
llm_manager = LLMManager()
