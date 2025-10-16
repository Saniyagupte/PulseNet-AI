const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const cors = require("cors");
const patientRoutes = require("./routes/patientRoutes");

const app = express();
app.use(cors());
app.use(express.json());

app.use("/api/patients", patientRoutes);

const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*" }
});

io.on("connection", (socket) => {
  console.log("Dashboard connected:", socket.id);
});

// Expose io globally so Kafka consumer can emit events
global.io = io;

const PORT = process.env.PORT || 5005;
server.listen(PORT, () => console.log(`Graph API running on port ${PORT}`));
