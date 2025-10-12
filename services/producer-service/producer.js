// producer.js
import { Kafka } from 'kafkajs';

const kafka = new Kafka({
  clientId: 'producer-service',
  brokers: ['localhost:9092'],
});

const producer = kafka.producer();

function getRandomGaussian(mean, stddev) {
  let u = 0, v = 0;
  while(u === 0) u = Math.random();
  while(v === 0) v = Math.random();
  let num = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  return num * stddev + mean;
}

async function produce(num = 200, patientCount = 5) {
  await producer.connect();

  try {
    for (let i = 0; i < num; i++) {
      const patient_id = `patient-${Math.floor(Math.random() * patientCount) + 1}`;
      const device_id = `device-${Math.floor(Math.random() * 10) + 1}`;
      const measurementTypes = ["heart_rate", "spo2", "resp_rate"];
      const measurement = measurementTypes[Math.floor(Math.random() * measurementTypes.length)];

      let value;
      if (measurement === "heart_rate") {
        value = getRandomGaussian(75, 15);
      } else if (measurement === "spo2") {
        value = getRandomGaussian(98, 1);
      } else {
        value = getRandomGaussian(16, 3);
      }

      const evt = {
        id: `evt-${Date.now()}-${i}`,
        patient_id,
        device_id,
        timestamp: Math.floor(Date.now() / 1000),
        measurement,
        value: parseFloat(value.toFixed(2)),
      };

      await producer.send({
        topic: 'events.raw',
        messages: [
          { value: JSON.stringify(evt) }
        ],
      });

      console.log(`Produced: ${JSON.stringify(evt)}`);

      await new Promise(resolve => setTimeout(resolve, 100));
    }
  } finally {
    await producer.disconnect();
  }
}

produce().catch(console.error);
