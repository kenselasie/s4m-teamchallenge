# Full Stack Code Challenge: PDF Parser

## Overview

This is a code challenge for full-stack developers. The challenge involves building a PDF parsing feature with a React frontend and FastAPI backend.

## Challenge Description

Create a feature that allows users to:

1. Upload a PDF file through a web interface
2. Parse the PDF content on the backend into chunks/sections:
   - Each PDF should be split into logical sections (e.g., by pages or chapters)
   - Store basic metadata (upload date, title, total pages) with the PDF
3. Store the parsed content in a database (PDF and its chunks)
4. Display the parsed content in a structured way on the frontend:
   - A list view showing available PDFs with their metadata
   - A detail view showing:
     - PDF metadata
     - A paginated list of chunks/sections
     - The ability to search through chunks

Note: Build as far as you get in a few hours, focus on the parts you consider most important to show your skills and best practices.
If you run out of time, feel free to add your thoughts and ideas as comments or notes.

And feel free to improve our code base ! :)

## Tech Stack

- Frontend: React + TypeScript
- Backend: FastAPI + Python

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Authentication

The boilerplate includes a basic authentication system:

- Demo credentials:
  - Email: demo@example.com
  - Password: demo123

## What We're Looking For

1. Clean, well-structured code
2. Architecture best practices
3. Quality best practices
4. Efficient database querying
5. Performance best practices
6. Security best practices
7. Test-Driven Development (TDD) approach to ensure code quality and maintainability

Please follow and improve what you find, leave comments to explain your changes.

## Time Expectation

This challenge is designed to take 4-6 hours.

If you run out of time, feel free to add your thoughts and ideas as comments or notes.

## Submission

1. Fork this repository
2. Implement your solution
3. Create a pull request
4. Include any additional documentation or notes in the PR description

## Extras

### To run frontend tests

1. Unit Test

```bash
cd frontend
npm run test
```

2. E2E Test

```bash
npm run cypress:open
```

### To run backend tests

1. All Tests (Unit and Integration Tests)

```bash
cd backend
python -m pytest tests
```

2. Unit Tests

```bash
cd backend
python -m pytest tests/unit
```

3. Integration Tests

```bash
cd backend
python -m pytest tests/integration
```

# Architecture Used - Notes

This project implements a **Clean Architecture** with **Layered Service** pattern, following traditional separation of concerns for maintainability.

## Backend Architecture

### Layer Structure:

```
app/
├── models/          # Domain entities (User, PDF, PDFChunk)
├── schemas/         # Data transfer objects (Pydantic models)
├── repositories/    # Data access layer (database operations)
├── services/        # Business logic layer
├── routers/         # API endpoints (presentation layer)
└── utils/          # Shared utilities
```

### Key Architectural Decisions:

1. **Repository Pattern**: Abstracts database operations behind interfaces

   - `base.py`: Generic repository with common CRUD operations
   - Entity-specific repositories extend the base for specialized queries

2. **Service Layer**: Contains business logic separate from API controllers

   - `auth_service.py`: Authentication and authorization logic
   - `pdf_service.py`: PDF processing and management logic

3. **Schema Validation**: Pydantic models ensure type safety and validation

   - Request/response models separate from domain models
   - Pagination schemas for consistent API responses

4. **Dependency Injection**: FastAPI's dependency system for loose coupling
   - Database sessions injected into repositories
   - Services injected into routers

## Frontend Architecture

### Component Structure:

```
src/
├── components/      # Reusable UI components
├── pages/          # Route-level components
├── context/        # Global state management (Auth, Notifications)
├── hooks/          # Custom React hooks
└── services/       # API communication layer
```

### Key Patterns:

- **Context API**: For global state (authentication, notifications)
- **Custom Hooks**: For data fetching and state management
- **Component Composition**: Modular, reusable components

## Testing Strategy

- **Unit Tests**: Individual component/service testing
- **Integration Tests**: API endpoint testing with test db
- **E2E Tests**: Full user journey testing with Cypress

## Future Improvements

1. **Database Migrations**: Replace create_tables with Alembic for proper schema versioning
2. **Caching Layer**: Add Redis for improved performance
3. **Support for bigger files**: PDF uploads support for larger file sizes

## Author Attribution

Add author metadata to PDF records for content ownership tracking.
