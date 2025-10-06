# Bookstore Management System (BMS)

Starter code for an ontology-driven, agent-based simulation of bookstore operations. The project demonstrates how to pair Owlready2 for ontology modelling with Mesa for multi-agent simulations, and exposes the simulation through a FastAPI backend and React dashboard.

## Project Goals

- Model a bookstore domain ontology that captures books, customers, employees, and inventory concepts.
- Encode business rules using SWRL (Semantic Web Rule Language) to drive agent behaviours.
- Simulate realistic bookstore scenarios where customer, employee, and inventory agents interact.
- Provide extension points for experimentation with message buses, decision policies, and logging/metrics.

## Repository Layout

```
.
+-- backend/
|   +-- app/
|       +-- __init__.py
|       +-- main.py
|       +-- schemas.py
|       +-- simulation_manager.py
|   +-- requirements.txt
+-- bms/
|   +-- __init__.py
|   +-- config.py
|   +-- data/
|   |   +-- bookstore_ontology.owl
|   |   +-- sample_inventory.json
|   +-- ontology/
|   |   +-- __init__.py
|   |   +-- builder.py
|   |   +-- rules.py
|   +-- simulation/
|       +-- __init__.py
|       +-- agents.py
|       +-- message_bus.py
|       +-- model.py
|       +-- policies.py
+-- frontend/
|   +-- index.html
|   +-- package.json
|   +-- src/
|       +-- App.tsx
|       +-- components/
|       +-- lib/
|       +-- pages/
|   +-- vite.config.ts
+-- scripts/
|   +-- run_simulation.py
+-- tests/
|   +-- test_smoke.py
+-- pyproject.toml
+-- requirements.txt
```

## Backend (FastAPI)

1. Create and activate a Python 3.10+ virtual environment.
2. Install the core simulation dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Install the API dependencies:

   ```
   pip install -r backend/requirements.txt
   ```

4. Run the API with Uvicorn:

   ```
   uvicorn backend.app.main:app --reload
   ```

## Frontend (Vite + React)

1. Install Node.js (18+) and npm or pnpm.
2. Install dependencies:

   ```
   cd frontend
   npm install
   ```

3. Start the development server:

   ```
   npm run dev
   ```

The dashboard expects the FastAPI service to be available at http://127.0.0.1:8000 by default. Override `VITE_API_BASE` to point to a different host if needed.

## Simulation Script

To run the sample simulation without the API:

```
python scripts/run_simulation.py
```

## Testing

Run the smoke tests with:

```
pytest
```

Add more test coverage as you extend the ontology, simulation agents, or API.
