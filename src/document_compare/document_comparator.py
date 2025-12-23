import sys
from dotenv import load_dotenv  
import pandas as pd
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPoratalException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

class DocumentComparatorLLM:
    def __init__(self):
        load_dotenv()
        self.log = CustomLogger().get_logger(__name__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser,llm=self.llm)
        self.prompt = PROMPT_REGISTRY["document_comparison"]
        self.chain = self.prompt | self.llm | self.fixing_parser
        self.log.info("DocumentComparatorLLM initialized wih model and parser.")


    def compare_documents(self):
        """
        Compares two documents and returns a structured comparison.
        """
        try:
            pass
        except Exception as e:
            self.log.error(f"Error during document comparison: {e}")
            raise DocumentPoratalException("Error during document comparison",sys)
    def _format_response(self):
        """
        Format the response from the LLM into a structured format.
        """
        try:
            pass
        except Exception as e:
            self.log.error(f"Error fomratting response into Dataframe: {e}")
            raise DocumentPoratalException("Error fomratting response into Dataframe",sys)
