# EcoTrace Backend

## 📋 Project Overview

**EcoTrace** is a platform for tracking environmental impact and sustainability metrics across supply chains. It enables manufacturers to submit product batches with material details, transporters to log shipments with carbon emission calculations, and lab technicians to conduct and report sustainability tests. An AI engine analyzes batches and generates sustainability scores based on environmental, ethical, safety, and cost factors.

The platform serves multiple stakeholders:
- **Manufacturers** create and manage products, batch submissions, and view AI sustainability scores
- **Transporters** log shipments, track emissions, and validate transport chains
- **Lab Technicians** conduct tests and report results
- **Administrators** oversee all operations and manage system data

This repository contains the **backend API service**—a Python FastAPI application that handles all data operations, business logic, role-based access control, and AI integrations.

---

## Backend Architecture

Python FastAPI service with SQLAlchemy ORM, role-based access, and modular services for 
AI, carbon calculations, and change analysis.

---

## 🧱 Structure

```
app/
├── crud/          # database operations
├── models/        # SQLAlchemy models
├── routes/        # FastAPI routers (products, batches, transports, ai, auth, etc.)
├── schemas/       # Pydantic request/response models
├── services/      # helper logic (ai_engine, carbon_engine, etc.)
├── utils/         # utilities like email, logger, helpers
├── core/          # config, security, roles
└── main.py        # app entry point
```

---

## 🚀 Getting Started

1. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Configure database in `app/config.py` (defaults to SQLite). Run migrations if needed.

4. Start the development server:
   ```powershell
   uvicorn app.main:app --reload
   ```

5. View API docs at `http://localhost:8000/docs`

---

## 📄 API Documentation

See `API_BUILD_SUMMARY.md` for detailed route documentation, role requirements, and examples.

---

## 🧠 Features

- **Role-based access:** manufacturers, transporters, labs, and admins (via `core/roles.py`)
- **Product/batch management:** full CRUD with validation
- **Transport tracking:** emission calculations, chain validation, and stats
- **AI services:** placeholder endpoints for sustainability scoring and material analysis
- **Pagination & search:** on batch and transport listings
- **Statistics:** manufacturer and transporter dashboards with aggregated metrics

---

## 🛠️ Key Services

- **carbon_engine.py** – emission calculations for transports
- **ai_engine.py** – placeholder AI score generation (ready for real ML integration)
- **change_analyzer.py** – material change classification

---

## 📦 Production Deployment

- Use a production database (PostgreSQL, MySQL, etc.)
- Run behind Uvicorn/Gunicorn with environment variables for DB URL and secrets
- Add logging, error tracking, and security hardening as needed
- Consider Docker containerization
