<div align="center">

# 🛡️ EnergyShield-AI
**Autonomous Energy Supply Chain Resilience & Disruption Modeling**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_Database-blue.svg)](https://neo4j.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*A submission for the **ET AI Hackathon 2026** — Problem Statement 2: AI-Driven Energy Supply Chain Resilience.*

</div>

<hr/>

## 📖 Overview

In the modern geopolitical landscape, supply chain disruptions (from canal blockages to sanctions) can paralyze energy grids, causing massive domestic fuel price hikes and severe GDP drag. Wait times for manual analysis are too long—economies lacking integrated response intelligence take up to 47 days longer to stabilize.

**EnergyShield-AI** is an agentic AI architecture built to solve this. It fuses real-time global intelligence (GDELT, OFAC, PortWatch, EIA) with a **Geospatial Digital Twin** of the global energy supply chain. The platform continuously monitors chokepoints and suppliers, automatically triggering macroeconomic scenarios and synthesizing alternative procurement plans when thresholds are breached.

## ✨ Key Features

- **🌐 Live Ingestion Pipeline**: Autonomously scrapes and processes live geopolitical news (GDELT), sanctions data (OFAC), maritime choke-point activity (IMF PortWatch), and global commodity prices (EIA).
- **🕸️ Graph-Based Digital Twin**: Models the complex web of global trade (suppliers, shipping routes, choke points, refineries) using Neo4j to instantly trace the downstream exposure of any global event.
- **📉 Disruption Scenario Modeler**: Simulates the downstream impact of black-swan events (e.g., Strait of Hormuz closure). It calculates volumetric supply drops, shipping delays, and directly forecasts the macroeconomic ripple effects on **Domestic Fuel Prices** and **GDP**.
- **🤖 Agentic Procurement AI**: When a severe disruption is modeled or detected, an ensemble of AI agents automatically analyzes the digital twin to rank alternative suppliers, compute rerouting logistics, and recommend Strategic Petroleum Reserve (SPR) drawdowns.
- **💼 Analyst Command Center**: A premium, executive-level React dashboard that abstracts complex graph mathematics and AI orchestration into clean, actionable intelligence for policymakers and procurement officers.

## 🏗️ Architecture & Tech Stack

EnergyShield-AI is built on a scalable, modern microservices architecture designed to be completely commodity-agnostic (easily scaling beyond Crude Oil to LNG, Coal, and Critical Minerals).

* **Frontend**: React (Vite), Vanilla CSS (Premium Dark/Cream aesthetics), Recharts for data visualization.
* **Backend**: Python, FastAPI, Pydantic (Strict Schema Validation).
* **AI & Orchestration**: Agentic Ensemble Pattern, Event-driven architecture.
* **Database**: Neo4j (Knowledge Graph / Supply Chain Mapping).

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Neo4j Desktop or Neo4j AuraDB instance

### 1. Database (Neo4j) Setup
Start your Neo4j instance and note your connection URI (e.g., `bolt://localhost:7687`), username, and password.

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Neo4j credentials and LLM API keys

# Seed the Digital Twin Knowledge Graph
python scripts/seed_graph.py

# Start the FastAPI Server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

### 4. Access the Platform
Navigate to `http://localhost:5173` in your browser to access the Analyst Command Center.

## 🎯 Hackathon Deliverables Alignment

This repository directly fulfills the "What You May Build" suggestions from the ET Hackathon prompt:
- ✅ **Real-Time Data Ingestion** (GDELT, OFAC, PortWatch, EIA)
- ✅ **Risk Identification & Forecasting** (Automated event extraction and scoring)
- ✅ **Scenario Modeler** (Calculates cascading effects: supply, delay, freight cost, fuel price, GDP)
- ✅ **Actionable Recommendations** (AI-ranked alternative suppliers and SPR plans)

## 👥 Team Ownership

| Role                                          | Person             | Core Responsibility                                                                     |
| --------------------------------------------- | ------------------ | --------------------------------------------------------------------------------------- |
| Frontend and Backend Lead                     | Ayush Kumar        | Frontend dashboard, backend APIs, database integration, report generation, deployment   |
| ML and Agents Lead                            | Abhishek Choudhary | Event extraction, risk scoring, scenario modelling, continuous learning, explainability |
| Data, Orchestration, and Knowledge Graph Lead | Mayur Raj          | Data ingestion, schedulers, orchestration, knowledge graph, procurement orchestration   |

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
