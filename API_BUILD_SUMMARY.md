# EcoTrace API Summary

## ✅ All APIs Built & Ready (Feb 2026)
The backend has evolved since the original draft. Routes are now grouped by role, pagination and statistics endpoints have been added, and most operations are restricted to the authenticated user.

---
### Manufacturer Endpoints
#### **Products** (`/api/products`)
- `POST /` – Create a product (manufacturer)
- `GET /my-products/all` – List your products
- `GET /my-products/stats` – Dashboard metrics (total products, batch counts, latest batch per product)
- `GET /{product_id}` – Get product with batches **(admin only)**
- `GET /` – List all products **(admin only; supports skip/limit)**
- `PUT /{product_id}` – Update product **(admin only)**
- `DELETE /{product_id}` – Delete product **(admin only)**

#### **Batches** (`/api/batches`)
- `GET /my` – Paginated list of your batches (page, limit, search)
- `GET /{batch_id}` – Retrieve a batch you own
- `POST /{product_id}` – Create a batch with AI validation (manufacturer)
- `PUT /{batch_id}` – Update batch (manufacturer)
- `DELETE /{batch_id}` – Delete batch (manufacturer)

> (Previous public/admin filtering by product or status was removed during refactor; batch access is now scoped to the manufacturer. we will be adding batch fetch for admin by manufacturer or product specific)

---
### Transporter Endpoints
#### **Transports** (`/api/transports`)
- `GET /my/stats` – Aggregated stats (total transports, distance, emissions, avg per km)
- `GET /my` – Paginated list of your transports (skip, limit, search across origin/destination/product/batch)
- `GET /batch/{batch_id}/available-origins` – Valid next‑hop origins for a batch
- `GET /batch/{batch_id}` – Paginated transports for a given batch (manufacturer role)
- `POST /` – Create a transport with emission calculation and chain validation (transporter)
- `GET /{transport_id}` – Get a transport you own (transporter)
- `PUT /{transport_id}` – Update transport **(admin only; transporter id must match)**
- `DELETE /{transport_id}` – Delete transport **(admin only; transporter id must match)**

---
### Public & AI Routes (`/api/ai`)
- `GET /batch/{batch_id}/score` – Retrieve AI sustainability score (public)
- `POST /batch/{batch_id}/analyze-materials` – Analyze batch materials (manufacturer owns batch)
- `POST /batch/{batch_id}/generate-score` – Regenerate AI score (admin only)
- `GET /batch/{batch_id}/insights` – Public sustainability insights (placeholder)

> All AI-related endpoints currently return stub/placeholder data but are wired for easy replacement.

---
## 🔧 Built Components and Utilities

✅ **Services:**
- `carbon_engine.py` – Carbon & emission calculations (used for transports)
- `ai_engine.py` – Stubbed AI score generation & material analysis
- `change_analyzer.py` – Material change classification logic

✅ **New helpers / stats:**
- Manufacturer dashboard (`get_manufacturer_dashboard`)
- Transport statistics (`get_transport_stats`)
- Origin lookup for transport chains (`get_available_origins`)

✅ **Schemas:**
- ProductCreate, ProductUpdate, ProductResponse, ProductWithBatches
- BatchCreate, BatchUpdate, BatchResponse, BatchListResponse
- TransportCreate, TransportUpdate, TransportResponse, TransportListResponse

✅ **CRUD Patterns:**
- Products: full CRUD plus manufacturer listing & dashboard
- Batches: manufacturer‑scoped CRUD with pagination
- Transports: scoped CRUD, pagination, stats, batch queries

✅ **Data Models:**
- Product, Batch, Transport, AIScore (all interlinked)
- User roles enforced via `app/core/roles.py`

---
## 📝 Notes

- All endpoints enforce **role‑based access control**.
- Pagination and search added for batches & transports.
- Emission calculations now recalc on updates.
- Stats endpoints provide quick dashboard figures for clients.
- AI & analysis functions are placeholders; swapping in real models will not affect routes.

---
## 🚀 Next Steps: Real AI Implementation
Replace or extend the following functions when moving beyond stub data:
- `app/services/ai_engine.py` – `generate_ai_score()` & `analyze_batch_materials()`
- `app/services/change_analyzer.py` – `analyze_material_differences()`

The API surface is stable; the new AI logic can be plugged in without changing clients.
