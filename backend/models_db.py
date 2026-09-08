from sqlalchemy import Column, Integer, String, Float, DateTime
from geoalchemy2 import Geometry
from .database import Base

class SSTReading(Base):
    __tablename__ = "sst_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True) # e.g., 'mosdac_insat3d'
    temp_c = Column(Float)
    timestamp = Column(DateTime, index=True)
    geom = Column(Geometry('POINT', srid=4326))

class ChlorophyllReading(Base):
    __tablename__ = "chlorophyll_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True) # e.g., 'bhuvan_ocm3'
    concentration_mg_m3 = Column(Float)
    timestamp = Column(DateTime, index=True)
    geom = Column(Geometry('POINT', srid=4326))

class PFZZone(Base):
    __tablename__ = "pfz_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True) # e.g., 'bhuvan'
    confidence_score = Column(Float)
    timestamp = Column(DateTime, index=True)
    geom = Column(Geometry('POLYGON', srid=4326))

class WeatherStation(Base):
    __tablename__ = "weather_stations"
    
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, unique=True, index=True)
    source = Column(String, index=True) # e.g., 'mosdac_aws'
    wind_speed_kmh = Column(Float, nullable=True)
    wave_height_m = Column(Float, nullable=True)
    timestamp = Column(DateTime, index=True)
    geom = Column(Geometry('POINT', srid=4326))
