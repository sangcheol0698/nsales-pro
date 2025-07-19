from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
                response = await client.chat.completions.create(
                    model=selected_model,
                    messages=conversation_messages,
                    max_tokens=model_config["max_tokens"],
                    temperature=model_config["temperature"]
                )
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
    
    # OpenAI API에 전달할 메시지 구성
    conversation_messages = [
        {"role": "system", "content": "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요. 최신 정보가 필요하거나 실시간 데이터, 뉴스, 시장 동향 등을 질문받으면 웹 검색을 적극 활용하여 정확하고 최신의 정보를 제공하세요."}
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
            response = await client.chat.completions.create(
                model=selected_model,
                messages=conversation_messages,
                max_tokens=model_config["max_tokens"],
                temperature=model_config["temperature"]
            )
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

# 스트리밍 채팅
@app.post("/api/v1/chat/stream")
async def stream_chat(request: ChatRequest):
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
        
        # OpenAI API에 전달할 메시지 구성
        conversation_messages = [
            {"role": "system", "content": "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요. 최신 정보가 필요하거나 실시간 데이터, 뉴스, 시장 동향 등을 질문받으면 웹 검색을 적극 활용하여 정확하고 최신의 정보를 제공하세요."}
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
                # 웹 검색이 필요하지 않은 경우 일반 스트리밍 사용
                stream = await client.chat.completions.create(
                    model=selected_model,
                    messages=conversation_messages,
                    max_tokens=model_config["max_tokens"],
                    temperature=model_config["temperature"],
                    stream=True
                )
            
            # 일반 스트리밍 처리 (웹 검색 실패하거나 웹 검색이 필요하지 않은 경우)
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
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
                    await asyncio.sleep(0.01)  # 약간의 지연으로 자연스러운 스트리밍 효과
            
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