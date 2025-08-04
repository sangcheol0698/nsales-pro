# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NSales Pro Chat API is a FastAPI-based AI chatting service backend with Google Services integration. It provides:

- AI-powered chat with OpenAI GPT models (GPT-4o, GPT-4, GPT-3.5-turbo)
- Real-time streaming chat capabilities
- Google Calendar and Gmail integration via Function Calling
- File upload support (PDF, DOCX, images with OCR)
- Web search capabilities
- Session and message management

## Common Development Commands

### Server Management
```bash
# Start development server
python main.py

# Alternative start with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Install dependencies
pip install -r requirements.txt

# Check server logs
tail -f server.log
```

### Environment Setup
```bash
# Create environment file (OPENAI_API_KEY required)
# Note: .env.example does not exist - create .env directly
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Google Services Setup
Follow `google_setup.md` for complete Google Calendar/Gmail integration setup. Key files:
- `credentials.json` - OAuth2 client credentials (not in repo)
- `token.pickle` - User auth tokens (auto-generated)

## High-Level Architecture

### Core Components

**Main Application (`main.py`)**
- FastAPI application with comprehensive chat API
- OpenAI integration with multiple model support
- Google Services Function Calling integration
- File processing (PDF, DOCX, OCR)
- Memory-based storage (development only)

**Google Services (`google_services.py`)**
- `GoogleAuthService` - OAuth2 authentication handling
- `GoogleCalendarService` - Calendar operations (events, creation, scheduling)
- `GoogleGmailService` - Email operations (send, receive, search)

**AI Tools System (`tools/`)**
- `ToolManager` - Centralized tool registry and initialization
- `ToolRegistry` - Tool registration and categorization system
- `GoogleCalendarViewTool`, `GoogleCalendarCreateTool`, `GoogleCalendarFindFreeTool` - Calendar tools
- `GmailSendTool`, `GmailViewTool` - Email tools
- Status monitoring and error handling for all tools

**Function Calling Integration**
- Google services exposed as OpenAI function tools
- Natural language to API translation
- Smart mention detection (@캘린더, @메일, etc.)
- Legacy integration via `google_functions.py` (GOOGLE_TOOLS, FUNCTION_MAP)

### Key Data Models
- `ChatMessage` - Individual chat messages
- `ChatSession` - Chat conversation sessions
- `CalendarEvent` - Google Calendar event data
- `EmailMessage` - Gmail message data

### API Architecture
- RESTful endpoints under `/api/v1/`
- Streaming support via Server-Sent Events
- File upload with multipart form handling
- CORS enabled for frontend integration

### Storage Strategy
- **Development**: In-memory dictionaries (`sessions_db`, `messages_db`)
- **Production**: Designed for database integration (SQLAlchemy + PostgreSQL recommended)

## Important Implementation Details

### AI Model Configuration
The system supports multiple OpenAI models with different capabilities:
- **GPT-4o**: Latest multimodal model with web search and Assistant API support
- **GPT-4**: Advanced model with web search and Assistant API support  
- **GPT-3.5-turbo**: Fast, efficient model (no web search or Assistant API)

### Assistant API Integration
Advanced AI capabilities using OpenAI's Assistant API:
- **Dynamic Assistant Creation**: Session-specific assistants with custom instructions
- **Thread Management**: Persistent conversation threads with message history
- **Tool Integration**: Seamless integration with Google services and file search
- **Vector Store Integration**: Automatic file search capabilities within conversations
- **Streaming Support**: Real-time responses via Assistant API streaming

### Function Calling System
Google services are integrated via OpenAI's Function Calling:
- Calendar operations: `get_calendar_events`, `create_calendar_event`, `find_free_time`
- Email operations: `get_emails`, `send_email`
- Natural language triggers automatically invoke appropriate functions
- Results are formatted and presented to users

### Web Search Integration
Uses OpenAI's Responses API for web search capabilities:
- Activated by `webSearch` parameter or model capability
- Provides cited sources with URLs
- Falls back to regular chat if search fails

### File Processing Pipeline
Supports multiple file types with text extraction and vector store integration:
- **PDF**: PyPDF2 for text extraction
- **DOCX**: python-docx for document processing
- **Images**: pytesseract OCR (Korean + English)
- **Text**: Direct UTF-8 processing
- **Vector Store**: Automatic integration with OpenAI Vector Stores for knowledge retrieval

### Vector Store & Knowledge Base System
Advanced document indexing and semantic search capabilities:
- **Session-specific Vector Stores**: Each chat session can maintain its own knowledge base
- **Automatic File Indexing**: Uploaded files are automatically added to vector stores
- **Semantic Search**: AI-powered content retrieval based on query similarity
- **Context-aware Responses**: Assistant API integrates vector store search results
- **Knowledge Base Management**: Create and manage document collections for enhanced AI responses

### Security Considerations
- Google credentials stored locally (not in repository)
- OpenAI API key via environment variable
- CORS configured for specific frontend origins
- No sensitive data logging

## Development Workflow

1. **Environment Setup**: Configure `.env` with OpenAI API key
2. **Google Integration**: Follow `google_setup.md` for OAuth2 setup
3. **Testing**: Use `/docs` endpoint for Swagger UI testing
4. **File Processing**: Test with various file types via `/api/v1/chat/messages/with-files`
5. **Function Calling**: Test Google integrations with natural language queries
6. **Vector Stores**: Test document indexing and search via vector store endpoints
7. **AI Tools System**: Monitor tool status via server logs or `/api/v1/tools/status` (if implemented)

### Testing Strategy
- **API Testing**: Interactive testing via Swagger UI at `localhost:8000/docs`
- **Google Services**: Test authentication flow via `/api/v1/google/auth`
- **File Upload**: Test multipart uploads with various file formats
- **Streaming**: Test real-time chat via Server-Sent Events endpoints
- **Tool Integration**: Verify tool registry initialization in server logs

## Frontend Integration Points

- **CORS Origins**: `localhost:5173`, `localhost:5174`, `localhost:3000`
- **Streaming**: Server-Sent Events at `/api/v1/chat/stream`
- **File Upload**: Multipart form at `/api/v1/chat/messages/with-files`
- **Google Auth**: OAuth flow via `/api/v1/google/auth` and `/callback`
- **Vector Stores**: Management endpoints at `/api/v1/vector-stores` and `/api/v1/sessions/{id}/vector-store`

## Key Architecture Patterns

### Service Layer Integration
- **Conditional Loading**: Google services, title generator, and AI tools load conditionally with graceful degradation
- **Registry Pattern**: AI tools use centralized registry for organization and status monitoring
- **Factory Pattern**: Dynamic assistant and thread creation based on session requirements
- **Strategy Pattern**: Different AI models with varying capabilities (web search, Assistant API)

### Error Handling Strategy
- **Graceful Degradation**: System continues functioning when optional services fail to load
- **Service Availability Checks**: Runtime validation of Google services and tool availability
- **Comprehensive Logging**: Detailed startup logs showing service initialization status
- **Fallback Mechanisms**: Alternative approaches when preferred methods are unavailable

## Migration Notes

The current implementation uses in-memory storage suitable for development. For production deployment:
- Implement database models with SQLAlchemy
- Add user authentication and authorization
- Configure proper logging and monitoring
- Implement rate limiting
- Set up proper secret management
- Consider containerization with Docker
- Implement health checks and monitoring for all integrated services