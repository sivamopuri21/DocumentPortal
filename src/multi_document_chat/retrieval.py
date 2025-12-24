import os
import sys
from operator import itemgetter
from typing import List, Optional
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
    def __init__(self,session_id:str, retriver=None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.llm = self._load_llm()
            self.conttextualize_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_PROMPT.value]
            self.qa_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.QA_PROMPT.value]
            if retriver is None:
                raise ValueError("Retriver cannot be None")
            self.retriver = retriver
            self._build_lcel_chain()
            self.log.info("ConversationalRAG initialized successfully",session=self.session_id)

        except Exception as e:
            raise DocumentPoratalException(f"Error in initializing ConversationalRAG: {e}")
    def load_retriver_from_faiss(self,index_path: str):
        """
        Load a FAISS vectorstore from disk and convert to retriver.
        """
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            vectorstore = FAISS.load_local(index_path, embeddings,allow_dangerous_deserialization=True)
            self.retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self.log.info("Retriver loaded successfully from FAISS", session=self.session_id)
            self._build_lcel_chain()
            return self.retriever
        except Exception as e:
            self.log.error(f"Error loading retriever from FAISS",error=str(e),session=self.session_id)
            raise DocumentPoratalException("Error loading retriever from FAISS", sys)
    def invoke(self,user_input:str, chat_history:Optional[List[BaseMessage]]=None)-> str:
        """
        Args:
            user_input (str): _description_
            chat_history (Optional[List[BaseMessage]],optional]): _description_. Defaults to None.
        """
        try:
            chat_history = chat_history or []
            payload = {"input": user_input, "chat_history": chat_history or []}
            answer = self.chain.invoke(payload)
            if not answer:
                self.log.warning("Empty answer received", session=self.session_id,user_input=user_input)
                return "No answer generated."
            
            self.log.info("Chain invoked successfully", session=self.session_id, user_input=user_input, answer_preview=answer[:150])
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
    def _format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])
    def _build_lcel_chain(self):
        try:
            question_retriver =(
                {"input": itemgetter("input"),"chat_history":itemgetter("chat_history")}
                |self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )
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
