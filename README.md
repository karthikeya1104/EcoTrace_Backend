# EcoTrace Backend API

## Overview

EcoTrace is a production-grade sustainability tracking platform that measures and optimizes environmental impact across supply chains. The backend provides a comprehensive REST API enabling manufacturers, transporters, lab technicians, and administrators to track products from production through delivery with real-time carbon emission calculations and AI-powered sustainability analysis.

### Platform Status: Live & Production Ready
- **Frontend**: https://ecotrace-gcet.vercel.app/
- **Backend API**: Deployed and operational

### Core Capabilities

- **🏭 Manufacturers** create products and batches with detailed material tracking
- **🚚 Transporters** log shipments with automatic carbon emission calculations  
- **🧪 Lab Technicians** conduct sustainability tests and generate comprehensive reports
- **👥 Administrators** manage users and monitor system-wide sustainability metrics
- **🤖 AI Engine** analyzes batches and generates multi-factor sustainability scores
- **📱 Public Access** via QR codes for supply chain transparency
- **🔒 JWT Security** with granular role-based access control

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | High-performance async REST API |
| Database | SQLAlchemy | ORM and data persistence |
| Validation | Pydantic | Type-safe data validation |
| Authentication | JWT (python-jose) | Secure token-based auth |
| AI | Google Generative AI | Sustainability scoring |
| Password Security | bcrypt | Secure password hashing |
| CORS | FastAPI CORSMiddleware | Cross-origin requests |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                        # FastAPI app & route registration
│   ├── config.py                      # Database configuration
│   ├── database.py                    # Session management
│   ├── core/
│   │   ├── security.py                # JWT & password utilities
│   │   └── roles.py                   # Role definitions
│   ├── models/                        # SQLAlchemy models
│   │   ├── user.py, product.py, batch.py, transport.py
│   │   ├── lab_report.py, review.py, ai_score.py
│   │   └── audit_log.py
│   ├── schemas/                       # Pydantic validation schemas
│   ├── crud/                          # Database operations
│   ├── routes/                        # API endpoints
│   │   ├── auth.py, products.py, batches.py
│   │   ├── transport.py, lab_reports.py, ai.py
│   │   └── admin.py, reviews.py, public.py
│   ├── services/                      # Business logic
│   │   ├── ai_engine.py               # Sustainability scoring
│   │   ├── carbon_engine.py           # Emission calculations
│   │   └── change_analyzer.py         # Batch comparison
│   └── utils/logger.py                # Structured logging
├── logs/                              # Application logs
├── requirements.txt                   # Python dependencies
├── API_BUILD_SUMMARY.md               # Complete endpoint reference
└── README.md                          # This file
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip package manager

### Quick Start

1. Navigate to backend:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1      # Windows
   source venv/bin/activate          # Unix/macOS
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment (`.env` file):
   ```env
   DATABASE_URL=sqlite:///./ecotrace.db
   JWT_SECRET_KEY=your-secret-key-here
   GOOGLE_AI_API_KEY=your-api-key-here
   FRONTEND_URL=http://localhost:5173
   DEBUG=true
   ```

5. Start development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. Access APIs:
   - **Interactive Docs**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Authentication System

### JWT-Based Architecture
- **Token Type**: Bearer tokens with 24-hour expiration
- **Refresh Flow**: Issue new access token using refresh token
- **Role Claims**: User role embedded in token payload
- **Session**: Stateless on server side

### User Roles & Permissions

| Role | Functions | Permissions |
|------|-----------|------------|
| **manufacturer** | Create products/batches | Own product/batch CRUD, AI scores |
| **transporter** | Manage shipments | Transport CRUD, emission reports |
| **lab** | Conduct tests | Report CRUD, batch analysis |
| **admin** | System management | Full access, user management, audit logs |

### Auth Endpoints

- `POST /register` - Create account with role
- `POST /login` - Email/password authentication
- `GET /me` - Current user profile
- `POST /refresh` - Renew access token
- `POST /logout` - Session termination

---

## Core Features

### Product & Batch Management
- Create products with specifications and categories
- Track production batches with material composition
- Monitor batch status (pending → in_transit → completed)
- Sustainability metrics per material component
- Version control for batch iterations

### Transport & Emissions
- Automated CO2 calculations based on:
  - Transport distance and mode (road/rail/sea/air)
  - Cargo weight and volume
  - Real-world emission coefficients
- Route chain validation (prevent circular routes)
- Origin/destination management
- Cost tracking per shipment

### Laboratory Testing
- Receipt and management of pending test requests
- Structured test methodology documentation
- Test result recording and quality assurance
- Professional report generation with certifications
- Batch quality validation

### AI & Analytics
- **Multi-dimensional Scoring**: Environmental, ethical, safety, cost factors
- **Material Impact Analysis**: Component-level sustainability assessment
- **Change Detection**: Batch version comparison and improvement tracking
- **Intelligence**: AI-powered optimization recommendations
- **Google Generative AI** integration for advanced insights

### Administration
- User lifecycle management
- Complete audit logging of system activities
- System-wide analytics and metrics
- Data integrity enforcement
- Report generation

---

## API Endpoints Overview

For complete endpoint documentation see [API_BUILD_SUMMARY.md](./API_BUILD_SUMMARY.md)

### Authentication (`/api/auth`)
- User registration and login
- Token management and refresh
- Session handling

### Products (`/api/products`)
- Create, read, update, delete products
- List manufacturer's product catalog
- Dashboard statistics

### Batches (`/api/batches`)
- Batch CRUD operations
- Search and filtering
- Material composition tracking
- Status monitoring

### Transport (`/api/transports`)
- Shipment CRUD with auto-emission calculation
- Route management and validation
- Batch routing workflows
- Performance analytics

### Laboratory (`/api/lab`)
- Test management and scheduling
- Report creation and updates
- Quality assurance workflows
- Pending test queues

### AI Scoring (`/api/ai`)
- Generate batch sustainability scores
- Material impact analysis  
- Batch comparison reports
- Improvement recommendations

### Public Access (`/api/public`)
- QR code batch verification
- Supply chain transparency
- No authentication required

---

## Data Models

| Model | Purpose | Relationships |
|-------|---------|---------------|
| User | Auth & profiles | Roles, owned data, audit logs |
| Product | Product definitions | Batches, manufacturer |
| Batch | Production tracking | Materials, transports, tests, AI scores |
| Transport | Shipments | Batch, route, emissions |
| LabReport | Test results | Batch, conducted by lab tech |
| AIScore | Sustainability metrics | Batch, analysis data |
| AuditLog | Activity tracking | User, affected resource |
| Review | User feedback | Batch, reviewer |

---

## Production Deployment

### Environment Configuration

```env
# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:pass@host:5432/ecotrace

# Security
JWT_SECRET_KEY=your-production-secret-key
GOOGLE_AI_API_KEY=your-api-key

# CORS
FRONTEND_URL=your-production-frontend-url
CORS_ORIGINS=your-production-frontend-url

# Deploy Mode
DEBUG=false
```

### Deployment Options

**Gunicorn + Uvicorn (Recommended)**
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Docker Containerization**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

### Production Security

- ✅ HTTPS/TLS enabled
- ✅ Request logging and monitoring
- ✅ Secrets via environment variables
- ✅ CORS properly configured
- ✅ Input validation on all endpoints
- ✅ Comprehensive error handling
- ✅ Audit logging enabled

---

## Development & Testing

### Running Tests
```bash
pip install pytest pytest-asyncio httpx
pytest tests/ -v --cov=app --cov-report=html
```

### Code Quality Standards
- Full Python type hints
- Comprehensive docstrings
- Clear error handling
- Modular service architecture
- Input validation
- Security best practices

---

## Troubleshooting

**Database Connection Issues**
- Verify DATABASE_URL format
- Check database server status
- Ensure user has proper permissions

**Authentication Errors**
- Confirm JWT_SECRET_KEY is set
- Check token expiration (24 hours default)
- Verify user role and permissions

**API Issues**
- Check endpoint format in API_BUILD_SUMMARY.md
- Verify request body matches schema
- Review application logs in `logs/` directory
- Test with provided /docs interface

---

## 📄 License

See main project repository for license information.
