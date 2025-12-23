import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config_loader import load_config
from langchain_groq import ChatGroq
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPoratalException
import sys

log = CustomLogger().get_logger(__name__)

class ModelLoader:
    def __init__(self):
        """
        A utility class to load the configurations"""
        load_dotenv()
        self._validate_env()
        self.config = load_config()
        log.info("Configurations loaded successfully",config_keys=list(self.config.keys()))

    def _validate_env(self):
        """
        Validate necessary environment variables.
        Ensure API keys exists
        """
        required_vars = ["GOOGLE_API_KEY", "GROQ_API_KEY"]
        self.api_keys={key:os.getenv(key) for key in required_vars}
        missing_keys = [key for key, value in self.api_keys.items() if not value]
        if missing_keys:
            log.error("Missing environment variables", missing_keys=missing_keys)
            raise DocumentPoratalException("Missing environment variables", sys)
        log.info("Environment variables validated",available_keys=[k for k in self.api_keys if self.api_keys[k]])

    def load_embeddings(self):
        """Load and return the embedding model"""
        try:
            log.info("Loading embedding model...")
            model_name = self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(model=model_name)
        except Exception as e:
            log.error("Failed to load embeddings", error=str(e))
            raise DocumentPoratalException("Failed to load embeddings", sys)
    def load_llm(self):
        """Loading the llm and return the LLM model"""
        """Load LLM dynamicall based on provider in config."""
        llm_block = self.config["llm"]
        provider_key = os.getenv("LLM_PROVIDER", "google")

        if provider_key not in llm_block:
            log.error("Invalid LLM provider specified", provider=provider_key)
            raise ValueError(f"Provider '{provider_key}' not found in config")
        
        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature",0.2)
        max_tokens = llm_config.get("max_output_tokens",2048)

        log.info("Loading LLM...",provider=provider,model=model_name,temperature=temperature,max_tokens = max_tokens)

        if provider == "google":
            llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature, max_output_tokens=max_tokens)
            return llm
        elif provider == "groq":
            llm = ChatGroq(temperature=temperature, model_name=model_name, max_tokens=max_tokens)
            return llm
        else:
            log.error("Invalid LLM provider specified", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}", sys)   



if __name__ == "__main__":
    model_loader = ModelLoader()
    embeddings = model_loader.load_embeddings()
    print(f"Embeddinf Model Loaded :{embeddings}")
    
    llm = model_loader.load_llm()
    print(f"LLM Loaded:{llm}")

    result = llm.invoke("What is the capital of India?")
    print(f"LLM Response:{result.content}")

