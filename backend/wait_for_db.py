import psycopg2
import time
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_db():
    retries = 30  # Number of retries
    while retries > 0:
        try:
            conn = psycopg2.connect(
                dbname="resume_builder",
                user="resume",
                password="postgres",
                host="db",
                port="5432"
            )
            conn.close()
            logger.info("Database is ready!")
            return True
        except psycopg2.OperationalError as e:
            retries -= 1
            if retries == 0:
                logger.error(f"Could not connect to database: {e}")
                return False
            logger.warning(f"Database not ready, waiting... ({retries} attempts left)")
            time.sleep(2)

if __name__ == "__main__":
    if not wait_for_db():
        sys.exit(1)
