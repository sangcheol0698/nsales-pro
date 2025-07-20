from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
import os
from openai import AsyncOpenAI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import PyPDF2
import docx
from PIL import Image
import pytesseract
import io
import tempfile

# Google 서비스 import
try:
    from google_services import auth_service, calendar_service, gmail_service
    from google_functions import GOOGLE_TOOLS, FUNCTION_MAP
    GOOGLE_SERVICES_AVAILABLE = True
    print("✅ Google 서비스가 성공적으로 로드되었습니다.")
except ImportError as e:
    print(f"⚠️ Google 서비스 로드 실패: {e}")
    GOOGLE_SERVICES_AVAILABLE = False
    GOOGLE_TOOLS = []
    FUNCTION_MAP = {}

# .env 파일 로드
load_dotenv()


# OpenAI 클라이언트 초기화
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

# 사용 가능한 AI 모델 설정
AVAILABLE_MODELS = {
    "gpt-4o": {
        "name": "GPT-4o",
        "description": "OpenAI의 최신 멀티모달 모델",
        "provider": "openai",
        "supports_web_search": True,
        "max_tokens": 4000,
        "temperature": 0.7
    },
    "gpt-4": {
        "name": "GPT-4",
        "description": "OpenAI의 강력한 언어 모델",
        "provider": "openai", 
        "supports_web_search": True,
        "max_tokens": 4000,
        "temperature": 0.7
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "description": "빠르고 효율적인 OpenAI 모델",
        "provider": "openai",
        "supports_web_search": False,
        "max_tokens": 2000,
        "temperature": 0.7
    }
}

# 메모리 저장소 (실제 환경에서는 데이터베이스 사용)
sessions_db: Dict[str, Dict] = {}
messages_db: Dict[str, List[Dict]] = {}

# Google 서비스 도구 정의
def get_google_tools():
    """Google 서비스 함수들을 OpenAI 도구 형식으로 반환"""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_calendar_events",
                "description": "Google Calendar에서 일정을 조회합니다. 오늘, 이번주, 이번달 등의 일정을 확인할 수 있습니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_period": {
                            "type": "string",
                            "enum": ["today", "tomorrow", "this_week", "next_week", "this_month", "next_month"],
                            "description": "조회할 시간 범위"
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 10,
                            "description": "최대 조회할 일정 수"
                        }
                    },
                    "required": ["time_period"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_calendar_event",
                "description": "Google Calendar에 새로운 일정을 생성합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "일정 제목"
                        },
                        "description": {
                            "type": "string",
                            "description": "일정 설명"
                        },
                        "start_datetime": {
                            "type": "string",
                            "description": "시작 일시 (ISO 8601 형식: 2023-12-25T10:00:00)"
                        },
                        "end_datetime": {
                            "type": "string",
                            "description": "종료 일시 (ISO 8601 형식: 2023-12-25T11:00:00)"
                        },
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "참석자 이메일 목록"
                        }
                    },
                    "required": ["summary", "start_datetime", "end_datetime"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "find_free_time",
                "description": "지정된 기간 동안 빈 시간을 찾습니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "duration_minutes": {
                            "type": "integer",
                            "description": "필요한 시간 (분 단위)"
                        },
                        "date_range": {
                            "type": "string",
                            "enum": ["today", "tomorrow", "this_week", "next_week"],
                            "description": "검색할 날짜 범위"
                        },
                        "working_hours_only": {
                            "type": "boolean",
                            "default": True,
                            "description": "업무 시간(9-18시)만 검색할지 여부"
                        }
                    },
                    "required": ["duration_minutes", "date_range"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_emails",
                "description": "Gmail에서 이메일을 조회합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "검색 쿼리 (예: 'subject:회의', 'from:manager@company.com')"
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 10,
                            "description": "최대 조회할 이메일 수"
                        },
                        "time_period": {
                            "type": "string",
                            "enum": ["today", "this_week", "this_month", "all"],
                            "default": "this_week",
                            "description": "조회할 시간 범위"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": "Gmail을 통해 이메일을 발송합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "수신자 이메일 주소 목록"
                        },
                        "subject": {
                            "type": "string",
                            "description": "이메일 제목"
                        },
                        "body": {
                            "type": "string",
                            "description": "이메일 본문"
                        },
                        "cc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "참조 이메일 주소 목록"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        }
    ]

# 캘린더 일정을 표 형태로 포맷팅하는 함수
def format_calendar_events_as_table(events: List[Dict]) -> str:
    """캘린더 일정을 마크다운 표 형태로 포맷팅"""
    if not events:
        return "조회된 일정이 없습니다."
    
    # 표 헤더
    table = "## 📅 일정 목록\n\n"
    table += "| 날짜 | 시간 | 제목 | 장소 | 설명 |\n"
    table += "|------|------|------|------|------|\n"
    
    for event in events:
        # 날짜/시간 파싱
        start_time = event.get('start', '')
        summary = event.get('summary', '제목 없음')
        location = event.get('location', '-')
        description = event.get('description', '-')
        
        # 날짜와 시간 분리
        if 'T' in start_time:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                date_str = dt.strftime('%m/%d')
                time_str = dt.strftime('%H:%M')
                
                # 종료 시간도 파싱
                end_time = event.get('end', '')
                if 'T' in end_time:
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    time_str += f" - {end_dt.strftime('%H:%M')}"
            except:
                date_str = start_time[:10] if len(start_time) >= 10 else start_time
                time_str = start_time[11:16] if len(start_time) > 16 else "-"
        else:
            date_str = start_time
            time_str = "종일"
        
        # 텍스트 길이 제한 (표가 너무 길어지지 않도록)
        summary = (summary[:20] + "...") if len(summary) > 20 else summary
        location = (location[:15] + "...") if len(location) > 15 else location
        description = (description[:25] + "...") if len(description) > 25 else description
        
        # 마크다운 특수문자 이스케이프
        summary = summary.replace('|', '\\|')
        location = location.replace('|', '\\|')
        description = description.replace('|', '\\|')
        
        table += f"| {date_str} | {time_str} | {summary} | {location} | {description} |\n"
    
    table += f"\n총 **{len(events)}개**의 일정이 있습니다."
    return table

# Google 함수 실행 핸들러
async def execute_google_function(function_name: str, arguments: dict):
    """Google 함수를 실행하고 결과를 반환"""
    try:
        if not GOOGLE_SERVICES_AVAILABLE or not auth_service.is_authenticated():
            return {"error": "Google 서비스가 연결되지 않았습니다. 먼저 Google 인증을 완료해주세요."}
        
        if function_name == "get_calendar_events":
            from datetime import datetime, timedelta
            
            # time_period를 start_date, end_date로 변환
            time_period = arguments.get("time_period", "today")
            today = datetime.now().date()
            
            if time_period == "today":
                start_date = today.isoformat()
                end_date = today.isoformat()
            elif time_period == "tomorrow":
                tomorrow = today + timedelta(days=1)
                start_date = tomorrow.isoformat()
                end_date = tomorrow.isoformat()
            elif time_period == "this_week":
                # 이번 주 월요일부터 일요일까지
                days_since_monday = today.weekday()
                monday = today - timedelta(days=days_since_monday)
                sunday = monday + timedelta(days=6)
                start_date = monday.isoformat()
                end_date = sunday.isoformat()
            elif time_period == "next_week":
                # 다음 주 월요일부터 일요일까지
                days_since_monday = today.weekday()
                next_monday = today - timedelta(days=days_since_monday) + timedelta(days=7)
                next_sunday = next_monday + timedelta(days=6)
                start_date = next_monday.isoformat()
                end_date = next_sunday.isoformat()
            elif time_period == "this_month":
                # 이번 달 1일부터 말일까지
                first_day = today.replace(day=1)
                if today.month == 12:
                    last_day = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    last_day = today.replace(month=today.month+1, day=1) - timedelta(days=1)
                start_date = first_day.isoformat()
                end_date = last_day.isoformat()
            elif time_period == "next_month":
                # 다음 달 1일부터 말일까지
                if today.month == 12:
                    next_month_first = today.replace(year=today.year+1, month=1, day=1)
                    next_month_last = today.replace(year=today.year+1, month=2, day=1) - timedelta(days=1)
                else:
                    next_month_first = today.replace(month=today.month+1, day=1)
                    if today.month == 11:
                        next_month_last = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                    else:
                        next_month_last = today.replace(month=today.month+2, day=1) - timedelta(days=1)
                start_date = next_month_first.isoformat()
                end_date = next_month_last.isoformat()
            else:
                # 기본값은 오늘
                start_date = today.isoformat()
                end_date = today.isoformat()
            
            result = await calendar_service.get_events(
                start_date=start_date,
                end_date=end_date,
                max_results=arguments.get("max_results", 10)
            )
            return result
            
        elif function_name == "create_calendar_event":
            from google_services import CalendarEvent
            event_data = CalendarEvent(
                summary=arguments["summary"],
                description=arguments.get("description", ""),
                start_datetime=arguments["start_datetime"],
                end_datetime=arguments["end_datetime"],
                attendees=arguments.get("attendees", [])
            )
            result = await calendar_service.create_event(event_data)
            return result
            
        elif function_name == "find_free_time":
            result = await calendar_service.find_free_time(
                duration_minutes=arguments["duration_minutes"],
                date_range=arguments["date_range"],
                working_hours_only=arguments.get("working_hours_only", True)
            )
            return result
            
        elif function_name == "get_emails":
            result = await gmail_service.get_emails(
                query=arguments.get("query", ""),
                max_results=arguments.get("max_results", 10),
                time_period=arguments.get("time_period", "this_week")
            )
            return result
            
        elif function_name == "send_email":
            from google_services import EmailMessage
            email_data = EmailMessage(
                to=arguments["to"],
                subject=arguments["subject"],
                body=arguments["body"],
                cc=arguments.get("cc", [])
            )
            result = await gmail_service.send_email(email_data)
            return result
            
        else:
            return {"error": f"알 수 없는 함수: {function_name}"}
            
    except Exception as e:
        print(f"Google function execution error: {e}")
        return {"error": f"함수 실행 중 오류가 발생했습니다: {str(e)}"}

# Pydantic 모델들
class ChatMessage(BaseModel):
    id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime
    sessionId: str

class ChatRequest(BaseModel):
    content: str
    sessionId: str
    model: Optional[str] = "gpt-4o"  # 기본값은 gpt-4o
    webSearch: Optional[bool] = False  # 웹 검색 여부

class ChatResponse(BaseModel):
    id: str
    content: str
    role: str
    timestamp: datetime
    sessionId: str

class ChatSession(BaseModel):
    id: str
    title: str
    createdAt: datetime
    updatedAt: datetime
    messageCount: int

class SessionCreateRequest(BaseModel):
    title: Optional[str] = None

class SessionUpdateRequest(BaseModel):
    title: str

class ChatSearch(BaseModel):
    query: Optional[str] = None
    page: int = 0
    size: int = 50
    sort: Optional[str] = None

class ChatSessionList(BaseModel):
    sessions: List[ChatSession]
    totalElements: int
    totalPages: int
    currentPage: int
    size: int

class ChatHistory(BaseModel):
    messages: List[ChatMessage]
    sessionId: str
    totalCount: int

class ChatStreamChunk(BaseModel):
    id: str
    content: str
    role: str
    timestamp: datetime
    sessionId: str
    isComplete: bool = False

# 파일 처리 함수들
async def extract_text_from_pdf(file_content: bytes) -> str:
    """PDF 파일에서 텍스트 추출"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"PDF 읽기 오류: {str(e)}"

async def extract_text_from_docx(file_content: bytes) -> str:
    """DOCX 파일에서 텍스트 추출"""
    try:
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        return f"DOCX 읽기 오류: {str(e)}"

async def extract_text_from_image(file_content: bytes) -> str:
    """이미지에서 OCR로 텍스트 추출"""
    try:
        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image, lang='kor+eng')
        return text.strip() if text.strip() else "이미지에서 텍스트를 찾을 수 없습니다."
    except Exception as e:
        return f"이미지 OCR 오류: {str(e)}"

async def process_uploaded_file(file: UploadFile) -> str:
    """업로드된 파일을 처리하여 텍스트 추출"""
    try:
        file_content = await file.read()
        file_type = file.content_type.lower()
        filename = file.filename.lower()
        
        if file_type == "application/pdf" or filename.endswith('.pdf'):
            return await extract_text_from_pdf(file_content)
        elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"] or filename.endswith('.docx'):
            return await extract_text_from_docx(file_content)
        elif file_type.startswith('image/'):
            return await extract_text_from_image(file_content)
        elif file_type == "text/plain" or filename.endswith('.txt'):
            return file_content.decode('utf-8', errors='ignore')
        else:
            return f"지원하지 않는 파일 형식: {file_type}"
    except Exception as e:
        return f"파일 처리 오류: {str(e)}"

# 유틸리티 함수들
def generate_id() -> str:
    return str(uuid.uuid4())

def create_session(title: str = None) -> ChatSession:
    session_id = generate_id()
    session = ChatSession(
        id=session_id,
        title=title or f"새 채팅 {len(sessions_db) + 1}",
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        messageCount=0
    )
    
    sessions_db[session_id] = session.dict()
    messages_db[session_id] = []
    return session

def get_session(session_id: str) -> ChatSession:
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    return ChatSession(**sessions_db[session_id])

def update_session_message_count(session_id: str):
    if session_id in sessions_db:
        sessions_db[session_id]["messageCount"] = len(messages_db.get(session_id, []))
        sessions_db[session_id]["updatedAt"] = datetime.now()

# 초기 데모 데이터 생성
def initialize_demo_data():
    if not sessions_db:
        # 데모 세션 1
        demo_session_1 = create_session("영업 데이터 분석")
        messages_db[demo_session_1.id] = [
            {
                "id": generate_id(),
                "content": "이번 분기 영업 성과는 어떤가요?",
                "role": "user",
                "timestamp": datetime.now(),
                "sessionId": demo_session_1.id
            },
            {
                "id": generate_id(),
                "content": "이번 분기 영업 성과를 분석해보겠습니다. 전체적으로 목표 대비 115% 달성했으며, 특히 새로운 고객 확보 부분에서 좋은 성과를 보였습니다.",
                "role": "assistant",
                "timestamp": datetime.now(),
                "sessionId": demo_session_1.id
            }
        ]
        
        # 데모 세션 2
        demo_session_2 = create_session("프로젝트 현황 조회")
        messages_db[demo_session_2.id] = [
            {
                "id": generate_id(),
                "content": "진행 중인 프로젝트 목록을 보여주세요",
                "role": "user",
                "timestamp": datetime.now(),
                "sessionId": demo_session_2.id
            },
            {
                "id": generate_id(),
                "content": "현재 진행 중인 프로젝트는 총 12개입니다. 그 중 5개는 개발 단계, 4개는 테스트 단계, 3개는 배포 준비 단계에 있습니다.",
                "role": "assistant",
                "timestamp": datetime.now(),
                "sessionId": demo_session_2.id
            }
        ]
        
        # 데모 세션 3
        demo_session_3 = create_session("고객사 정보 문의")
        messages_db[demo_session_3.id] = []
        
        # 메시지 카운트 업데이트
        for session_id in sessions_db.keys():
            update_session_message_count(session_id)

# 앱 시작 시 데모 데이터 초기화 (비활성화)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # initialize_demo_data()  # 데모 데이터 생성 비활성화
    yield
    # Shutdown
    pass

app = FastAPI(
    title="NSales Pro Chat API",
    description="AI 채팅 서비스 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 엔드포인트들

@app.get("/")
async def root():
    return {"message": "NSales Pro Chat API", "version": "1.0.0"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/v1/models")
async def get_available_models():
    """사용 가능한 AI 모델 목록 반환"""
    return {"models": AVAILABLE_MODELS}

# Google 서비스 관련 엔드포인트
@app.get("/api/v1/google/auth")
async def google_auth():
    """Google OAuth2 인증 시작"""
    if not GOOGLE_SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Google 서비스를 사용할 수 없습니다.")
    
    auth_url = auth_service.get_authorization_url()
    if not auth_url:
        raise HTTPException(status_code=500, detail="인증 URL 생성에 실패했습니다.")
    
    return {"auth_url": auth_url}

@app.get("/api/v1/google/callback")
async def google_callback(code: str):
    """Google OAuth2 콜백 처리"""
    if not GOOGLE_SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Google 서비스를 사용할 수 없습니다.")
    
    success = auth_service.handle_callback(code)
    if success:
        return RedirectResponse(url="http://localhost:5174?google_auth=success")
    else:
        return RedirectResponse(url="http://localhost:5174?google_auth=error")

@app.get("/api/v1/google/status")
async def google_status():
    """Google 인증 상태 확인"""
    if not GOOGLE_SERVICES_AVAILABLE:
        return {"authenticated": False, "error": "Google 서비스를 사용할 수 없습니다."}
    
    return {
        "authenticated": auth_service.is_authenticated(),
        "services_available": True
    }

# 채팅 세션 관리
@app.post("/api/v1/chat/sessions", response_model=ChatSession)
async def create_chat_session(request: SessionCreateRequest):
    session = create_session(request.title)
    return session

@app.get("/api/v1/chat/sessions", response_model=ChatSessionList)
async def get_chat_sessions(search: ChatSearch = Depends()):
    sessions = list(sessions_db.values())
    
    # 검색 필터 적용
    if search.query:
        sessions = [
            s for s in sessions 
            if search.query.lower() in s["title"].lower()
        ]
    
    # 정렬 (최신순)
    sessions.sort(key=lambda x: x["updatedAt"], reverse=True)
    
    # 페이징
    total = len(sessions)
    start = search.page * search.size
    end = start + search.size
    paged_sessions = sessions[start:end]
    
    return ChatSessionList(
        sessions=[ChatSession(**s) for s in paged_sessions],
        totalElements=total,
        totalPages=(total + search.size - 1) // search.size,
        currentPage=search.page,
        size=search.size
    )

@app.get("/api/v1/chat/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(session_id: str):
    return get_session(session_id)

@app.patch("/api/v1/chat/sessions/{session_id}")
async def update_chat_session(session_id: str, request: SessionUpdateRequest):
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions_db[session_id]["title"] = request.title
    sessions_db[session_id]["updatedAt"] = datetime.now()
    return {"message": "Session updated successfully"}

@app.delete("/api/v1/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions_db[session_id]
    if session_id in messages_db:
        del messages_db[session_id]
    
    return {"message": "Session deleted successfully"}

# 메시지 관리
@app.get("/api/v1/chat/sessions/{session_id}/messages", response_model=ChatHistory)
async def get_message_history(session_id: str):
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = messages_db.get(session_id, [])
    return ChatHistory(
        messages=[ChatMessage(**msg) for msg in messages],
        sessionId=session_id,
        totalCount=len(messages)
    )

@app.post("/api/v1/chat/messages/with-files")
async def send_message_with_files(
    content: str = Form(...),
    sessionId: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    model: str = Form(default="gpt-4o")
):
    """파일 첨부를 지원하는 채팅 메시지 전송"""
    try:
        # 세션 존재 확인
        if sessionId not in sessions_db:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_messages = messages_db.get(sessionId, [])
        
        # 파일 처리
        file_contents = []
        if files:
            for file in files:
                if file.filename:  # 파일이 실제로 업로드된 경우
                    print(f"Processing file: {file.filename}, type: {file.content_type}")
                    file_text = await process_uploaded_file(file)
                    file_contents.append(f"[파일: {file.filename}]\n{file_text}")
        
        # 메시지 내용 구성 (텍스트 + 파일 내용)
        message_content = content
        if file_contents:
            message_content += "\n\n" + "\n\n".join(file_contents)
        
        # 사용자 메시지 저장
        user_message = ChatMessage(
            id=generate_id(),
            content=message_content,
            role="user",
            timestamp=datetime.now(),
            sessionId=sessionId
        )
        session_messages.append(user_message.model_dump())
        
        # OpenAI API에 전달할 메시지 구성
        conversation_messages = [
            {"role": "system", "content": "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 첨부된 파일의 내용을 분석하여 관련된 답변을 제공해주세요. 최신 정보가 필요하거나 실시간 데이터, 뉴스, 시장 동향 등을 질문받으면 웹 검색을 적극 활용하여 정확하고 최신의 정보를 제공하세요."}
        ]
        
        # 기존 대화 내용 추가 (최근 20개 메시지만 유지)
        recent_messages = session_messages[-21:] if len(session_messages) > 21 else session_messages[:-1]  # 현재 메시지 제외
        for msg in recent_messages:
            conversation_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # 현재 사용자 메시지 추가
        conversation_messages.append({"role": "user", "content": message_content})
        
        # 선택된 모델 정보 가져오기
        selected_model = model if model in AVAILABLE_MODELS else "gpt-4o"
        model_config = AVAILABLE_MODELS[selected_model]

        # OpenAI API 호출
        try:
            print(f"Using model: {selected_model} ({model_config['name']})")
            print(f"Conversation length: {len(conversation_messages)} messages")
            print(f"Files processed: {len(file_contents)}")
            
            # 웹 검색 여부는 form 데이터에서 확인
            web_search = form.get('webSearch', 'false').lower() == 'true'
            needs_web_search = web_search
            
            if needs_web_search and model_config["supports_web_search"]:
                print("🔍 Web search detected - using Responses API with web search")
                try:
                    # OpenAI Responses API를 사용한 웹 검색
                    response = await client.responses.create(
                        model=selected_model,
                        input=content,
                        tools=[
                            {
                                "type": "web_search"
                            }
                        ]
                    )
                    
                    # Extract message content from output
                    ai_content = ""
                    sources = []
                    
                    for output_item in response.output:
                        if output_item.type == 'message' and hasattr(output_item, 'content'):
                            for content_item in output_item.content:
                                if content_item.type == 'output_text':
                                    ai_content += content_item.text
                                    
                                    # Extract URL citations from annotations
                                    if hasattr(content_item, 'annotations'):
                                        for annotation in content_item.annotations:
                                            if annotation.type == 'url_citation':
                                                sources.append({
                                                    'title': getattr(annotation, 'title', ''),
                                                    'url': getattr(annotation, 'url', ''),
                                                    'snippet': ''
                                                })
                    
                    # Add sources to the content if found
                    if sources:
                        sources_text = "\n\n**참고 출처:**\n"
                        for i, source in enumerate(sources, 1):
                            sources_text += f"{i}. [{source['title']}]({source['url']})\n"
                        ai_content += sources_text
                        print(f"📚 Found {len(sources)} web search sources")
                except Exception as e:
                    print(f"Responses API error, falling back to chat completions: {e}")
                    # Responses API가 작동하지 않으면 일반 채팅으로 폴백
                    response = await client.chat.completions.create(
                        model="gpt-4o",
                        messages=conversation_messages,
                        max_tokens=1500,
                        temperature=0.7
                    )
                    ai_content = response.choices[0].message.content
            else:
                # 기본 채팅 API 호출 (Google 도구 포함)
                chat_params = {
                    "model": selected_model,
                    "messages": conversation_messages,
                    "max_tokens": model_config["max_tokens"],
                    "temperature": model_config["temperature"]
                }
                
                # Google 도구가 있으면 추가
                if available_tools:
                    chat_params["tools"] = available_tools
                    chat_params["tool_choice"] = "auto"
                    print(f"🛠️ Function Calling 활성화: {len(available_tools)}개 도구")
                    print(f"🔍 도구 목록: {[tool['function']['name'] for tool in available_tools]}")
                    print(f"🔍 요청 내용: {request.content}")
                
                response = await client.chat.completions.create(**chat_params)
                
                # Function calls가 있는지 확인
                if response.choices[0].message.tool_calls:
                    print(f"🔧 Function 호출 감지: {len(response.choices[0].message.tool_calls)}개")
                    
                    function_results = []
                    for tool_call in response.choices[0].message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        print(f"🔧 실행 중: {function_name}({function_args})")
                        result = await execute_google_function(function_name, function_args)
                        function_results.append(f"[{function_name} 결과]\n{json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    # 함수 결과를 AI 응답에 포함
                    ai_content = response.choices[0].message.content or ""
                    if function_results:
                        ai_content += "\n\n" + "\n\n".join(function_results)
                        print(f"📋 함수 실행 결과가 응답에 추가됨")
                else:
                    ai_content = response.choices[0].message.content
            
            print(f"OpenAI Response: {ai_content}")
            
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            ai_content = f"죄송합니다. 현재 AI 서비스에 일시적인 문제가 있습니다. 첨부하신 파일을 포함한 '{content}'에 대한 답변을 준비하고 있습니다. 잠시 후 다시 시도해주세요."
        
        # AI 응답 저장
        ai_message = ChatMessage(
            id=generate_id(),
            content=ai_content,
            role="assistant",
            timestamp=datetime.now(),
            sessionId=sessionId
        )
        session_messages.append(ai_message.model_dump())
        
        # 메시지 저장
        messages_db[sessionId] = session_messages
        
        # 세션 업데이트
        sessions_db[sessionId]["messageCount"] = len(session_messages)
        sessions_db[sessionId]["updatedAt"] = datetime.now()
        
        return {
            "userMessage": user_message,
            "aiMessage": ai_message,
            "success": True
        }
        
    except Exception as e:
        print(f"Error in send_message_with_files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat/messages", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    if request.sessionId not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 사용자 메시지 저장
    user_message = ChatMessage(
        id=generate_id(),
        content=request.content,
        role="user",
        timestamp=datetime.now(),
        sessionId=request.sessionId
    )
    
    if request.sessionId not in messages_db:
        messages_db[request.sessionId] = []
    
    messages_db[request.sessionId].append(user_message.dict())
    
    # 세션의 기존 메시지 히스토리 가져오기
    session_messages = messages_db.get(request.sessionId, [])
    
    # Google 서비스 사용 안내를 포함한 시스템 프롬프트 구성
    system_prompt = "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요. 최신 정보가 필요하거나 실시간 데이터, 뉴스, 시장 동향 등을 질문받으면 웹 검색을 적극 활용하여 정확하고 최신의 정보를 제공하세요."
    
    # 멘션 기반 서비스 활성화 로직
    mention_detected = False
    google_mention_keywords = ['@캘린더', '@메일', '@일정생성', '@빈시간']
    
    for keyword in google_mention_keywords:
        if keyword in request.content:
            mention_detected = True
            break
    
    # Google 서비스가 사용 가능하고 멘션이 감지된 경우 안내 추가
    if GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated() and mention_detected:
        system_prompt += "\n\n**🎯 Google 서비스 멘션 감지됨:**\n사용자가 @멘션을 사용했습니다. 다음 함수를 반드시 호출하여 요청을 처리하세요:\n- @캘린더 → get_calendar_events 함수 호출\n- @메일 → get_emails 또는 send_email 함수 호출\n- @일정생성 → create_calendar_event 함수 호출\n- @빈시간 → find_free_time 함수 호출\n\n멘션이 포함된 요청은 반드시 해당 함수를 실행하여 실제 데이터를 제공해야 합니다."
    elif GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated():
        system_prompt += "\n\n**Google 서비스 연동 안내:**\n사용자가 캘린더, 일정, 스케줄, Gmail, 이메일 관련 질문을 하면 다음 함수들을 적극 활용하세요:\n- get_calendar_events: 캘린더 일정 조회 (오늘, 이번주, 이번달 등)\n- create_calendar_event: 새 일정 생성\n- send_email: 이메일 전송\n- get_emails: 이메일 조회\n- find_free_time: 빈 시간 찾기\n\n사용자가 '캘린더', '일정', '스케줄' 등의 키워드를 사용하면 반드시 해당 함수를 호출하여 실제 데이터를 제공하세요."
    
    # OpenAI API에 전달할 메시지 구성
    conversation_messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # 기존 대화 내용 추가 (최근 10개 메시지만 유지하여 토큰 절약)
    recent_messages = session_messages[-20:] if len(session_messages) > 20 else session_messages
    for msg in recent_messages:
        conversation_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # 현재 사용자 메시지 추가
    conversation_messages.append({"role": "user", "content": request.content})
    
    # 선택된 모델 정보 가져오기
    selected_model = request.model if request.model in AVAILABLE_MODELS else "gpt-4o"
    model_config = AVAILABLE_MODELS[selected_model]
    
    # 사용 가능한 도구 목록 구성
    available_tools = []
    if GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated():
        available_tools.extend(get_google_tools())
        print(f"🛠️ Google 도구 {len(get_google_tools())}개 추가됨")
    
    # OpenAI API 호출
    try:
        print(f"Using model: {selected_model} ({model_config['name']})")
        print(f"OpenAI API Key: {os.getenv('OPENAI_API_KEY')[:20]}...")  # 디버깅용
        print(f"Conversation length: {len(conversation_messages)} messages")  # 디버깅용
        
        # 웹 검색 여부는 요청에서 확인
        needs_web_search = getattr(request, 'webSearch', False)
        search_content = request.content
        
        # 웹 검색은 지원하는 모델에서만 가능
        if needs_web_search and model_config["supports_web_search"]:
            print("🔍 Web search detected - using Responses API with web search")
            try:
                # OpenAI Responses API를 사용한 웹 검색
                response = await client.responses.create(
                    model=selected_model,
                    input=search_content,
                    tools=[
                        {
                            "type": "web_search"
                        }
                    ]
                )
                
                # Extract message content from output
                ai_content = ""
                sources = []
                
                for output_item in response.output:
                    if output_item.type == 'message' and hasattr(output_item, 'content'):
                        for content_item in output_item.content:
                            if content_item.type == 'output_text':
                                ai_content += content_item.text
                                
                                # Extract URL citations from annotations
                                if hasattr(content_item, 'annotations'):
                                    for annotation in content_item.annotations:
                                        if annotation.type == 'url_citation':
                                            sources.append({
                                                'title': getattr(annotation, 'title', ''),
                                                'url': getattr(annotation, 'url', ''),
                                                'snippet': ''
                                            })
                
                # Add sources to the content if found
                if sources:
                    sources_text = "\n\n**참고 출처:**\n"
                    for i, source in enumerate(sources, 1):
                        sources_text += f"{i}. [{source['title']}]({source['url']})\n"
                    ai_content += sources_text
                    print(f"📚 Found {len(sources)} web search sources")
            except Exception as e:
                print(f"Responses API error, falling back to chat completions: {e}")
                # Responses API가 작동하지 않으면 일반 채팅으로 폴백
                response = await client.chat.completions.create(
                    model=selected_model,
                    messages=conversation_messages,
                    max_tokens=model_config["max_tokens"],
                    temperature=model_config["temperature"]
                )
                ai_content = response.choices[0].message.content
        else:
            # 기본 채팅 API 호출 (Google 도구 포함)
            chat_params = {
                "model": selected_model,
                "messages": conversation_messages,
                "max_tokens": model_config["max_tokens"],
                "temperature": model_config["temperature"]
            }
            
            # Google 도구가 있으면 추가
            if available_tools:
                chat_params["tools"] = available_tools
                chat_params["tool_choice"] = "auto"
                print(f"🛠️ Function Calling 활성화: {len(available_tools)}개 도구")
                print(f"🔍 도구 목록: {[tool['function']['name'] for tool in available_tools]}")
                print(f"🔍 요청 내용: {request.content}")
            
            response = await client.chat.completions.create(**chat_params)
            
            # Function calls가 있는지 확인
            if response.choices[0].message.tool_calls:
                print(f"🔧 Function 호출 감지: {len(response.choices[0].message.tool_calls)}개")
                
                function_results = []
                for tool_call in response.choices[0].message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 실행 중: {function_name}({function_args})")
                    result = await execute_google_function(function_name, function_args)
                    function_results.append(f"[{function_name} 결과]\n{json.dumps(result, ensure_ascii=False, indent=2)}")
                
                # 함수 결과가 있으면 AI가 해석하도록 처리
                if function_results:
                    # 첫 번째 함수 결과만 사용 (여러 함수 호출시 고려 필요)
                    first_tool_call = response.choices[0].message.tool_calls[0]
                    first_result = await execute_google_function(first_tool_call.function.name, json.loads(first_tool_call.function.arguments))
                    
                    # 결과가 빈 리스트이면 적절한 메시지로 변환
                    if isinstance(first_result, list) and len(first_result) == 0:
                        if first_tool_call.function.name == "get_calendar_events":
                            ai_content = "해당 기간에 예정된 일정이 없습니다. 자유로운 시간을 보내세요! 😊"
                        else:
                            ai_content = "조회된 결과가 없습니다."
                    elif "error" in str(first_result):
                        ai_content = f"죄송합니다. {first_tool_call.function.name} 실행 중 문제가 발생했습니다: {first_result.get('error', str(first_result))}"
                    else:
                        # 캘린더 일정은 표 형태로 포맷팅
                        if first_tool_call.function.name == "get_calendar_events" and isinstance(first_result, list):
                            ai_content = format_calendar_events_as_table(first_result)
                        else:
                            # 다른 함수는 기본 JSON 형태
                            ai_content = f"{response.choices[0].message.content or ''}\n\n조회 결과:\n{json.dumps(first_result, ensure_ascii=False, indent=2)}"
                    
                    print(f"📋 함수 결과 해석 완료: {first_tool_call.function.name}")
                else:
                    ai_content = response.choices[0].message.content or ""
            else:
                ai_content = response.choices[0].message.content
        
        print(f"OpenAI Response: {ai_content}")  # 디버깅용
        
    except Exception as e:
        # OpenAI API 오류 시 폴백 응답
        print(f"OpenAI API Error: {e}")  # 디버깅용
        ai_content = f"죄송합니다. 현재 AI 서비스에 일시적인 문제가 있습니다. '{request.content}'에 대한 답변을 준비하고 있습니다. 잠시 후 다시 시도해주세요."
    
    # AI 응답 저장
    ai_message = ChatMessage(
        id=generate_id(),
        content=ai_content,
        role="assistant",
        timestamp=datetime.now(),
        sessionId=request.sessionId
    )
    
    messages_db[request.sessionId].append(ai_message.dict())
    update_session_message_count(request.sessionId)
    
    return ChatResponse(**ai_message.dict())

# 스트리밍 채팅 (임시로 일반 API 사용)
@app.post("/api/v1/chat/stream")
async def stream_chat(request: ChatRequest):
    """스트리밍 채팅 API - 임시로 일반 API로 폴백"""
    try:
        # 일반 API로 처리
        response = await send_message(request)
        
        # 응답을 스트리밍 형태로 변환
        content = response.content  # response.aiMessage.content가 아니라 response.content
        session_id = request.sessionId
        message_id = response.id  # response.aiMessage.id가 아니라 response.id
        
        async def generate_stream():
            # 문자별로 스트리밍
            for i, char in enumerate(content):
                chunk = ChatStreamChunk(
                    id=message_id,
                    content=char,
                    role="assistant",
                    timestamp=datetime.now(),
                    sessionId=session_id,
                    isComplete=i == len(content) - 1
                )
                yield f"data: {chunk.json()}\n\n"
                await asyncio.sleep(0.01)
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
    except Exception as e:
        print(f"Streaming error: {e}")
        # 에러 발생시 폴백 응답
        error_chunk = ChatStreamChunk(
            id="error",
            content="죄송합니다. 현재 AI 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요.",
            role="assistant",
            timestamp=datetime.now(),
            sessionId=request.sessionId,
            isComplete=True
        )
        
        async def error_stream():
            yield f"data: {error_chunk.json()}\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )

# 원래 스트리밍 함수 (임시 비활성화)
@app.post("/api/v1/chat/stream_disabled")
async def stream_chat_original(request: ChatRequest):
    if request.sessionId not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 사용자 메시지 저장
    user_message = ChatMessage(
        id=generate_id(),
        content=request.content,
        role="user",
        timestamp=datetime.now(),
        sessionId=request.sessionId
    )
    
    if request.sessionId not in messages_db:
        messages_db[request.sessionId] = []
    
    messages_db[request.sessionId].append(user_message.dict())
    
    async def generate_stream():
        ai_message_id = generate_id()
        full_content = ""
        
        # 세션의 기존 메시지 히스토리 가져오기
        session_messages = messages_db.get(request.sessionId, [])
        
        # Google 서비스 사용 안내를 포함한 시스템 프롬프트 구성
        system_prompt = "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요. 최신 정보가 필요하거나 실시간 데이터, 뉴스, 시장 동향 등을 질문받으면 웹 검색을 적극 활용하여 정확하고 최신의 정보를 제공하세요."
        
        # 멘션 기반 서비스 활성화 로직
        mention_detected = False
        google_mention_keywords = ['@캘린더', '@메일', '@일정생성', '@빈시간']
        
        for keyword in google_mention_keywords:
            if keyword in request.content:
                mention_detected = True
                break
        
        # Google 서비스가 사용 가능하고 멘션이 감지된 경우 안내 추가
        if GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated() and mention_detected:
            system_prompt += "\n\n**🎯 Google 서비스 멘션 감지됨:**\n사용자가 @멘션을 사용했습니다. 다음 함수를 반드시 호출하여 요청을 처리하세요:\n- @캘린더 → get_calendar_events 함수 호출\n- @메일 → get_emails 또는 send_email 함수 호출\n- @일정생성 → create_calendar_event 함수 호출\n- @빈시간 → find_free_time 함수 호출\n\n멘션이 포함된 요청은 반드시 해당 함수를 실행하여 실제 데이터를 제공해야 합니다."
        elif GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated():
            system_prompt += "\n\n**Google 서비스 연동 안내:**\n사용자가 캘린더, 일정, 스케줄, Gmail, 이메일 관련 질문을 하면 다음 함수들을 적극 활용하세요:\n- get_calendar_events: 캘린더 일정 조회 (오늘, 이번주, 이번달 등)\n- create_calendar_event: 새 일정 생성\n- send_email: 이메일 전송\n- get_emails: 이메일 조회\n- find_free_time: 빈 시간 찾기\n\n사용자가 '캘린더', '일정', '스케줄' 등의 키워드를 사용하면 반드시 해당 함수를 호출하여 실제 데이터를 제공하세요."
        
        # OpenAI API에 전달할 메시지 구성
        conversation_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 기존 대화 내용 추가 (최근 20개 메시지만 유지하여 토큰 절약)
        recent_messages = session_messages[-20:] if len(session_messages) > 20 else session_messages
        for msg in recent_messages:
            conversation_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # 현재 사용자 메시지 추가
        conversation_messages.append({"role": "user", "content": request.content})
        
        try:
            # 선택된 모델 정보 가져오기
            selected_model = request.model if request.model in AVAILABLE_MODELS else "gpt-4o"
            model_config = AVAILABLE_MODELS[selected_model]
            
            print(f"Stream using model: {selected_model} ({model_config['name']})")
            print(f"Stream conversation length: {len(conversation_messages)} messages")  # 디버깅용
            
            # 사용 가능한 도구 목록 구성
            available_tools = []
            
            # 웹 검색 도구 추가
            if needs_web_search and model_config["supports_web_search"]:
                available_tools.append({"type": "web_search"})
            
            # Google 서비스 도구 추가 (인증된 경우만)
            if GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated():
                available_tools.extend(GOOGLE_TOOLS)
                print(f"🔗 Google 서비스 도구 {len(GOOGLE_TOOLS)}개 추가됨")
            
            # 웹 검색 여부는 프론트엔드에서 결정 (webSearch 파라미터로 전달)
            needs_web_search = getattr(request, 'webSearch', False)
            search_content = request.content
            
            if needs_web_search and model_config["supports_web_search"]:
                print("🔍 Web search detected in stream - using Responses API")
                try:
                    # 웹 검색이 필요한 경우 스트리밍 대신 일반 응답 사용
                    response = await client.responses.create(
                        model=selected_model,
                        input=search_content,
                        tools=[
                            {
                                "type": "web_search"
                            }
                        ]
                    )
                    
                    # Extract message content from output
                    ai_content = ""
                    sources = []
                    
                    for output_item in response.output:
                        if output_item.type == 'message' and hasattr(output_item, 'content'):
                            for content_item in output_item.content:
                                if content_item.type == 'output_text':
                                    ai_content += content_item.text
                                    
                                    # Extract URL citations from annotations
                                    if hasattr(content_item, 'annotations'):
                                        for annotation in content_item.annotations:
                                            if annotation.type == 'url_citation':
                                                sources.append({
                                                    'title': getattr(annotation, 'title', ''),
                                                    'url': getattr(annotation, 'url', ''),
                                                    'snippet': ''
                                                })
                    
                    # Add sources to the content if found
                    if sources:
                        sources_text = "\n\n**참고 출처:**\n"
                        for i, source in enumerate(sources, 1):
                            sources_text += f"{i}. [{source['title']}]({source['url']})\n"
                        ai_content += sources_text
                        print(f"📚 Found {len(sources)} web search sources in stream")
                    
                    full_content = ai_content
                    
                    # 웹 검색 결과를 자연스럽게 스트리밍
                    import re
                    
                    # 문자별로 스트리밍 (더 자연스럽게)
                    for i, char in enumerate(ai_content):
                        stream_chunk = ChatStreamChunk(
                            id=ai_message_id,
                            content=char,
                            role="assistant",
                            timestamp=datetime.now(),
                            sessionId=request.sessionId,
                            isComplete=False
                        )
                        yield f"data: {stream_chunk.json()}\n\n"
                        
                        # 문자 유형에 따른 적응적 지연
                        if char in ".!?":
                            await asyncio.sleep(0.15)  # 문장 끝
                        elif char in ",;:":
                            await asyncio.sleep(0.08)  # 문장 중간
                        elif char == '\n':
                            await asyncio.sleep(0.12)  # 줄바꿈
                        elif char == ' ':
                            await asyncio.sleep(0.03)  # 공백
                        elif char in "()[]{}":
                            await asyncio.sleep(0.05)  # 괄호
                        else:
                            await asyncio.sleep(0.02)  # 일반 문자
                    
                    # 웹 검색 스트리밍 완료 신호
                    final_chunk = ChatStreamChunk(
                        id=ai_message_id,
                        content="",
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=request.sessionId,
                        isComplete=True
                    )
                    yield f"data: {final_chunk.json()}\\n\\n"
                    
                    # 웹 검색 성공 시 여기서 return
                    # AI 응답 저장
                    ai_message = ChatMessage(
                        id=ai_message_id,
                        content=full_content,
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=request.sessionId
                    )
                    
                    messages_db[request.sessionId].append(ai_message.dict())
                    update_session_message_count(request.sessionId)
                    return
                        
                except Exception as web_error:
                    print(f"Responses API error in stream, falling back to chat completions: {web_error}")
                    # 웹 검색 실패 시 일반 스트리밍으로 폴백
                    stream = await client.chat.completions.create(
                        model=selected_model,
                        messages=conversation_messages,
                        max_tokens=model_config["max_tokens"],
                        temperature=model_config["temperature"],
                        stream=True
                    )
            else:
                # 임시로 스트리밍 대신 일반 API 사용
                chat_params = {
                    "model": selected_model,
                    "messages": conversation_messages,
                    "max_tokens": model_config["max_tokens"],
                    "temperature": model_config["temperature"]
                }
                
                # Google 도구가 있으면 추가
                if available_tools and not needs_web_search:
                    chat_params["tools"] = available_tools
                    chat_params["tool_choice"] = "auto"
                    print(f"🛠️ Function Calling 활성화: {len(available_tools)}개 도구")
                
                print(f"🔍 비스트리밍 파라미터: {chat_params}")
                response = await client.chat.completions.create(**chat_params)
                
                # 응답을 스트리밍 형태로 변환
                ai_content = response.choices[0].message.content
                
                # Function calls가 있는지 확인
                if response.choices[0].message.tool_calls:
                    print(f"🔧 Function 호출 감지: {len(response.choices[0].message.tool_calls)}개")
                    
                    for tool_call in response.choices[0].message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        if function_name in FUNCTION_MAP:
                            try:
                                # 함수 실행 상태 표시
                                status_content = f"\n\n🔄 {function_name} 실행 중...\n"
                                for char in status_content:
                                    status_chunk = ChatStreamChunk(
                                        id=ai_message_id,
                                        content=char,
                                        role="assistant",
                                        timestamp=datetime.now(),
                                        sessionId=request.sessionId,
                                        isComplete=False
                                    )
                                    yield f"data: {status_chunk.json()}\n\n"
                                    await asyncio.sleep(0.02)
                                
                                # 함수 실행
                                function_result = await FUNCTION_MAP[function_name](**function_args)
                                
                                # 결과를 스트리밍으로 출력
                                result_content = f"✅ 결과:\n{function_result}\n\n"
                                ai_content += result_content
                                
                                for char in result_content:
                                    result_chunk = ChatStreamChunk(
                                        id=ai_message_id,
                                        content=char,
                                        role="assistant",
                                        timestamp=datetime.now(),
                                        sessionId=request.sessionId,
                                        isComplete=False
                                    )
                                    yield f"data: {result_chunk.json()}\n\n"
                                    await asyncio.sleep(0.02)
                                    
                            except Exception as e:
                                error_content = f"❌ {function_name} 실행 오류: {str(e)}\n\n"
                                ai_content += error_content
                                
                                for char in error_content:
                                    error_chunk = ChatStreamChunk(
                                        id=ai_message_id,
                                        content=char,
                                        role="assistant",
                                        timestamp=datetime.now(),
                                        sessionId=request.sessionId,
                                        isComplete=False
                                    )
                                    yield f"data: {error_chunk.json()}\n\n"
                                    await asyncio.sleep(0.02)
                else:
                    # 일반 응답을 문자별로 스트리밍
                    for char in ai_content:
                        stream_chunk = ChatStreamChunk(
                            id=ai_message_id,
                            content=char,
                            role="assistant",
                            timestamp=datetime.now(),
                            sessionId=request.sessionId,
                            isComplete=False
                        )
                        yield f"data: {stream_chunk.json()}\n\n"
                        await asyncio.sleep(0.02)
                
                full_content = ai_content
                
                # 완료 신호
                final_chunk = ChatStreamChunk(
                    id=ai_message_id,
                    content="",
                    role="assistant",
                    timestamp=datetime.now(),
                    sessionId=request.sessionId,
                    isComplete=True
                )
                yield f"data: {final_chunk.json()}\n\n"
                
                # AI 응답 저장
                ai_message = ChatMessage(
                    id=ai_message_id,
                    content=full_content,
                    role="assistant",
                    timestamp=datetime.now(),
                    sessionId=request.sessionId
                )
                
                messages_db[request.sessionId].append(ai_message.dict())
                update_session_message_count(request.sessionId)
                return
            
            # 일반 스트리밍 처리 (웹 검색 실패하거나 웹 검색이 필요하지 않은 경우)
            tool_calls = []
            current_tool_call = None
            
            async for chunk in stream:
                delta = chunk.choices[0].delta
                
                # Function calling 처리
                if delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        if tool_call_delta.index == 0:
                            if current_tool_call is None:
                                current_tool_call = {
                                    "id": tool_call_delta.id or "",
                                    "function": {
                                        "name": tool_call_delta.function.name or "",
                                        "arguments": tool_call_delta.function.arguments or ""
                                    }
                                }
                            else:
                                if tool_call_delta.function.arguments:
                                    current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments
                
                # 일반 텍스트 응답 처리
                elif delta.content:
                    content = delta.content
                    full_content += content
                
                    stream_chunk = ChatStreamChunk(
                        id=ai_message_id,
                        content=content,
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=request.sessionId,
                        isComplete=False
                    )
                    
                    yield f"data: {stream_chunk.json()}\n\n"
                    await asyncio.sleep(0.01)
                
                # 스트림 완료 체크
                if chunk.choices[0].finish_reason == "tool_calls" and current_tool_call:
                    tool_calls.append(current_tool_call)
            
            # Function 호출 실행
            if tool_calls:
                print(f"🔧 Function 호출 실행: {len(tool_calls)}개")
                
                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    
                    if function_name in FUNCTION_MAP:
                        try:
                            # 함수 실행 상태 표시
                            status_chunk = ChatStreamChunk(
                                id=ai_message_id,
                                content=f"\n\n🔄 {function_name} 실행 중...\n",
                                role="assistant",
                                timestamp=datetime.now(),
                                sessionId=request.sessionId,
                                isComplete=False
                            )
                            yield f"data: {status_chunk.json()}\n\n"
                            
                            # 함수 실행
                            function_result = await FUNCTION_MAP[function_name](**function_args)
                            
                            # 결과를 스트리밍으로 출력
                            result_content = f"✅ 결과:\n{function_result}\n\n"
                            full_content += result_content
                            
                            for char in result_content:
                                result_chunk = ChatStreamChunk(
                                    id=ai_message_id,
                                    content=char,
                                    role="assistant",
                                    timestamp=datetime.now(),
                                    sessionId=request.sessionId,
                                    isComplete=False
                                )
                                yield f"data: {result_chunk.json()}\n\n"
                                await asyncio.sleep(0.02)
                                
                        except Exception as e:
                            error_content = f"❌ {function_name} 실행 오류: {str(e)}\n\n"
                            full_content += error_content
                            
                            for char in error_content:
                                error_chunk = ChatStreamChunk(
                                    id=ai_message_id,
                                    content=char,
                                    role="assistant",
                                    timestamp=datetime.now(),
                                    sessionId=request.sessionId,
                                    isComplete=False
                                )
                                yield f"data: {error_chunk.json()}\n\n"
                                await asyncio.sleep(0.02)
            
            # 완료 신호
            final_chunk = ChatStreamChunk(
                id=ai_message_id,
                content="",
                role="assistant",
                timestamp=datetime.now(),
                sessionId=request.sessionId,
                isComplete=True
            )
            yield f"data: {final_chunk.json()}\n\n"
            
        except Exception as e:
            # OpenAI API 오류 시 폴백 응답
            print(f"🚨 스트리밍 API 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            fallback_content = f"죄송합니다. 현재 AI 서비스에 일시적인 문제가 있습니다. '{request.content}'에 대한 답변을 준비하고 있습니다. 잠시 후 다시 시도해주세요."
            full_content = fallback_content
            
            # 폴백 응답을 단어 단위로 스트리밍
            words = fallback_content.split()
            for i, word in enumerate(words):
                stream_chunk = ChatStreamChunk(
                    id=ai_message_id,
                    content=word + " ",
                    role="assistant",
                    timestamp=datetime.now(),
                    sessionId=request.sessionId,
                    isComplete=i == len(words) - 1
                )
                yield f"data: {stream_chunk.json()}\n\n"
                await asyncio.sleep(0.1)
        
        # AI 응답 저장
        ai_message = ChatMessage(
            id=ai_message_id,
            content=full_content,
            role="assistant",
            timestamp=datetime.now(),
            sessionId=request.sessionId
        )
        
        messages_db[request.sessionId].append(ai_message.dict())
        update_session_message_count(request.sessionId)
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Nginx 버퍼링 비활성화
        }
    )

@app.delete("/api/v1/chat/messages/{message_id}")
async def delete_message(message_id: str):
    for session_id, messages in messages_db.items():
        for i, msg in enumerate(messages):
            if msg["id"] == message_id:
                del messages[i]
                update_session_message_count(session_id)
                return {"message": "Message deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Message not found")

@app.post("/api/v1/chat/messages/{message_id}/regenerate", response_model=ChatResponse)
async def regenerate_message(message_id: str):
    for session_id, messages in messages_db.items():
        for i, msg in enumerate(messages):
            if msg["id"] == message_id and msg["role"] == "assistant":
                # 이전 사용자 메시지 찾기
                user_message = None
                if i > 0:
                    user_message = messages[i-1]
                
                if not user_message:
                    raise HTTPException(status_code=400, detail="Cannot regenerate: no previous user message found")
                
                try:
                    # 세션의 기존 메시지 히스토리 가져오기 (재생성할 메시지 제외)
                    session_messages = messages_db.get(session_id, [])
                    
                    # OpenAI API에 전달할 메시지 구성
                    conversation_messages = [
                        {"role": "system", "content": "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요."}
                    ]
                    
                    # 재생성할 메시지 이전까지의 대화 내용 추가
                    for j, msg in enumerate(session_messages):
                        if j >= i:  # 재생성할 메시지부터는 제외
                            break
                        conversation_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    # 사용자 메시지 추가
                    conversation_messages.append({"role": "user", "content": user_message["content"]})
                    
                    # OpenAI API 호출
                    response = await client.chat.completions.create(
                        model="gpt-4o",
                        messages=conversation_messages,
                        max_tokens=1000,
                        temperature=0.8  # 더 다양한 응답을 위해 temperature 증가
                    )
                    
                    new_content = response.choices[0].message.content
                    
                except Exception as e:
                    # OpenAI API 오류 시 폴백 응답
                    new_content = f"죄송합니다. 다시 생성하는 중 문제가 발생했습니다. '{user_message['content']}'에 대한 새로운 답변을 준비하고 있습니다."
                
                # 새로운 응답으로 교체
                new_message = ChatMessage(
                    id=generate_id(),
                    content=new_content,
                    role="assistant",
                    timestamp=datetime.now(),
                    sessionId=session_id
                )
                
                messages[i] = new_message.dict()
                update_session_message_count(session_id)
                
                return ChatResponse(**new_message.dict())
    
    raise HTTPException(status_code=404, detail="Message not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)