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
            self.log = CustomLogger().get_logger(__name__)
            #base directories
            self.temp_dir = Path(temp_dir)
            self.faiss_dir = Path(faiss_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            #sessionalized parts
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
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
    def ingest_documents(self,uploaded_files):
        try:
            documents=[]
            for uploaded_file in uploaded_files:
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in self.SUPPORTED_FILE_TYPES:
                    self.log.warning("Unsupported file type", file=uploaded_file.name)
                    continue
                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
                temp_path = self.session_temp_dir / unique_filename
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                self.log.info("File saved for ingestion", filename=str(uploaded_file.name),saved_as = str(temp_path),session = self.session_id)
                if ext == ".pdf":
                    loader = PyPDFLoader(str(temp_path))
                elif ext == ".docx":
                    loader = Docx2txtLoader(str(temp_path))
                elif ext == ".txt":
                    loader = TextLoader(str(temp_path)) 
                else:
                    self.log.info("Unsupported file type encountered",filename = uploaded_file.name)
                    continue

                docs = loader.load()
                documents.extend(docs)

            if not documents:
                raise DocumentPoratalException("No documents found in the uploaded file", sys)
                
            self.log.info("All Documents loaded successfully", total_docs=len(documents), session=self.session_id)
            return self._create_retriver(documents)
                    
        except Exception as e:
            self.log.error("Failed to ingest file", error=str(e))
            raise DocumentPoratalException("Failed to ingest file in DocumentIngestor",sys)
    def _create_retriver(self,documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
            chunks = splitter.split_documents(documents)
            self.log.info("Documents split successfully", total_chunks=len(chunks), session=self.session_id)
            embeddings = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(chunks, embeddings)

            #save FAISS index under session folder
            vectorstore.save_local(str(self.session_faiss_dir))
            self.log.info("FAISS index saved to disk", path=str(self.session_faiss_dir), session=self.session_id)

            retriever = vectorstore.as_retriever(search_kwargs={"k": 3},search_type="similarity")
            self.log.info("Retriever created successfully", retriever_type=str(type(retriever)), session=self.session_id)
            return retriever
        
        except Exception as e:
            self.log.error("Failed to create retriver", error=str(e))
            raise DocumentPoratalException("Failed to create retriver in DocumentIngestor",sys)