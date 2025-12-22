import logging
import os
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self,log_dir="logs"):
        #ensure log directiry exists
        self.log_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        
        #create log file name based on current date and time
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.log_dir, log_file)
        # #basic logging
        # logging.basicConfig(
        #     filename=log_file_path,
        #     format="[ %(asctime)s ] %(levelname)s %(name)s (line: %(lineno)d) - %(message)s",
        #     level=logging.INFO,
        # )
        
    def get_logger(self,name=__file__):
        logger_name = os.path.basename(name)

        #configure logging for console _file (bith JSON)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[console_handler,file_handler]
        )

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso",utc=True,key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True
        )
        return structlog.get_logger(logger_name)
    

if __name__ == "__main__":
    logger=CustomLogger()
    logger=logger.get_logger(__file__)
    logger.info("User uploded a pdf",user_id="123",file_name="report.pdf")
    logger.error("Failed to process the PDF",error="File Not Found",user_id="123")
    #logger.info("Custom logger intiated")
