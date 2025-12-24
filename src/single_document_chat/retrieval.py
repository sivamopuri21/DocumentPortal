import os
import sys
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriver, create_retrival_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPoratalException
from logger.custom_logger import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self,session_id:str,retriever) -> None:
        try:
            self.log = CustomLogger().get_logger(__name__)
        except Exception as e:
            self.log.error("Error initializing ConversationalRAG", error=str(e), session=session_id)
            raise DocumentPoratalException("Error initializing ConversationalRAG",sys)
        
    def _load_llm(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error loading LLM", error=str(e),session=self.session_id)
            raise DocumentPoratalException("Error loading LLM", sys)
        
    def _get_session_history(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error getting session history", error=str(e),session=self.session_id)
            raise DocumentPoratalException("Error getting session history", sys)
        
    def load_retriver_from_faiss(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error loading retriever from FAISS", error=str(e),session=self.session_id)
            raise DocumentPoratalException("Error loading retriever from FAISS", sys)
        
    def invoke(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error invoking ConversationalRAG", error=str(e), session=self.session_id)
            raise DocumentPoratalException("Error invoking ConversationalRAG", sys)