# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NSales Pro is a multi-layered AI-powered sales management application with a Vue.js frontend, React chat widget, and FastAPI backend. The system integrates Google services (Calendar/Gmail) with AI capabilities for intelligent business automation.

## Architecture

The project consists of three main components:

1. **Vue.js Main Application** (root) - Primary dashboard and business logic
2. **React Chat Widget** (`react-typescript-app/`) - Embeddable AI chat interface  
3. **FastAPI Backend** (`backend/`) - AI chat API with Google services integration

## Common Development Commands

### Frontend (Vue.js Main App)
```bash
# Development server
npm run dev

# Build for production
npm run build

# Type checking
vue-tsc -b

# Testing
npm run test              # Run all tests with Vitest
npm run test:watch        # Watch mode
npm run test:coverage     # Generate coverage report
npm run test:ui          # Visual test interface
npm run test:e2e         # Cypress E2E tests
npm run test:e2e:dev     # Cypress in dev mode

# Code formatting
npm run format           # Format all files
npm run format:check     # Check formatting
```

### React Chat Widget
```bash
cd react-typescript-app

# Development server
npm run dev

# Build for production
npm run build

# Type checking
tsc -b

# Linting and formatting
npm run lint             # Check for issues
npm run lint:fix         # Auto-fix issues
npm run format           # Format code
npm run format:check     # Check formatting
```

### Backend (FastAPI)
```bash
cd backend

# Start development server
python main.py
# OR
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Install dependencies
pip install -r requirements.txt

# Environment setup
cp .env.example .env      # Then edit .env with OPENAI_API_KEY
```

## High-Level Architecture

### Frontend Architecture

**Vue.js Application**
- **Feature-based structure**: Organized by business domains (auth, chat, employee, member, notice, partner, project, sales)
- **Dependency Injection**: Uses `tsyringe` for service layer management with decorators (`@singleton()`, `@inject()`)
- **Component Library**: Extensive UI component system with Reka UI (shadcn/ui-style components)
- **State Management**: Pinia for global state, VueUse composables for reactive utilities
- **Testing**: Vitest for unit tests with jsdom environment, Cypress for E2E testing

**Key Patterns:**
- Repository pattern for data access (`features/*/repository/`) with dependency injection
- Entity models for type safety (`features/*/entity/`) using TypeScript interfaces
- Composables for reusable logic (`core/composables/`)
- Strict TypeScript with form validation (Vee-Validate + Zod schemas)
- Feature modules contain: `components/`, `entity/`, `repository/`, `views/`, and sometimes `layouts/`

**React Chat Widget**
- Standalone embeddable widget for AI chat functionality
- Session management with TypeScript interfaces
- Tailwind CSS for styling consistency
- EventSource for real-time streaming

### Backend Architecture

**FastAPI Application** (`backend/`)
- RESTful API with OpenAI integration (GPT-4o, GPT-4, GPT-3.5-turbo)
- Google Services integration via Function Calling system
- File processing pipeline (PDF, DOCX, OCR with pytesseract)
- Vector store support for knowledge base functionality
- Memory-based storage (development) with database migration path

**Key Services:**
- `GoogleAuthService` - OAuth2 authentication
- `GoogleCalendarService` - Calendar operations (events, scheduling, free time finding)
- `GoogleGmailService` - Email operations (send, receive, search)
- Function Calling system for natural language → API translation
- Tools management system with registry pattern

### Technology Stack

**Frontend:**
- Vue 3 + TypeScript + Vite
- TailwindCSS + Pretendard font
- Reka UI components, Vue Router, Pinia
- Vitest + Cypress for testing
- TSyringe for dependency injection

**Backend:**
- FastAPI + Python 3.9+
- OpenAI API integration with streaming support
- Google APIs (Calendar, Gmail)
- File processing (PyPDF2, python-docx, pytesseract)

## Development Workflow

### Environment Setup
1. **Root Vue app**: `npm install` → `npm run dev` (port 5173)
2. **React widget**: `cd react-typescript-app` → `npm install` → `npm run dev` (port 5174)  
3. **Backend**: `cd backend` → `pip install -r requirements.txt` → Configure `.env` → `python main.py` (port 8000)

### Google Services Setup
Follow `backend/google_setup.md` for OAuth2 configuration. Required files:
- `backend/credentials.json` (OAuth2 client - not in repo)
- `backend/token.pickle` (auto-generated user tokens)

### Testing Strategy
- **Unit Tests**: Vitest for component and service testing with jsdom environment
- **E2E Tests**: Cypress for user workflow validation
- **Integration**: Test API endpoints via Swagger UI at `localhost:8000/docs`
- **Coverage**: V8 coverage provider with text, JSON, and HTML reporting

### Code Quality Tools
- **Prettier**: Consistent formatting across all code with project-specific config
- **ESLint**: Vue and React specific linting with TypeScript support
- **TypeScript**: Strict type checking with `vue-tsc` for templates
- **Babel**: Decorator support for tsyringe dependency injection

## Important Implementation Details

### Frontend Patterns
- **Repository Pattern**: All API calls through repository classes with `@singleton()` decorator and `@inject()` for dependencies
- **Feature Modules**: Self-contained business logic with entities, repositories, views, and components
- **Type Safety**: Zod schemas for runtime validation, TypeScript interfaces for compile-time safety
- **Component Architecture**: Reusable UI components in `src/core/components/ui/` with consistent API patterns
- **HTTP Client**: Centralized `HttpRepository` using Axios with error handling

### Chat System Integration
- **Streaming Support**: Server-Sent Events with `@microsoft/fetch-event-source`
- **Enhanced Chat API**: Tools support with Google services integration
- **File Upload**: Multipart form handling with various file types
- **Vector Stores**: Knowledge base functionality with document indexing

### Backend Integration
- **CORS Configuration**: Supports `localhost:5173`, `localhost:5174`, `localhost:3000`
- **Streaming**: Server-Sent Events for real-time AI responses
- **File Upload**: Multipart form handling with text extraction and OCR
- **Function Calling**: Natural language triggers for Google API operations
- **Tools System**: Registry-based tool management with status monitoring

### Migration Considerations
- Backend uses in-memory storage (development only)
- Production requires database implementation (SQLAlchemy + PostgreSQL recommended)
- Frontend designed for scalable deployment with proper build optimization
- Dependency injection pattern facilitates testing and modularity

## Testing Commands Reference

```bash
# Frontend (Vue)
npm run test                    # All unit tests
npm run test:watch             # Watch mode
npm run test:coverage          # Coverage report
npm run test:ui                # Visual test interface
npm run test:e2e               # Full E2E suite
npm run test:e2e:dev          # Interactive E2E

# React Widget
cd react-typescript-app
npm run lint                   # Code quality check
npm run lint:fix              # Auto-fix issues

# Backend
cd backend
python main.py                 # Start server for API testing
# Visit localhost:8000/docs for Swagger UI testing
```