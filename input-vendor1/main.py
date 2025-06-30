import pika
import os
import json
import time
import random

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "user")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "password")
QUEUE_NAME = "raw_data"

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)

print(f"input-vendor1 service started, connecting to RabbitMQ at {RABBITMQ_HOST}")

connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)

def generate_vendor1_data():
    return {
        "vendor": "vendor1",
        "device_id": f"dev-{random.randint(1000, 9999)}",
        "timestamp": int(time.time()),
        "signal_strength": random.randint(-100, -50),
        "status": random.choice(["active", "inactive"])
    }

try:
    while True:
        data = generate_vendor1_data()
        message = json.dumps(data)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # persistent
        )
        print(f"[x] Sent: {message}")
        time.sleep(5)
except KeyboardInterrupt:
    print("Shutting down input-vendor1 producer...")
finally:
    connection.close() 