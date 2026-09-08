import logging
import geopandas as gpd

logger = logging.getLogger(__name__)

def fetch_sst_data(bbox: tuple = None) -> gpd.GeoDataFrame:
    """
    Fetches Sea Surface Temperature (SST) from MOSDAC (INSAT-3D / Oceansat-3).
    """
    logger.info("Fetching SST data from MOSDAC...")
    return gpd.GeoDataFrame(
        columns=['source', 'temp_c', 'timestamp', 'geometry'],
        geometry='geometry',
        crs="EPSG:4326"
    )

def fetch_aws_stations() -> gpd.GeoDataFrame:
    """
    Fetches Automatic Weather Station (AWS) telemetry.
    """
    logger.info("Fetching AWS station data from MOSDAC...")
    return gpd.GeoDataFrame(
        columns=['station_id', 'source', 'wind_speed_kmh', 'wave_height_m', 'timestamp', 'geometry'],
        geometry='geometry',
        crs="EPSG:4326"
    )
