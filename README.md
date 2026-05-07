# Timberline & Trestle Scheduling API

A professional FastAPI-based REST API for construction project scheduling, managing materials, phases, and calculating optimal project start dates based on supply chain lead times.

## Features

- **Phase Management**: Create, read, update, and delete construction phases with ordering and duration tracking
- **Material Tracking**: Manage materials with lead times and associate them with specific phases
- **Intelligent Scheduling**: Calculate the earliest safe project start date using critical-path analysis based on material lead times
- **RESTful API**: Clean, documented endpoints following REST conventions
- **Pydantic Validation**: Robust input validation with clear error messages

## Tech Stack

- **FastAPI** - Modern, high-performance web framework
- **SQLAlchemy 2.0** - SQL toolkit and ORM
- **Pydantic v2** - Data validation using Python type annotations
- **SQLite** - Lightweight database for development and testing
- **Pytest** - Testing framework

## Installation

### Prerequisites

- Python 3.11+

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd timberline_api

# Create and activate virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive documentation is automatically generated and available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Phases

| Method | Endpoint       | Description               |
| ------ | -------------- | ------------------------- |
| POST   | `/phases/`     | Create a new phase        |
| GET    | `/phases/`     | List all phases (ordered) |
| GET    | `/phases/{id}` | Get a specific phase      |
| PUT    | `/phases/{id}` | Update a phase            |
| DELETE | `/phases/{id}` | Delete a phase            |

### Materials

| Method | Endpoint          | Description             |
| ------ | ----------------- | ----------------------- |
| POST   | `/materials/`     | Create a new material   |
| GET    | `/materials/`     | List all materials      |
| GET    | `/materials/{id}` | Get a specific material |
| PUT    | `/materials/{id}` | Update a material       |
| DELETE | `/materials/{id}` | Delete a material       |

### Scheduling

| Method | Endpoint     | Description                           |
| ------ | ------------ | ------------------------------------- |
| GET    | `/schedule/` | Calculate earliest safe project start |

### Request/Response Examples

#### Create Phase

```bash
curl -X POST "http://localhost:8000/phases/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Foundation", "order": 1, "duration_days": 10}'
```

#### Create Material

```bash
curl -X POST "http://localhost:8000/materials/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Concrete", "lead_time_days": 5, "phase_id": 1}'
```

#### Get Schedule

```bash
curl "http://localhost:8000/schedule/?desired_start=2026-06-01T00:00:00"
```

Response:

```json
{
  "desired_start": "2026-06-01T00:00:00",
  "earliest_safe_start": "2026-06-01T00:00:00",
  "delay_days": 0,
  "milestones": [
    {
      "phase": {
        "id": 1,
        "name": "Foundation",
        "order": 1,
        "duration_days": 10
      },
      "earliest_start_date": "2026-06-01T00:00:00"
    }
  ]
}
```

## Scheduling Algorithm

The scheduling service uses critical-path logic to determine the earliest safe project start date:

1. **Phase Ordering**: Phases are sorted by their `order` field to establish the sequence
2. **Offset Calculation**: The start offset for each phase is computed based on preceding phase durations
3. **Shortfall Analysis**: For each material, the algorithm calculates if its lead time exceeds the available time before its assigned phase begins
4. **Delay Computation**: The maximum shortfall across all materials determines how many days the project start must be delayed

**Formula**: `earliest_safe_start = desired_start + max(shortfall across all materials)`

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage (requires pytest-cov)
pytest --cov=services --cov=routers
```

## Project Structure

```
timberline_api/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration and session management
│   └── models/              # SQLAlchemy ORM models
│       ├── material.py
│       └── phase.py
├── routers/                 # API route handlers
│   ├── material.py
│   ├── phase.py
│   └── project.py
├── schemas/                 # Pydantic request/response schemas
│   ├── material.py
│   ├── phase.py
│   └── project.py
├── services/                # Business logic
│   └── scheduler.py
├── utils/                   # Utilities and custom exceptions
│   └── exceptions.py
├── tests/                   # Test suite
│   └── test_scheduler.py
├── conftest.py              # Pytest configuration
├── pytest.ini               # Pytest settings
└── requirements.txt         # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
