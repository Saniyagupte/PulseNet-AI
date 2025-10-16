const express = require("express");
const router = express.Router();
const driver = require("../db");

// 🩺 Query: Get all events for a given patient
router.get("/:id/events", async (req, res) => {
  const session = driver.session();
  try {
    const result = await session.run(
      `MATCH (p:Patient {id: $id})-[:HAS_EVENT]->(e:Event)
       RETURN e ORDER BY e.timestamp DESC`,
      { id: req.params.id }
    );
    const events = result.records.map(r => r.get("e").properties);
    res.json(events);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Neo4j query failed" });
  } finally {
    await session.close();
  }
});

// 🧠 Query: Find patients with repeated anomalies
router.get("/anomalies/repeated", async (req, res) => {
  const session = driver.session();
  try {
    const result = await session.run(`
      MATCH (p:Patient)-[:HAS_EVENT]->(e:Event)
      WHERE e.anomaly = true
      WITH p, COUNT(e) AS anomalyCount
      WHERE anomalyCount > 2
      RETURN p.id AS patientId, anomalyCount
    `);
    res.json(result.records.map(r => r.toObject()));
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Query failed" });
  } finally {
    await session.close();
  }
});

module.exports = router;
