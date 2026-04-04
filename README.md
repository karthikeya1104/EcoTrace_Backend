# EcoTrace Backend API

## Overview

EcoTrace is a comprehensive sustainability tracking platform that measures and optimizes environmental impact across supply chains. The backend provides a robust REST API that enables stakeholders to make data-driven decisions for a greener future.

### Key Capabilities

- Manufacturers create products and batches with detailed material tracking
- Transporters log shipments with real-time carbon emission calculations
- Lab technicians conduct sustainability tests and generate reports
- Administrators oversee operations and manage system data
- AI engine analyzes batches and generates sustainability scores
- Public access via QR codes for transparency and verification
- **Lab Technicians** conduct sustainability tests and generate reports
- **Administrators** oversee operations and manage system data
- **AI Engine** analyzes batches and generates sustainability scores
- **Public Access** via QR codes for transparency and verification

---

## Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | High-performance async web API |
| Database | SQLAlchemy + SQLite/PostgreSQL | ORM and data persistence |
| Validation | Pydantic | Data validation and serialization |
| Authentication | JWT | Secure token-based authentication |
| Documentation | Swagger/OpenAPI | Interactive API documentation |

### Design Principles

- Modular service-oriented architecture with clear separation of concerns
- Role-based access control with granular permissions
- Comprehensive data validation and business logic enforcement
- Async operations for scalability and performance
- Type hints and documentation for maintainability

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Database and app configuration
│   ├── database.py             # Database connection and session management
│   ├── core/
│   │   ├── config.py          # Core configuration settings
│   │   ├── roles.py           # Role definitions and permissions
│   │   └── security.py        # JWT utilities and security functions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # User authentication and profile models
│   │   ├── product.py         # Product definitions and specifications
│   │   ├── batch.py           # Production batch tracking
│   │   ├── transport.py       # Shipment and logistics models
│   │   ├── lab_report.py      # Laboratory test results
│   │   ├── review.py          # User feedback and ratings
│   │   ├── audit_log.py       # System activity audit trail
│   │   └── ai_score.py        # AI-generated sustainability scores
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # User data validation schemas
│   │   ├── product.py         # Product request/response schemas
│   │   ├── batch.py           # Batch data structures
│   │   ├── transport.py       # Transport operation schemas
│   │   ├── lab_report.py      # Lab report validation
│   │   ├── review.py          # Review and feedback schemas
│   │   └── transport.py       # Transport data models
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── user.py            # User database operations
│   │   ├── product.py         # Product CRUD operations
│   │   ├── batch.py           # Batch management functions
│   │   ├── transport.py       # Transport CRUD operations
│   │   ├── lab_report.py      # Lab report database functions
│   │   ├── material.py        # Material tracking operations
│   │   ├── review.py          # Review management
│   │   └── admin.py           # Administrative operations
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User management routes
│   │   ├── products.py        # Product management API
│   │   ├── batches.py         # Batch operations
│   │   ├── transports.py      # Transport management
│   │   ├── lab.py             # Laboratory operations
│   │   ├── ai.py              # AI and analytics endpoints
│   │   ├── admin.py           # Administrative routes
│   │   ├── reviews.py         # Review system endpoints
│   │   └── public.py          # Public access routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_engine.py       # AI scoring and analysis service
│   │   ├── carbon_engine.py   # Carbon emission calculations
│   │   ├── change_analyzer.py # Material change detection
│   │   └── email.py           # Email notification service
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Centralized logging utility
│       ├── helpers.py         # Common helper functions
│       └── email.py           # Email utilities
├── logs/                      # Application logs directory
├── requirements.txt           # Python dependencies
├── API_BUILD_SUMMARY.md       # API endpoint documentation
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.9 or higher
- **Package Manager**: pip (comes with Python)
- **Terminal**: PowerShell, Command Prompt, or bash

### Installation & Setup

1. **Navigate to backend directory:**
   ```powershell
   cd backend
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure database (optional):**
   - Default: SQLite (`sqlite:///./ecotrace.db`)
   - For production: Edit `app/config.py` or set `DATABASE_URL` environment variable

5. **Initialize database:**
   ```powershell
   # Tables auto-create on first run
   # For migrations (if using Alembic):
   # alembic upgrade head
   ```

6. **Start development server:**
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the application:**
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc
   - **API Base URL**: http://localhost:8000/api

---

## 🔐 Authentication & Authorization

### JWT-Based Security

- **Token Generation**: Secure JWT tokens with user claims
- **Role-Based Access**: Four distinct user roles with specific permissions
- **Session Management**: Stateless authentication with automatic expiration
- **Token Refresh**: Secure token renewal without re-authentication

### User Roles & Permissions

| Role | Primary Functions | Key Permissions |
|------|------------------|-----------------|
| **manufacturer** | Product creation, batch management | Own products/batches CRUD, view AI scores |
| **transporter** | Shipment tracking, emission calculation | Transport CRUD, route validation, emission reports |
| **lab** | Testing, report generation | Lab reports CRUD, batch analysis, quality assurance |
| **admin** | System oversight, user management | Full system access, audit logs, user administration |

---

## ✨ Core Features

### 🏭 Product & Batch Management

- **Product Lifecycle**: Create, update, and manage product catalogs
- **Batch Tracking**: Detailed production batches with material composition
- **Material Analysis**: Track ingredients, quantities, and sustainability metrics
- **Status Monitoring**: Real-time batch status updates (pending → in_transit → completed)

### 🚚 Transport & Carbon Tracking

- **Route Management**: Origin-to-destination shipment tracking
- **Emission Calculation**: Automatic CO2 calculations based on distance, mode, and weight
- **Chain Validation**: Prevent circular routes and ensure supply chain integrity
- **Analytics Dashboard**: Distance, emissions, and cost tracking

### 🧪 Laboratory Operations

- **Test Management**: Comprehensive testing workflows and methodologies
- **Report Generation**: Detailed sustainability reports with certifications
- **Quality Assurance**: Test result validation and compliance checking
- **Status Tracking**: Monitor test progress and completion rates

### 🤖 AI & Sustainability Analytics

- **Score Generation**: Multi-factor sustainability scoring (environmental, ethical, safety, cost)
- **Material Analysis**: Component-level impact assessment
- **Change Detection**: Track improvements between batch versions
- **Insights Engine**: AI-powered recommendations for optimization

### 📊 Administrative Oversight

- **User Management**: Complete user lifecycle management
- **Audit Logging**: Comprehensive system activity tracking
- **System Statistics**: Global metrics and performance monitoring
- **Data Integrity**: Validation and consistency enforcement

---

## 🔧 Core Services

### AI Engine (`services/ai_engine.py`)
**Purpose**: Generate intelligent sustainability scores and insights
- Multi-dimensional scoring algorithm
- Material composition analysis
- Production method evaluation
- ML model integration ready

### Carbon Engine (`services/carbon_engine.py`)
**Purpose**: Calculate transportation emissions accurately
- Distance-based calculations
- Transport mode factors (air, sea, rail, road)
- Weight and volume considerations
- Carbon intensity coefficients

### Change Analyzer (`services/change_analyzer.py`)
**Purpose**: Track material modifications and implications
- Batch comparison algorithms
- Sustainability impact assessment
- Cost and efficiency analysis
- Supply chain optimization suggestions

---

## 🗄️ Data Models

| Model | Purpose | Key Relationships |
|-------|---------|-------------------|
| **User** | Authentication and role management | Roles, audit logs |
| **Product** | Product definitions and specifications | Batches, manufacturer |
| **Batch** | Production batch tracking | Materials, transports, reports, AI scores |
| **Transport** | Shipment and logistics | Batches, emissions, transporter |
| **LabReport** | Test results and findings | Batches, lab technician |
| **AIScore** | Sustainability metrics | Batches, AI analysis |
| **AuditLog** | System activity tracking | All models, users |
| **Review** | User feedback system | Batches, consumers |

---

## 🚢 Production Deployment

### Environment Setup

1. **Database Configuration:**
   ```powershell
   # PostgreSQL recommended for production
   DATABASE_URL=postgresql://user:password@host:5432/ecotrace
   ```

2. **Security Settings:**
   ```powershell
   JWT_SECRET_KEY=your-super-secure-secret-key-here
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

### Server Deployment

**Option 1: Gunicorn (Recommended)**
```powershell
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Option 2: Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

### Security Checklist

- ✅ Use HTTPS/TLS in production
- ✅ Implement rate limiting
- ✅ Enable request logging and monitoring
- ✅ Store secrets as environment variables
- ✅ Configure CORS appropriately
- ✅ Validate all user inputs
- ✅ Implement comprehensive error handling

---

## 🧪 Testing & Development

### Running Tests
```powershell
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

### Development Workflow

1. **Code Quality**: Use type hints and comprehensive docstrings
2. **Error Handling**: Implement graceful exception management
3. **Logging**: Utilize the centralized logger utility
4. **Documentation**: Keep API documentation current
5. **Testing**: Write unit and integration tests for new features

### Code Standards

- **Type Hints**: Full Python type annotation coverage
- **Documentation**: Comprehensive docstrings for all functions
- **Naming**: Descriptive, consistent naming conventions
- **Structure**: Clean separation of concerns
- **Security**: Input validation and secure coding practices

---

## 📚 API Documentation

For detailed endpoint specifications, request/response formats, and implementation status, see:
- **[API_BUILD_SUMMARY.md](./API_BUILD_SUMMARY.md)** - Complete endpoint reference
- **Interactive Docs**: http://localhost:8000/docs (when running)
- **OpenAPI Spec**: http://localhost:8000/openapi.json

---

## 🤝 Contributing

### Adding New Features

1. **Define Requirements**: Specify endpoints and data structures
2. **Create Schemas**: Add Pydantic models in `schemas/`
3. **Implement Models**: Define SQLAlchemy models in `models/`
4. **Build CRUD Operations**: Add database functions in `crud/`
5. **Create Routes**: Implement API endpoints in `routes/`
6. **Add Business Logic**: Extend services as needed
7. **Update Documentation**: Maintain API_BUILD_SUMMARY.md

### Code Review Checklist

- ✅ Type hints and docstrings present
- ✅ Input validation implemented
- ✅ Error handling comprehensive
- ✅ Role-based access enforced
- ✅ Tests written and passing
- ✅ Documentation updated

---

## 📞 Support & Troubleshooting

### Common Issues

**Database Connection Errors:**
- Verify DATABASE_URL format
- Check database server status
- Ensure proper permissions

**Authentication Problems:**
- Confirm JWT_SECRET_KEY is set
- Check token expiration
- Verify user roles and permissions

**API Errors:**
- Review request/response formats
- Check API_BUILD_SUMMARY.md for correct endpoints
- Examine application logs in `logs/` directory

### Getting Help

1. Check the interactive API documentation at `/docs`
2. Review API_BUILD_SUMMARY.md for endpoint details
3. Examine application logs for error messages
4. Test with different user roles to isolate permission issues

---

## 📄 License

This project is licensed under the MIT License. See the main project repository for full license details.

1. **Clone and navigate to backend:**
   ```powershell
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure database (optional):**
   Edit `app/config.py` to set database URL. Default is SQLite (`sqlite:///./ecotrace.db`)

5. **Initialize database:**
   ```powershell
   # If using migrations with Alembic
   alembic upgrade head
   
   # Otherwise, tables are created on first run
   ```

6. **Start development server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

7. **Access the API:**
   - Interactive API docs (Swagger): http://localhost:8000/docs
   - API base: http://localhost:8000/api

---

## 📚 API Documentation

For comprehensive API endpoint documentation, role requirements, request/response examples, and implementation status, see [API_BUILD_SUMMARY.md](./API_BUILD_SUMMARY.md).

---

## 🔐 Authentication & Authorization

- **JWT Tokens:** Token-based authentication for all protected endpoints
- **Role-Based Access:** Four primary roles with granular permissions:
  - `manufacturer` – Product and batch management
  - `transporter` – Transport and shipment tracking
  - `lab` – Test creation and reporting
  - `admin` – System administration and oversight
- **Token Storage:** Tokens include user ID, role, and expiration claims
- **Session Management:** Stateless JWT validation on each request

---

## ✨ Key Features

### 📦 Product & Batch Management
- Create, read, update, delete products
- Manage product batches with material composition tracking
- Manufacturer-scoped access to own products
- Batch status tracking and validation

### 🚚 Transport & Emission Tracking
- Create transport records with origin/destination validation
- Automatic carbon emission calculations based on distance and mode
- Transport chain validation to prevent looping routes
- Aggregated statistics for transporter dashboards

### 🧪 Lab Operations
- Manage lab test requests and reports
- Structure test data with scope, methodology, and results
- Track test status and completeness
- Generate sustainability insights from reports

### 🤖 AI & Sustainability Analysis
- Generate AI-powered sustainability scores for batches
- Multi-factor scoring: environmental, ethical, safety, cost
- Material-level analysis for impact optimization
- Integration-ready for ML models (currently using stub data)

### 📊 Statistics & Dashboards
- Manufacturer dashboard: product counts, batch metrics
- Transporter dashboard: distance, emissions, cost tracking
- Search and pagination for all list endpoints
- Aggregation functions for quick metrics

---

## 🛠️ Core Services

### Carbon Engine (`services/carbon_engine.py`)
Calculates transportation emissions based on:
- Distance traveled
- Transport mode (air, sea, rail, road)
- Weight/volume of goods
- Carbon intensity factors

### AI Engine (`services/ai_engine.py`)
Generates sustainability scores considering:
- Material composition
- Production methods
- Transport carbon footprint
- Test results and certifications

### Change Analyzer (`services/change_analyzer.py`)
Tracks material changes between batches to identify:
- Sustainability improvements
- Cost implications
- Supply chain modifications

---

## 🗄️ Database Models

**User** – Authentication and role management
**Product** – Product definitions with manufacturer relationship
**Batch** – Production batches with material composition
**Transport** – Shipment records with emission metadata
**LabReport** – Test results and findings
**AIScore** – Calculated sustainability scores
**AuditLog** – System activity tracking
**Review** – Peer reviews and feedback

---

## 🚢 Production Deployment

### Database Setup
```powershell
# Use production-grade database
# PostgreSQL recommended for production
set DATABASE_URL=postgresql://user:password@host:5432/ecotrace
```

### Server Setup
```powershell
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -b 0.0.0.0:8000
```

### Environment Variables
```
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your-secret-key
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-w", "4"]
```

### Security Recommendations
- ✅ Use HTTPS/TLS in production
- ✅ Implement rate limiting
- ✅ Add request logging and monitoring
- ✅ Use environment variables for secrets
- ✅ Enable CORS appropriately
- ✅ Validate all user inputs
- ✅ Implement request signing for critical operations

---

## 🧪 Testing

To add tests, create a `tests/` directory:
```powershell
pip install pytest pytest-asyncio httpx
pytest tests/
```

---

## 📝 Development Workflow

1. **Feature branches:** Create branches from `main`
2. **Type hints:** Use Python type annotations for clarity
3. **Docstrings:** Document functions and classes
4. **Error handling:** Handle exceptions gracefully
5. **Logging:** Use the logger utility for diagnostics
6. **Testing:** Write tests for new endpoints

---

## 🤝 Contributing

When extending the API:
1. Define Pydantic schema in `schemas/`
2. Create SQLAlchemy model in `models/`
3. Implement CRUD operations in `crud/`
4. Add routes in `routes/`
5. Add business logic to `services/`
6. Update API documentation

---

## 📞 Support

For issues or questions:
- Check API documentation at http://localhost:8000/docs
- Review API_BUILD_SUMMARY.md for endpoint details
- Check logs in `logs/` directory for errors

---

## 📄 License

See main project repository for license information.
