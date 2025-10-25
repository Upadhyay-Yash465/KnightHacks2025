# KnightHacks 2025 Project

This is the main project directory for the KnightHacks 2025 submission.

## Project Structure

```
KnightHacks2025/
├── backend/                 # Backend application
│   ├── src/                # Source code
│   ├── dependencies/       # Dependencies and build files
│   ├── config/             # Configuration files
│   ├── tests/              # Test files
│   ├── docs/               # Backend documentation
│   ├── agent/              # AI agent modules
│   ├── services/           # Service modules
│   └── utils/              # Utility modules
├── frontend/               # Frontend application
│   ├── src/                # Source code
│   ├── dependencies/       # Dependencies and build files
│   ├── config/             # Configuration files
│   ├── tests/              # Test files
│   └── docs/               # Frontend documentation
└── docs/                   # Project documentation
```

## Getting Started

### Backend Setup
1. Navigate to `backend/`
2. Install dependencies: `pip install -r dependencies/requirements.txt`
3. Configure environment: Copy `config/env.example` to `.env` and update values
4. Run the application: `python src/main.py`

### Frontend Setup
1. Navigate to `frontend/`
2. Install dependencies: `npm install` (from `dependencies/` directory)
3. Run the development server: `npm run dev`

## Documentation

- Project documentation is available in the `docs/` directory
- Backend-specific documentation is in `backend/docs/`
- Frontend-specific documentation is in `frontend/docs/`

## Contributing

Please follow the established folder structure when adding new files:
- Source code goes in `src/` directories
- Configuration files go in `config/` directories
- Dependencies and build files go in `dependencies/` directories
- Tests go in `tests/` directories
- Documentation goes in `docs/` directories
