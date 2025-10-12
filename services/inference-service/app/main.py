# services/inference-service/app/main.py

import os
import asyncio
import json
import logging
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from .inference import predict as model_predict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inference")

# Kafka configuration
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
RAW_TOPIC = os.getenv("RAW_TOPIC", "events.raw")
INFER_TOPIC = os.getenv("INFER_TOPIC", "events.infer")
GROUP_ID = os.getenv("GROUP_ID", "inference-group")

# FastAPI app
app = FastAPI()


async def run_consumer_loop():
    consumer = AIOKafkaConsumer(
        RAW_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID
    )
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)

    await consumer.start()
    await producer.start()
    logger.info(f"Inference consumer started (bootstrap={KAFKA_BOOTSTRAP})")

    try:
        async for msg in consumer:
            try:
                event = json.loads(msg.value.decode())
                # Map incoming fields to vitals dict for CNN
                vitals = {
                    "heart_rate": event.get("heart_rate", 80),
                    "oxygen": event.get("spo2", 98),
                    "blood_pressure": event.get("blood_pressure", 120)
                }
                infer = model_predict(vitals)  # CNN inference
                enriched = {**event, "inference": infer}
                await producer.send_and_wait(INFER_TOPIC, json.dumps(enriched).encode())
                logger.info(f"Processed event id={event.get('id')} label={infer.get('label')}")
            except Exception:
                logger.exception("Failed to process event")
    finally:
        await consumer.stop()
        await producer.stop()


@app.on_event("startup")
async def startup():
    asyncio.create_task(run_consumer_loop())


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
