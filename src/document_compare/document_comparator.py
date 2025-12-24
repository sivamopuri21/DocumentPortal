import sys
from dotenv import load_dotenv  
import pandas as pd
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPoratalException
from model.models import SummaryResponse, PromptType
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
        self.prompt = PROMPT_REGISTRY[PromptType.DOCUMENT_COMPARISON.value]
        self.chain = self.prompt | self.llm | self.fixing_parser
        self.log.info("DocumentComparatorLLM initialized wih model and parser.")


    def compare_documents(self,combined_docs: str) -> pd.DataFrame:
        """
        Compares two documents and returns a structured comparison.
        """
        try:
            inputs ={
                "combined_docs":combined_docs,
                "format_instructions":self.parser.get_format_instructions()
            }
            self.log.info("Starting document comparision",inputs=inputs)
            response = self.chain.invoke(inputs)
            self.log.info("Chain invoked successfully", response_preview=(response)[:200])
            return self._format_response(response)
        
        except Exception as e:
            self.log.error(f"Error during document comparison",error=str(e))
            raise DocumentPoratalException("Error during document comparison",sys)
    def _format_response(self,response_parsed: list[dict]) -> pd.DataFrame:
        """
        Format the response from the LLM into a structured format.
        """
        try:
            df = pd.DataFrame(response_parsed)
            self.log.info("Response formatted into DataFrame", df_shape=df.shape)
            return df
        except Exception as e:
            self.log.error(f"Error fomratting response into Dataframe: {e}")
            raise DocumentPoratalException("Error fomratting response into Dataframe",sys)
