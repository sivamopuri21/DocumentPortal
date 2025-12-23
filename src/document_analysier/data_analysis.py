import os
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPoratalException
from model.models import *
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
import sys
from prompt.prompt_library import PROMPT_REGISTRY

class DocumentAnalyzer:
    """
    Analyze documents usong a pre-trained model.
    Automatically logs all actions and supports session-based organization.
    """
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            #prepare parser 
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser,llm=self.llm)

            self.prompt = PROMPT_REGISTRY["document_analysis"]
            self.log.info("DocumentAnalyzer initialized successfully")
        except Exception as e:
            self.log.error(f"Error initializing DocumentAnalyzer: {e}")
            raise DocumentPoratalException("Error initializing DocumentAnalyzer",sys)
    def analyze_document(self,document_text:str)-> dict:
        """
        Analyzed a document text and extract structured metadata and summary
        """
        try:
            chain = self.prompt | self.llm | self.fixing_parser
            self.log.info("Metadata analysis chain initalized")

            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text":document_text}
                )
            self.log.info("Metadata analysis chain completed",keys=list(response.keys()))
            return response
        except Exception as e:
            self.log.error(f"Error analyzing document: {e}")
            raise DocumentPoratalException("Error analyzing document") from e


