import pika
import os
import json
import time
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# RabbitMQ config
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "user")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "password")
QUEUE_NAME = "raw_data"

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

# DB setup
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# RabbitMQ setup
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)

print(f"processor service started, connecting to RabbitMQ at {RABBITMQ_HOST} and PostgreSQL at {POSTGRES_HOST}")

def process_message(ch, method, properties, body):
    session = SessionLocal()
    try:
        data = json.loads(body)
        vendor = data.get("vendor")
        if vendor == "vendor1":
            normalized = NormalizedData(
                vendor=vendor,
                device_id=data.get("device_id"),
                timestamp=data.get("timestamp"),
                signal_strength=data.get("signal_strength"),
                status=data.get("status")
            )
        elif vendor == "vendor2":
            normalized = NormalizedData(
                vendor=vendor,
                device_id=data.get("id"),
                timestamp=data.get("ts"),
                signal_strength=data.get("metrics", {}).get("rssi"),
                status="active" if data.get("is_online") else "inactive"
            )
        else:
            print(f"[!] Unknown vendor: {vendor}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        session.add(normalized)
        session.commit()
        print(f"[x] Saved to DB: {data}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[!] Error processing message: {e}")
        session.rollback()
    finally:
        session.close()

def main():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message)
    print("[x] Waiting for messages. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Shutting down processor...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main() 