import sys
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPoratalException

class DocumentComparator:
    def __init__(self,base_dir):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)


    def delete_existing_files(self):
        """Deletes existing files at the specific location """
        try:
            pass
        except Exception as e:
            self.log.error(f"Error deleting existing files: {e}")
            raise DocumentPoratalException("Error deleting existing files", sys)
        

    def save_uploded_files(self):
        """Saves uploaded files to a specific directory"""
        try:
            pass
        except Exception as e:
            self.log.error(f"Error saving uploaded files: {e}")
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
            self.log.error(f"Error reading PDF: {e}")
            raise DocumentPoratalException("Error reading PDF",sys)
