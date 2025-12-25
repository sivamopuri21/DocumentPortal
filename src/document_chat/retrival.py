import os
import sys
from operator import itemgetter
from typing import List, Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPoratalException

from logger.custom_logger import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    """
        LCEL-based Conversational RAG with lazy retriever initialization.

        Usage:
            rag = ConversationalRAG(session_id="abc")
            rag.load_retriever_from_faiss(index_path="faiss_index/abc", k=5, index_name="index")
            answer = rag.invoke("What is ...?", chat_history=[])
    """
    def __init__(self, session_id: Optional[str], retriever=None):
        
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.llm = self._load_llm()
            self.contextualize_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt:ChatPromptTemplate =PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            self.retriever = retriever  # Allow None initially
            self.chain = None
            if self.retriever is not None:
                self._build_lcel_chain()
            self.log.info("ConversationalRAG initialized successfully",session=self.session_id)

        except Exception as e:
            raise DocumentPoratalException(f"Error in initializing ConversationalRAG: {e}")
    def load_retriever_from_faiss(
        self,
        index_path: str,
        k: int = 5,
        index_name: str = "index",
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Load FAISS vectorstore from disk and build retriever + LCEL chain.
        """
        try:
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            embeddings = ModelLoader().load_embeddings()
            vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            if search_kwargs is None:
                search_kwargs = {"k": k}

            self.retriever = vectorstore.as_retriever(
                search_type=search_type, search_kwargs=search_kwargs
            )
            self._build_lcel_chain()

            self.log.info(
                "FAISS retriever loaded successfully",
                index_path=index_path,
                index_name=index_name,
                k=k,
                session_id=self.session_id,
            )
            #self._build_lcel_chain()
            return self.retriever
        except Exception as e:
            self.log.error(f"Error loading retriever from FAISS",error=str(e),session=self.session_id)
            raise DocumentPoratalException("Error loading retriever from FAISS", sys)
    def invoke(self, user_input: str, chat_history: Optional[List[BaseMessage]] = None) -> str:
        """Invoke the LCEL pipeline."""
        try:
            if self.chain is None:
                raise DocumentPoratalException(
                    "RAG chain not initialized. Call load_retriever_from_faiss() before invoke().", sys
                )
            chat_history = chat_history or []
            payload = {"input": user_input, "chat_history": chat_history or []}
            answer = self.chain.invoke(payload)
            if not answer:
                self.log.warning(
                    "No answer generated", user_input=user_input, session_id=self.session_id
                )
                return "No answer generated."
            
            self.log.info("Chain invoked successfully", session=self.session_id, user_input=user_input, answer_preview=str(answer)[:150])
            return answer
        except Exception as e:
            self.log.error(f"Error invoking ConversationalRAG", error=str(e), session=self.session_id)
            raise DocumentPoratalException("Error invoking ConversationalRAG", sys)
    def _load_llm(self):
        try:
            llm=ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM could not be loaded")
            self.log.info("LLM loaded successfully", session=self.session_id)
            return llm
        except Exception as e:
            self.log.error(f"Error loading LLM", error=str(e), session=self.session_id)
            raise DocumentPoratalException("Error loading LLM", sys)
        

    @staticmethod
    def _format_docs(docs) -> str:
        return "\n\n".join(getattr(d, "page_content", str(d)) for d in docs)
    

    def _build_lcel_chain(self):
        try:
            if self.retriever is None:
                raise DocumentPoratalException("No retriever set before building chain", sys)
            self.log.info("Before Building LCEL chain", session=self.session_id)
            question_retriver =(
                {"input": itemgetter("input"),"chat_history":itemgetter("chat_history")}
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )
            self.log.info("After question_retriver", session=self.session_id)
            retrieve_docs = question_retriver | self.retriever | self._format_docs
            self.chain = (
                {"context": retrieve_docs , "input": itemgetter("input"), "chat_history": itemgetter("chat_history")}
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )
            self.log.info("LCEL chain built successfully", session=self.session_id)
        except Exception as e:
            self.log.error(f"Error building LCEL chain", error=str(e), session=self.session_id)
            raise DocumentPoratalException("Error building LCEL chain", sys)
