# 🤖 Adaptive Logistics Agent: A Multi-Agent AI for Fleet Optimization

This project is a high-fidelity simulation of an adaptive, AI-driven logistics system. It moves beyond simple LLM chatbots to build a robust **multi-agent system** that can manage a fleet of delivery drivers in a dynamic, real-world environment.

The system features a central **"Dispatcher" AI Agent** that uses a large language model (LLM) for high-level reasoning. It delegates complex mathematical optimization to a dedicated solver and manages a team of "Driver" agents to execute deliveries, all while adapting to real-time events like new orders and traffic.

## 🎯 The Problem: Why a Simple LLM Fails

Last-mile delivery is a famously complex "Vehicle Routing Problem" (VRP). A standalone LLM (like ChatGPT or Gemini) **cannot** solve this problem effectively because it:

1.  **Cannot Solve Complex Math:** LLMs are terrible at solving the combinatorial optimization required for VRP. They can *talk* about a route, but they can't mathematically *prove* it's the optimal one.
2.  **Is Not State-Aware:** The real world is dynamic. An LLM has no access to real-time traffic, a driver's live location, or a new high-priority order that just came in.
3.  **Cannot Execute or Adapt:** An LLM's output is static text. It cannot dispatch routes, monitor progress, or re-route a driver when an unexpected event occurs.

This project solves these issues by using an **agentic architecture**, where the LLM is the "brain" in a system of specialized tools and executors.

## ✨ Core Features

* **Multi-Agent System:** A central **Dispatcher Agent** plans and coordinates multiple programmatic **Driver Agents**.
* **Hybrid AI Model:** Combines the reasoning and planning power of an LLM (via **CrewAI**) with the mathematical precision of a dedicated solver (**Google OR-Tools**).
* **Dynamic Re-routing:** The Dispatcher agent can perceive changes in the environment (like new orders) and re-plan routes for its drivers on the fly.
* **Real-World Routing:** Uses the **Open Source Routing Machine (OSRM)** running in a Docker container, providing hyper-fast, realistic travel-time calculations based on OpenStreetMap data (100% free and offline).
* **Dynamic Simulation:** A Python-based environment simulates time, generates new orders, and manages the state of all packages and drivers.
* **Interactive Dashboard (Optional):** A **Streamlit** interface to visualize driver locations, package statuses, and the agent's decisions in real-time.

## 🏗️ System Architecture

The system is built on a "Dispatcher-Solver-Executor" model:

1.  **Environment Simulator:** The "game loop" that holds the state of the world (drivers, packages, time) and introduces new events.
2.  **Dispatcher Agent (The Brain):** A CrewAI agent that perceives the environment. Its goal is to deliver all packages efficiently. It uses tools to achieve this.
3.  **Tools (The Agent's "Hands"):**
    * **`RoutingEngine` (OSRM):** A tool that connects to the local OSRM server to get a real-time distance/duration matrix between any set of points.
    * **`RouteOptimizer` (OR-Tools):** A tool that takes the distance matrix and solves the complex VRP, returning a mathematically optimal route.
4.  **Driver Agents (The Executors):** Simple programmatic agents that receive a route from the Dispatcher and execute it within the simulation, updating their status as they go.



## 🔧 Tech Stack

* **AI Agent Framework:** **CrewAI** (or LangChain)
* **LLM:** **Google Gemini** (or any other API-based LLM)
* **Routing Engine:** **OSRM (Open Source Routing Machine)**
* **Containerization:** **Docker**
* **Optimization Solver:** **Google OR-Tools**
* **Simulation & Core Logic:** **Python 3.10+**
* **Data Validation:** **Pydantic**
* **API/Tool Communication:** **Requests**
* **Dashboard:** **Streamlit** (Optional)

## 🚀 Setup & Installation Guide

Follow these steps precisely to get the project running.

### 1. Prerequisites

* **Python 3.10+**
* **Docker Desktop:** Must be installed and running.
* **Git**

### 2. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/logistics_agent.git](https://github.com/YOUR_USERNAME/logistics_agent.git)
cd logistics_agent
```

### 3. Set Up the Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On MacOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install all required Python packages
pip install -r requirements.txt
```

### 4. Set Up the OSRM Routing Server (The Hard Part)

This is a one-time setup that creates your local, offline-first routing API.

**A. Download Map Data:**

1. Go to <a href="http://download.geofabrik.de/asia/india.html">GeoFabrik Download Server</a>.

2. Download the `maharashtra-latest.osm.pbf` file.

3. Create a folder named `osrm_data` in your project's root directory.

4. Move the downloaded file into `osrm_data`.

**B. Process the Map Data with Docker: (This will take a few minutes)**

```bash
# Make sure Docker Desktop is running!
# Use `pwd` (Mac/Linux) or `cd` (Windows) to get the full absolute path
# to your osrm_data folder.

# 1. Extract the road network
docker run -t -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/maharashtra-latest.osm.pbf

# 2. Build the routing hierarchy
docker run -t -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-contract /data/maharashtra-latest.osrm
```

You should now have several new .osrm files inside your osrm_data folder.

**C. Run the OSRM Server: Run this command in a new, separate terminal window. You must leave this terminal open.**

```bash
docker run -d -p 5000:5000 -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/maharashtra-latest.osrm
```

Test it! Open your browser and go to http://localhost:5000. You should see a "Service is running" message.

### 5. Set Up API Keys
1. Find the `.env.example` file in the repository and rename it to `.env`.

2. Open the `.env` file and add your LLM API key:

```toml
# .env
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

## 🏃‍♂️ How to Run the Simulation

You are now ready to run the project.

1. Ensure OSRM is running: Make sure the Docker container you started in step 4-C is still running in its terminal.

2. Activate your Python environment:

```bash
source venv/bin/activate
```

3. Run the main simulation:

```bash
python main.py
```

You will see the simulation start in your terminal, with the Dispatcher Agent receiving tasks, planning routes, and assigning them to drivers.

(Optional) Run the Streamlit Dashboard

If your project has a dashboard.py file:

```bash
# In a new terminal window
source venv/bin/activate
streamlit run dashboard.py
```

This will open a dashboard in your browser to visualize the fleet's progress.

## 🗺️ Project Roadmap
Phase 0: Foundation: Setup project, data models (models.py).

Phase 1: Simulation: Build the core Environment class (environment.py).

Phase 2: Optimization Engine: Build the OSRM connector and OR-Tools solver (optimizer.py).

Phase 3: The First Agent: Create the Dispatcher agent and tools (agents.py).

Phase 4: Multi-Agent Collaboration: Create Driver agents and establish communication.

Phase 5: The Adaptive Loop: Make the Dispatcher run in a continuous loop, reacting to events.

Phase 6: Visualization: Build the Streamlit dashboard (dashboard.py).