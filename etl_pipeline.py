import logging
from datetime import datetime, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from extract import extract_crypto_data
from transform import transform_crypto_data
from load import load_crypto_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_etl():
    logger.info("ETL Pipeline started...")
    try:
        logger.info("Extracting data...")
        raw_data = extract_crypto_data()

        logger.info("Transforming data...")
        records = transform_crypto_data(raw_data)

        logger.info("Loading data...")
        load_crypto_data(records)

        logger.info(f"ETL completed successfully at {datetime.now(timezone.utc)}")

    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}")

if __name__ == "__main__":
    logger.info("Starting ETL Scheduler, runs every 5 minutes...")
    run_etl()

    scheduler = BlockingScheduler()
    scheduler.add_job(run_etl, "interval", minutes=5)
    scheduler.start()
