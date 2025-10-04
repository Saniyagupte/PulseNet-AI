# services/graph-service/app/main.py

import asyncio
import json
import logging

from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
INFERENCE_TOPIC = "inference-events"
ALERT_TOPIC = "alerts"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test"

# Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# FastAPI app
app = FastAPI()


async def run_consumer_loop():
    consumer = AIOKafkaConsumer(
        INFERENCE_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="graph-service",
        enable_auto_commit=True,
        auto_offset_reset="latest",
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    )

    await consumer.start()
    await producer.start()

    try:
        async for msg in consumer:
            try:
                event = json.loads(msg.value)
                logger.info(f"Received event: {event}")

                with driver.session() as session:
                    session.run(
                        """
                        MERGE (e:Event {id:$id})
                        SET e.timestamp = $ts, e.measurement=$measurement, e.value=$value, e.inference = $inference
                        WITH e
                        MATCH (p:Patient {id:$patient_id})
                        MERGE (p)-[:HAS_EVENT]->(e)
                        """,
                        id=event.get("id"),
                        ts=event.get("timestamp"),
                        measurement=event.get("measurement"),
                        value=event.get("value"),
                        inference=json.dumps(event.get("inference")),
                        patient_id=event.get("patient_id", "unknown"),
                    )

                # If inference suggests something other than 'normal', publish an alert
                inf = event.get("inference", {})
                label = inf.get("label", "")
                score = inf.get("score", 0)

                if label and label != "normal":
                    alert = {
                        "id": event.get("id"),
                        "patient_id": event.get("patient_id"),
                        "label": label,
                        "score": score,
                        "timestamp": event.get("timestamp"),
                    }
                    await producer.send_and_wait(ALERT_TOPIC, json.dumps(alert).encode())
                    logger.info(f"Published alert: {alert}")

            except Exception:
                logger.exception("Failed to process inference event")

    finally:
        await consumer.stop()
        await producer.stop()


@app.on_event("startup")
async def startup():
    asyncio.create_task(run_consumer_loop())


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/patient_events/{patient_id}")
def patient_events(patient_id: str, limit: int = 50):
    with driver.session() as session:
        q = """
        MATCH (p:Patient {id:$patient_id})-[:HAS_EVENT]->(e:Event)
        RETURN properties(e) AS e
        ORDER BY e.timestamp DESC LIMIT $limit
        """
        res = session.run(q, patient_id=patient_id, limit=limit)
        return [r["e"] for r in res]


@app.post("/query")
def run_cypher(payload: dict):
    # WARNING: this executes arbitrary Cypher. Add auth & validation in production.
    cypher = payload.get("cypher")
    params = payload.get("params", {})

    if not cypher:
        raise HTTPException(status_code=400, detail="cypher required")

    with driver.session() as session:
        res = session.run(cypher, **params)
        return [r.data() for r in res]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002)
