# Smart Healthcare Event Intelligence Platform

## Overview
This project is a scalable backend system designed for real-time patient monitoring and anomaly detection. It ingests high-velocity healthcare event data from IoT devices and wearables, processes it using AI models, stores enriched data in a graph database, and exposes APIs for analytics and alerts.

## Features
- **Real-time Event Ingestion:** Patient vitals and sensor data streamed through Apache Kafka.
- **AI-Powered Anomaly Detection:** Neural network (CNN) microservice analyzes vitals to detect irregularities.
- **Knowledge Graph Storage:** Neo4j graph database models patients, devices, and events to capture relationships and timelines.
- **REST API & Dashboards:** FastAPI backend provides endpoints for querying patient histories and anomaly insights.
- **Real-time Alerts:** Critical patient states trigger notifications to clinicians via Kafka and WebSocket.
- **Scalable & Fault-Tolerant:** Containerized with Docker.
