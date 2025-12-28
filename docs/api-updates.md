# API updates

This document summarizes recent backend changes for scheduling and search.

## CORS and routes
- Added CORS middleware to allow `http://localhost:3000`.
- Standardized employees root routes to no trailing slash.

## Schedule search
- Added `POST /api/job_shifts/FindSchedule`.
- Optional filters: `manager_id`, `employee_id`, `start_date`, `end_date`.
- Response includes nested `client` and `employee` details.

## Text search endpoints (frontend search)
- Added `POST /api/employees/text-search` with `{ query, manager_id?, limit? }`.
- Added `POST /api/clients/text-search` with `{ query, manager_id?, limit? }`.
- Employee text search matches only `first_name`, `last_name`, and `nickname`.
