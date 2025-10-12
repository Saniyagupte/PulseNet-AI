class EventMessage {
  constructor({ patient_id, device_id, timestamp, heart_rate, oxygen, blood_pressure, inference }) {
    this.patient_id = patient_id;
    this.device_id = device_id || "unknown";
    this.timestamp = timestamp;
    this.heart_rate = heart_rate;
    this.oxygen = oxygen;
    this.blood_pressure = blood_pressure;
    this.inference = inference || { label: "normal", score: 0 };
  }
}

module.exports = EventMessage;
