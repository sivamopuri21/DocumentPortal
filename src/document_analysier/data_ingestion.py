import os
import fitz
import uuid
from datetime import datetime
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPoratalException
import sys

class DocumentHandler:
    """
    Handles PDF saving and readingf operations.
    Automatically logs all actions and supports session-based organization.    
    """
    def __init__(self,data_dir=None,session_id=None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = data_dir or os.getenv("DATA_STORAGE_PATH",os.path.join(os.getcwd(),"data","document_analysis"))
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            #create base session directory
            self.session_path = os.path.join(self.data_dir, self.session_id)
            os.makedirs(self.session_path, exist_ok=True)
            self.log.info("PDFHandler initalized",session_id=self.session_id,session_path=self.session_path)
        except Exception as e:
            self.log.info(f"Error initalizing DocumentHandler: {e}")
            raise DocumentPoratalException("Error initalizing DocumentHandler",e) from e

    def save_pdf(self,pdf_data):
        try:
            pdf_path = os.path.join(self.data_dir, f"{self.session_id}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_data)
            self.log.info(f"PDF saved successfully: {pdf_path}")
        except Exception as e:
            self.log.error(f"Error saving PDF: {e}")

    def read_pdf(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error reading PDF: {e}")

if __name__ == "__main__":
    handler = DocumentHandler()