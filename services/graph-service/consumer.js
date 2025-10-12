const { Kafka } = require("kafkajs");
const driver = require("./db");
const EventMessage = require("./models/EventMessage");

const kafka = new Kafka({
  clientId: "graph-service",
  brokers: [process.env.KAFKA_BROKER || "localhost:9092"]
});

const consumer = kafka.consumer({ groupId: "graph-service-group" });

async function saveEventToNeo4j(event) {
  const session = driver.session();
  try {
    const query = `
      MERGE (p:Patient {id: $patientId})
      MERGE (d:Device {id: $deviceId})
      CREATE (e:Event {
          timestamp: $timestamp,
          heartRate: $heartRate,
          oxygen: $oxygen,
          bloodPressure: $bloodPressure,
          anomalyScore: $anomalyScore,
          anomaly: $anomaly
      })
      MERGE (p)-[:HAS_EVENT]->(e)
      MERGE (d)-[:GENERATES_EVENT]->(e)
    `;
    await session.run(query, {
      patientId: event.patient_id,
      deviceId: event.device_id,
      timestamp: event.timestamp,
      heartRate: event.heart_rate,
      oxygen: event.oxygen,
      bloodPressure: event.blood_pressure,
      anomalyScore: event.inference.score,
      anomaly: event.inference.label === "anomaly"
    });
    console.log(`Stored event for patient ${event.patient_id}`);
  } catch (err) {
    console.error("Neo4j error:", err);
  } finally {
    await session.close();
  }
}

async function runConsumer() {
  await consumer.connect();
  await consumer.subscribe({ topic: process.env.KAFKA_TOPIC || "events.infer", fromBeginning: false });
  await consumer.run({
    eachMessage: async ({ message }) => {
      const event = new EventMessage(JSON.parse(message.value.toString()));
      await saveEventToNeo4j(event);
    }
  });
  console.log("Graph service Kafka consumer running...");
}

runConsumer().catch(console.error);
