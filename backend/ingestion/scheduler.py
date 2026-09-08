import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from .isro import bhuvan, mosdac

logger = logging.getLogger(__name__)

def ingest_pfz_job():
    try:
        logger.info("Starting scheduled PFZ ingestion...")
        gdf = bhuvan.fetch_pfz_data()
        logger.info(f"Ingested {len(gdf.get('features', []))} PFZ records.")
    except Exception as e:
        logger.error(f"Failed to ingest PFZ data: {e}")

def ingest_sst_job():
    try:
        logger.info("Starting scheduled SST ingestion...")
        gdf = mosdac.fetch_sst_data()
        logger.info(f"Ingested {len(gdf.get('features', []))} SST records.")
    except Exception as e:
        logger.error(f"Failed to ingest SST data: {e}")

def start_scheduler():
    # Only run scheduler if not in mock mode, to avoid spamming actual DB during dev/mock runs
    if os.getenv("ORCA_DATA_MODE", "").lower() == "mock":
        logger.info("ORCA_DATA_MODE=mock, bypassing background ISRO ingestion scheduler.")
        return None

    scheduler = BackgroundScheduler()
    
    # Run PFZ ingest daily at 02:00
    scheduler.add_job(ingest_pfz_job, 'cron', hour=2, minute=0)
    # Run SST ingest every 6 hours
    scheduler.add_job(ingest_sst_job, 'interval', hours=6)
    
    scheduler.start()
    logger.info("ISRO Data Ingestion Scheduler started.")
    return scheduler
