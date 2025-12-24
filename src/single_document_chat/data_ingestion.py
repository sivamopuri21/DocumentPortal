import uuid
from pathlib import Path
import sys
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPoratalException
from utils.model_loader import ModelLoader
from datetime import datetime

class SingleDocIngestor:
    def __init__(self,data_dir: str="data/single_document_chat",faiss_dir:str="faiss_index"):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)

            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.log.info("SingleDocIngestor initialized successfully",temp_path=str(self.data_dir), faiss_dir = str(self.faiss_dir))

        except Exception as e:
            self.log.error(f"Error initializing SingleDocIngestor",error=str(e))
            raise DocumentPoratalException("Error initializing SingleDocIngestor",sys)
        
    def ingest_files(self,uploaded_files):
        try:
            documents=[]
            for uploaded_file in uploaded_files:
                unique_filename = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = self.data_dir / unique_filename
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                self.log.info(f"PDF saved for ingestion", file=uploaded_file.name)
                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)
            self.log.info("PDF files loaded",count=len(documents))
            return self._create_retriver(documents)
                
        except Exception as e:
            self.log.error(f"Error ingesting files", error=str(e))
            raise DocumentPoratalException("Error ingesting files", sys)

    def _create_retriver(self,documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
            chunks = splitter.split_documents(documents)
            self.log.info("Documents split into chunks", count=len(chunks))

            embeddings = self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(chunks, embeddings)

            vectorstore.save_local(str(self.faiss_dir))
            self.log.info("Vectorstore created and saved", faiss_dir=str(self.faiss_dir))
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3},search_type="similarity")
            self.log.info("Retriever created successfully", retriever_type=str(type(retriever)))
            return retriever
        
        except Exception as e:
            self.log.error(f"Error creating retriever", error=str(e))
            raise DocumentPoratalException("Error creating retriever", sys)
