# services/inference-service/app/main.py

import os
import asyncio
import json
import logging
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inference")

# Kafka configuration
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
RAW_TOPIC = os.getenv("RAW_TOPIC", "events.raw")
INFER_TOPIC = os.getenv("INFER_TOPIC", "events.infer")
GROUP_ID = os.getenv("GROUP_ID", "inference-group")

# FastAPI app
app = FastAPI()


async def dummy_predict(event: dict) -> dict:
    """
    Simple placeholder for model inference.
    Replace this with a real model call (PyTorch/TensorFlow/ONNX/Triton) later.
    """
    value = float(event.get("value", 0))
    measurement = event.get("measurement", "")

    if measurement == "heart_rate":
        if value > 120:
            label = "tachycardia"
        elif value < 50:
            label = "bradycardia"
        else:
            label = "normal"
        score = min(max((value - 50) / 100, 0), 1)
    else:
        label = "anomaly" if value > 0.9 else "normal"
        score = value

    return {"label": label, "score": score}


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
                infer = await dummy_predict(event)
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
