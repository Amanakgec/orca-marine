import os
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..data import mock_isro_seed
# from ..models_db import SSTReading, PFZZone

router = APIRouter(prefix="/api/ocean", tags=["Ocean ISRO Data"])

@router.get("/sst")
def get_sst(
    bbox: str = Query(None, description="Bounding box in format min_lon,min_lat,max_lon,max_lat"),
    db: Session = Depends(get_db)
):
    """
    Returns Sea Surface Temperature points within a bounding box.
    """
    mode = os.getenv("ORCA_DATA_MODE", "mock").lower()
    
    if mode == "mock":
        return mock_isro_seed.get_mock_sst(bbox=bbox)
    
    # Real DB query logic goes here:
    # return db.query(SSTReading).filter(...).all()
    raise HTTPException(status_code=501, detail="Real DB mode not fully wired in current demo.")

@router.get("/pfz")
def get_pfz(
    bbox: str = Query(None, description="Bounding box in format min_lon,min_lat,max_lon,max_lat"),
    db: Session = Depends(get_db)
):
    """
    Returns Potential Fishing Zones (Polygons) within a bounding box.
    """
    mode = os.getenv("ORCA_DATA_MODE", "mock").lower()
    
    if mode == "mock":
        return mock_isro_seed.get_mock_pfz(bbox=bbox)
        
    raise HTTPException(status_code=501, detail="Real DB mode not fully wired in current demo.")
