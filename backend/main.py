from fastapi import FastAPI, HTTPException, Depends
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

# .env 파일 로드
load_dotenv()


# OpenAI 클라이언트 초기화
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

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

# 앱 시작 시 데모 데이터 초기화
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_demo_data()
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
        {"role": "system", "content": "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요."}
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
    
    # OpenAI API 호출
    try:
        print(f"OpenAI API Key: {os.getenv('OPENAI_API_KEY')[:20]}...")  # 디버깅용
        print(f"Conversation length: {len(conversation_messages)} messages")  # 디버깅용
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_messages,
            max_tokens=1000,
            temperature=0.7
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
            {"role": "system", "content": "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요."}
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
            print(f"Stream conversation length: {len(conversation_messages)} messages")  # 디버깅용
            
            # OpenAI 스트리밍 API 호출
            stream = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversation_messages,
                max_tokens=1000,
                temperature=0.7,
                stream=True
            )
            
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
                        model="gpt-3.5-turbo",
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)