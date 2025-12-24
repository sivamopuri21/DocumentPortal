import uuid
from pathlib import Path
from datetime import datetime, timezone
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPoratalException
from utils.model_loader import ModelLoader
import sys

class DocumentIngestor:
    SUPPORTED_FILE_TYPES = {".pdf", ".docx", ".txt",".md"}
    def __init__(self,temp_dir:str ="data/multi_doc_chat",faiss_dir:str="faiss_index",session_id:str | None=None):
        try:
            #base directories
            self.temp_dir = Path(temp_dir)
            self.faiss_dir = Path(faiss_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            #sessionalized parts
            self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[:8]}"
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_faiss_dir = self.faiss_dir / self.session_id
            self.session_temp_dir.mkdir(parents=True, exist_ok=True)
            self.session_faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.log.info(
                "DocumentIngestor initialized", 
                session=self.session_id,
                temp_dir=str(self.session_temp_dir),
                faiss_dir=str(self.session_faiss_dir),
                temp_base = str(self.temp_dir),
                faiss_base = str(self.faiss_dir)
            )

        except Exception as e:
            self.log.error("Failed to intialie DocumentIngestor",error=str(e))
            raise DocumentPoratalException("INitalization error in DocumentIngestor",sys)
    def ingest_file(self):
        try:
            pass
        except Exception as e:
            self.log.error("Failed to ingest file", error=str(e))
            raise DocumentPoratalException("Failed to ingest file in DocumentIngestor",sys)
    def _create_retriver(self,documents):
        try:
            pass
        except Exception as e:
            self.log.error("Failed to create retriver", error=str(e))
            raise DocumentPoratalException("Failed to create retriver in DocumentIngestor",sys)