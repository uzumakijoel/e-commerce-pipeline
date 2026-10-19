from sql import sql
import os
from dotenv import load_dotenv
import logging
import logger


log= logging.getLogger(__name__)

load_dotenv()
#The result display
log.info("Start of the pipeline")
print(sql(
    os.getenv("DB_NAME"),
    os.getenv("DB_HOST"),
    os.getenv("DB_USER"),
    os.getenv("DB_PASSWORD")
))
log.info("End of the pipeline")


