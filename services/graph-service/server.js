const express = require("express");
const bodyParser = require("body-parser");
const driver = require("./db");

const app = express();
app.use(bodyParser.json());

app.get("/patients/:id/events", async (req, res) => {
  const session = driver.session();
  try {
    const result = await session.run(
      `MATCH (p:Patient {id: $id})-[:HAS_EVENT]->(e:Event)
       RETURN e ORDER BY e.timestamp`,
      { id: req.params.id }
    );
    const events = result.records.map(r => r.get("e").properties);
    res.json(events);
  } catch (err) {
    res.status(500).json({ error: err.message });
  } finally {
    await session.close();
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Graph service running on port ${PORT}`));
