import sys
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPoratalException
from datetime import datetime,timezone
import uuid


class DocumentIngestion:
    def __init__(self,base_dir:str="data\\document_compare",session_id=None):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path = self.base_dir/self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.log.info("DocumentIngestion initialized", base_dir=str(self.base_dir), session_id=self.session_id)
     

    def save_uploded_files(self,reference_file,actual_file):
        """Saves uploaded files to a specific directory"""
        try:
            #self.delete_existing_files()
            #self.log.info("Existing files deleted successfully")
            
            ref_path = self.session_path/reference_file.name
            act_path = self.session_path/actual_file.name

            if not reference_file.name.lower().endswith(".pdf") or not actual_file.name.lower().endswith(".pdf"):
                raise ValueError("Both files must be PDFs")
            
            with open(ref_path, "wb") as f:
                f.write(reference_file.getbuffer())

            with open(act_path, "wb") as f:
                f.write(actual_file.getbuffer())
            
            self.log.info("Files saved successfully", reference_file=str(reference_file.name), actual_file=str(actual_file.name),session=self.session_id)
            return ref_path, act_path
        except Exception as e:
            self.log.error(f"Error saving uploaded files",error=str(e),session=self.session_id)
            raise DocumentPoratalException("Error saving uploaded files", sys)
    def read_pdf(self,pdf_path:Path) -> str:
        """Reads a PDF file and extract text from each page"""
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError("PDF is encrypted and cannot be read : {pdf_path.name}")
                
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text() #type: ignore

                    if text.strip():
                        all_text.append(f"\n --- Page {page_num + 1} --- \n{text}")

                self.log.info("PDF read successfully",file=str(pdf_path),pages=len(all_text))
                return "\n".join(all_text)

                
        except Exception as e:
            self.log.error(f"Error reading PDF",error=str(e),session=self.session_id)
            raise DocumentPoratalException("Error reading PDF",sys)
        
    def combine_documents(self)->str:
        try:
            doc_parts=[]

            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix.lower() == ".pdf":
                    content = self.read_pdf(file) 
                    doc_parts.append(f"Document: {file.name}\n{content}")  

            combined_text = "\n\n".join(doc_parts)
            self.log.info("Document combined",count=len(doc_parts),session = self.session_id)
            return combined_text
        except Exception as e:
            self.log.error(f"Error combining documents",error=str(e),session = self.session_id)
            raise DocumentPoratalException("Error combining documents", sys)
    
    def clean_old_sessions(self,keep_latest: int=3):
        """
        Optional method to delete older session folders, keeping only the latest N.
        """
        try:
            session_folders = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()],
                reverse=True
            )
            for folder in session_folders[keep_latest:]:
                for file in folder.iterdir():
                    file.unlink()
                folder.rmdir()
                self.log.info(f"Old session folder deleted", folder=str(folder))

        except Exception as e:
            self.log.error(f"Error cleaning old sessions", error=str(e), session=self.session_id)
            raise DocumentPoratalException("Error cleaning old sessions", sys)
        

