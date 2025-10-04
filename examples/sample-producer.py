# examples/sample-producer.py

import asyncio
import json
import random
import time
from aiokafka import AIOKafkaProducer


async def produce(num=200, patient_count=5):
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()

    try:
        for i in range(num):
            patient_id = f"patient-{random.randint(1, patient_count)}"
            device_id = f"device-{random.randint(1, 10)}"
            measurement = random.choice(["heart_rate", "spo2", "resp_rate"])

            if measurement == "heart_rate":
                value = random.gauss(75, 15)
            elif measurement == "spo2":
                value = random.gauss(98, 1)
            else:  # resp_rate
                value = random.gauss(16, 3)

            evt = {
                "id": f"evt-{int(time.time() * 1000)}-{i}",
                "patient_id": patient_id,
                "device_id": device_id,
                "timestamp": int(time.time()),
                "measurement": measurement,
                "value": float(round(value, 2)),
            }

            await producer.send_and_wait("events.raw", json.dumps(evt).encode("utf-8"))
            print(f"Produced: {evt}")

            await asyncio.sleep(0.1)  # simulate delay between events

    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(produce())
