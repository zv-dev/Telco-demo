from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# PostgreSQL config
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "telco_db")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "telco")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "telco_pass")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

Base = declarative_base()

class NormalizedData(Base):
    __tablename__ = "normalized_data"
    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(BigInteger)
    signal_strength = Column(Integer)
    status = Column(String)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/data")
def get_data(db: Session = Depends(get_db)):
    records = db.query(NormalizedData).all()
    return [
        {
            "id": r.id,
            "vendor": r.vendor,
            "device_id": r.device_id,
            "timestamp": r.timestamp,
            "signal_strength": r.signal_strength,
            "status": r.status
        }
        for r in records
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 