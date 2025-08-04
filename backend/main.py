from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime, timezone, timedelta
import os
from openai import AsyncOpenAI
import openai  # 에러 처리용
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import PyPDF2
import docx
from PIL import Image
import pytesseract
import io
import tempfile
import logging
import base64

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

# Title Generator import
try:
    from title_generator import TitleGenerator
    TITLE_GENERATOR_AVAILABLE = True
    print("✅ Title Generator가 성공적으로 로드되었습니다.")
except ImportError as e:
    print(f"⚠️ Title Generator 로드 실패: {e}")
    TITLE_GENERATOR_AVAILABLE = False

# 새로운 AI Tools 시스템 import
try:
    from tools.manager import tool_manager

    TOOLS_SYSTEM_AVAILABLE = True
    print("✅ AI Tools 시스템이 성공적으로 로드되었습니다.")
    print(f"📊 등록된 도구 상태: {tool_manager.get_status()}")
except ImportError as e:
    print(f"⚠️ AI Tools 시스템 로드 실패: {e}")
    TOOLS_SYSTEM_AVAILABLE = False
    tool_manager = None

# .env 파일 로드
load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# OpenAI 클라이언트 초기화
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

# Title Generator 초기화
title_generator = None
if TITLE_GENERATOR_AVAILABLE:
    title_generator = TitleGenerator(client)

# 사용 가능한 AI 모델 설정
AVAILABLE_MODELS = {
    "gpt-4o": {
        "name": "GPT-4o",
        "description": "OpenAI의 최신 멀티모달 모델",
        "provider": "openai",
        "supports_web_search": True,
        "supports_assistant": True,
        "max_tokens": 4000,
        "temperature": 0.7
    },
    "gpt-4": {
        "name": "GPT-4",
        "description": "OpenAI의 강력한 언어 모델",
        "provider": "openai",
        "supports_web_search": True,
        "supports_assistant": True,
        "max_tokens": 4000,
        "temperature": 0.7
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "description": "빠르고 효율적인 OpenAI 모델",
        "provider": "openai",
        "supports_web_search": False,
        "supports_assistant": False,
        "max_tokens": 2000,
        "temperature": 0.7
    }
}

# 메모리 저장소 (실제 환경에서는 데이터베이스 사용)
sessions_db: Dict[str, Dict] = {}
messages_db: Dict[str, List[Dict]] = {}
assistants_db: Dict[str, str] = {}  # session_id -> assistant_id 매핑
threads_db: Dict[str, str] = {}  # session_id -> thread_id 매핑

# 📊 토큰 관리 및 최적화
token_usage_db: Dict[str, Dict] = {}  # session_id -> token usage stats
conversation_summaries: Dict[str, str] = {}  # session_id -> summary

# 토큰 사용량 추적 설정
MAX_CONVERSATION_TOKENS = 8000  # 대화당 최대 토큰
SUMMARY_TRIGGER_TOKENS = 6000  # 요약 트리거 토큰
MAX_MESSAGES_PER_SESSION = 50  # 세션당 최대 메시지

# 🗂️ 벡터 스토어 및 지식 베이스 관리
vector_stores_db: Dict[str, str] = {}  # session_id -> vector_store_id 매핑
knowledge_base_id: str = None  # 전역 지식 베이스 벡터 스토어 ID


# ===========================
# 🗂️ 벡터 스토어 기능 구현
# ===========================

async def create_or_get_vector_store(session_id: str = None, name: str = None) -> str:
    """세션별 벡터 스토어 생성 또는 기존 벡터 스토어 반환"""
    try:
        # 세션별 벡터 스토어 확인
        if session_id and session_id in vector_stores_db:
            return vector_stores_db[session_id]

        # 새 벡터 스토어 생성
        vector_store_name = name or f"Session Vector Store {session_id or 'Global'}"
        vector_store = await client.beta.vector_stores.create(
            name=vector_store_name,
            file_ids=[],  # 초기에는 빈 상태로 생성
            metadata={
                "session_id": session_id or "global",
                "created_at": datetime.now().isoformat(),
                "purpose": "knowledge_base"
            }
        )

        # 벡터 스토어 ID 저장
        vector_store_id = vector_store.id
        if session_id:
            vector_stores_db[session_id] = vector_store_id
        else:
            global knowledge_base_id
            knowledge_base_id = vector_store_id

        logger.info(f"✅ Vector store created: {vector_store_id} for session: {session_id}")
        return vector_store_id

    except Exception as e:
        logger.error(f"❌ Vector store creation failed: {str(e)}")
        raise


async def add_file_to_vector_store(vector_store_id: str, file_id: str) -> bool:
    """벡터 스토어에 파일 추가"""
    try:
        # 파일을 벡터 스토어에 추가
        vector_store_file = await client.beta.vector_stores.files.create_and_poll(
            vector_store_id=vector_store_id,
            file_id=file_id
        )

        logger.info(f"✅ File {file_id} added to vector store {vector_store_id}")
        return vector_store_file.status == "completed"

    except Exception as e:
        logger.error(f"❌ Failed to add file to vector store: {str(e)}")
        return False


async def search_vector_store(vector_store_id: str, query: str, limit: int = 5) -> List[Dict]:
    """벡터 스토어에서 유사한 문서 검색"""
    try:
        # 벡터 스토어에서 검색 수행
        search_results = await client.beta.vector_stores.search(
            vector_store_id=vector_store_id,
            query=query,
            limit=limit
        )

        # 검색 결과 포맷팅
        formatted_results = []
        for result in search_results.data:
            formatted_results.append({
                "content": result.content if hasattr(result, 'content') else "",
                "score": result.score if hasattr(result, 'score') else 0.0,
                "file_id": result.file_id if hasattr(result, 'file_id') else "",
                "metadata": result.metadata if hasattr(result, 'metadata') else {}
            })

        logger.info(f"✅ Vector search completed: {len(formatted_results)} results")
        return formatted_results

    except Exception as e:
        logger.error(f"❌ Vector store search failed: {str(e)}")
        return []


async def create_knowledge_base_embeddings(documents: List[str], session_id: str = None) -> str:
    """문서들을 임베딩하여 지식 베이스 생성"""
    try:
        # 벡터 스토어 생성 또는 가져오기
        vector_store_id = await create_or_get_vector_store(session_id, "Knowledge Base")

        # 각 문서를 파일로 업로드하고 벡터 스토어에 추가
        uploaded_files = []
        for i, document in enumerate(documents):
            # 임시 파일 생성
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            temp_file.write(document)
            temp_file.close()

            try:
                # OpenAI Files API로 업로드
                with open(temp_file.name, 'rb') as f:
                    file_object = await client.files.create(
                        file=f,
                        purpose="assistants"
                    )

                # 벡터 스토어에 추가
                if await add_file_to_vector_store(vector_store_id, file_object.id):
                    uploaded_files.append(file_object.id)

            finally:
                # 임시 파일 삭제
                try:
                    os.unlink(temp_file.name)
                except:
                    pass

        logger.info(f"✅ Knowledge base created with {len(uploaded_files)} documents")
        return vector_store_id

    except Exception as e:
        logger.error(f"❌ Knowledge base creation failed: {str(e)}")
        raise


async def get_relevant_context(query: str, session_id: str = None) -> str:
    """쿼리에 관련된 컨텍스트 검색"""
    try:
        # 세션별 벡터 스토어 확인
        vector_store_id = None
        if session_id and session_id in vector_stores_db:
            vector_store_id = vector_stores_db[session_id]
        elif knowledge_base_id:
            vector_store_id = knowledge_base_id

        if not vector_store_id:
            logger.info("No vector store available for context search")
            return ""

        # 벡터 스토어에서 관련 문서 검색
        search_results = await search_vector_store(vector_store_id, query, limit=3)

        if not search_results:
            return ""

        # 검색 결과를 컨텍스트로 포맷팅
        context_parts = []
        for result in search_results:
            if result.get("content"):
                context_parts.append(f"관련 정보: {result['content']}")

        return "\n\n".join(context_parts)

    except Exception as e:
        logger.error(f"❌ Context retrieval failed: {str(e)}")
        return ""


async def list_vector_stores() -> List[Dict]:
    """사용 가능한 벡터 스토어 목록 조회"""
    try:
        vector_stores = await client.beta.vector_stores.list(limit=20)

        stores_info = []
        for store in vector_stores.data:
            stores_info.append({
                "id": store.id,
                "name": store.name,
                "file_counts": store.file_counts,
                "created_at": store.created_at,
                "metadata": store.metadata if hasattr(store, 'metadata') else {}
            })

        return stores_info

    except Exception as e:
        logger.error(f"❌ Failed to list vector stores: {str(e)}")
        return []


# 📊 토큰 관리 및 최적화 함수들
def estimate_tokens(text: str) -> int:
    """텍스트의 토큰 수를 추정 (1 토큰 ≈ 4 characters)"""
    return max(1, len(text) // 4)


def calculate_conversation_tokens(messages: List[Dict]) -> int:
    """대화의 총 토큰 수 계산"""
    total_tokens = 0
    for message in messages:
        content = message.get("content", "")
        total_tokens += estimate_tokens(content)
    return total_tokens


async def create_conversation_summary(session_id: str, messages: List[Dict]) -> str:
    """대화 요약 생성"""
    try:
        print(f"📝 Creating conversation summary for session: {session_id}")

        # 요약할 메시지들 준비 (최근 20개만)
        messages_to_summarize = messages[-20:] if len(messages) > 20 else messages

        conversation_text = ""
        for msg in messages_to_summarize:
            role = msg.get("role", "")
            content = msg.get("content", "")
            conversation_text += f"{role}: {content}\n"

        # OpenAI를 사용하여 요약 생성
        summary_response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # 요약은 저렴한 모델 사용
            messages=[
                {
                    "role": "system",
                    "content": """당신은 대화 요약 전문가입니다. 주어진 대화를 간결하고 핵심적으로 요약해주세요.

요약 형식:
- 주요 주제와 논의 내용
- 핵심 결론이나 결정사항
- 중요한 데이터나 정보
- 사용자 관심사나 요구사항

한국어로 3-5문장으로 요약해주세요."""
                },
                {
                    "role": "user",
                    "content": f"다음 대화를 요약해주세요:\n\n{conversation_text}"
                }
            ],
            max_tokens=200,
            temperature=0.3
        )

        summary = summary_response.choices[0].message.content

        # 요약 저장
        conversation_summaries[session_id] = summary
        print(f"✅ Summary created for session {session_id}")

        return summary

    except Exception as e:
        print(f"🚨 Failed to create summary: {e}")
        return "대화 요약 생성 실패"


async def optimize_conversation_for_tokens(session_id: str) -> List[Dict]:
    """토큰 사용량에 따른 대화 최적화"""
    messages = messages_db.get(session_id, [])

    if not messages:
        return []

    current_tokens = calculate_conversation_tokens(messages)
    print(f"📊 Current conversation tokens: {current_tokens}")

    # 토큰 한계 초과 시 처리
    if current_tokens > MAX_CONVERSATION_TOKENS or len(messages) > MAX_MESSAGES_PER_SESSION:
        print(f"🚨 Token limit exceeded, optimizing conversation...")

        # 1. 대화 요약 생성 (아직 없다면)
        if session_id not in conversation_summaries:
            await create_conversation_summary(session_id, messages[:-10])  # 최근 10개 제외하고 요약

        # 2. 최근 메시지만 유지 (시스템 메시지 + 요약 + 최근 대화)
        recent_messages = messages[-15:]  # 최근 15개 메시지만 유지

        # 3. 요약을 시스템 메시지로 삽입
        summary = conversation_summaries.get(session_id, "")
        if summary:
            summary_message = {
                "role": "system",
                "content": f"이전 대화 요약: {summary}\n\n위 내용을 참고하여 지속적이고 일관된 대화를 이어가세요."
            }
            optimized_messages = [summary_message] + recent_messages
        else:
            optimized_messages = recent_messages

        # 4. 최적화된 메시지로 업데이트
        messages_db[session_id] = optimized_messages

        # 5. 토큰 사용량 업데이트
        new_tokens = calculate_conversation_tokens(optimized_messages)
        update_token_usage(session_id, current_tokens, new_tokens, optimized=True)

        print(f"✅ Conversation optimized: {current_tokens} → {new_tokens} tokens")
        return optimized_messages

    else:
        # 토큰 사용량 추적
        update_token_usage(session_id, current_tokens, current_tokens)
        return messages


def update_token_usage(session_id: str, old_tokens: int, new_tokens: int, optimized: bool = False):
    """토큰 사용량 업데이트"""
    if session_id not in token_usage_db:
        token_usage_db[session_id] = {
            "total_tokens": 0,
            "messages_count": 0,
            "optimizations": 0,
            "last_updated": datetime.now().isoformat()
        }

    usage = token_usage_db[session_id]
    usage["total_tokens"] = new_tokens
    usage["messages_count"] = len(messages_db.get(session_id, []))
    usage["last_updated"] = datetime.now().isoformat()

    if optimized:
        usage["optimizations"] += 1
        usage["tokens_saved"] = usage.get("tokens_saved", 0) + (old_tokens - new_tokens)


async def get_optimized_conversation_messages(session_id: str, max_messages: int = 20) -> List[Dict]:
    """최적화된 대화 메시지 가져오기"""
    # 먼저 토큰 최적화 수행
    optimized_messages = await optimize_conversation_for_tokens(session_id)

    # 요청된 최대 메시지 수로 제한
    if len(optimized_messages) > max_messages:
        # 시스템 메시지가 있다면 유지하고 나머지를 제한
        system_messages = [msg for msg in optimized_messages if msg.get("role") == "system"]
        user_assistant_messages = [msg for msg in optimized_messages if msg.get("role") in ["user", "assistant"]]

        # 최근 메시지들 선택
        recent_messages = user_assistant_messages[-(max_messages - len(system_messages)):]
        return system_messages + recent_messages

    return optimized_messages


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
                    last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
                start_date = first_day.isoformat()
                end_date = last_day.isoformat()
            elif time_period == "next_month":
                # 다음 달 1일부터 말일까지
                if today.month == 12:
                    next_month_first = today.replace(year=today.year + 1, month=1, day=1)
                    next_month_last = today.replace(year=today.year + 1, month=2, day=1) - timedelta(days=1)
                else:
                    next_month_first = today.replace(month=today.month + 1, day=1)
                    if today.month == 11:
                        next_month_last = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
                    else:
                        next_month_last = today.replace(month=today.month + 2, day=1) - timedelta(days=1)
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
            result = await gmail_service.get_messages(
                query=arguments.get("query", ""),
                max_results=arguments.get("max_results", 10)
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


# 개선된 통합 API 함수 (Responses API + Assistant API)
async def create_response_with_best_api(
        session_id: str,
        model: str,
        instructions: str,
        user_input: str,
        conversation_messages: List[Dict],
        available_tools: List[Dict],
        needs_web_search: bool,
        model_config: Dict
) -> str:
    """
    최적의 OpenAI API를 선택하여 응답 생성
    - Assistant API (복잡한 대화, 도구 사용)
    - Responses API (웹 검색, 간단한 도구 사용)
    - Chat Completions API (폴백)
    """

    # 1. Assistant API 사용 조건 확인
    use_assistant_api = (
            model_config.get("supports_assistant", False) and
            not needs_web_search  # 웹 검색이 필요하지 않은 경우 (도구 유무 무관)
    )

    print(f"🔍 API Selection Debug:")
    print(f"  - Model: {model}")
    print(f"  - supports_assistant: {model_config.get('supports_assistant', False)}")
    print(f"  - needs_web_search: {needs_web_search}")
    print(f"  - available_tools: {len(available_tools) if available_tools else 0}")
    print(f"  - use_assistant_api: {use_assistant_api}")

    if use_assistant_api:
        print("🎯 Using Assistant API for complex conversation with tools")
        return await create_response_with_assistant_api(
            session_id, user_input, model, model_config, instructions
        )

    # 2. Responses API 사용 (기존 로직)
    return await create_response_with_responses_api_fallback(
        model, instructions, user_input, conversation_messages,
        available_tools, needs_web_search, model_config
    )


def build_context_input(user_input: str, conversation_messages: list) -> str:
    """대화 컨텍스트를 포함한 입력 구성"""
    context_input = user_input
    if conversation_messages:
        # 최근 대화 히스토리를 컨텍스트로 포함 (최대 5개)
        recent_messages = conversation_messages[-5:]
        context_parts = []
        for msg in recent_messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                context_parts.append(f"사용자: {content}")
            else:
                context_parts.append(f"AI: {content}")
        
        # 컨텍스트와 현재 질문을 결합
        context_input = f"**이전 대화 컨텍스트:**\n" + "\n".join(context_parts) + f"\n\n**현재 질문:** {user_input}"
    
    return context_input


# 기존 Responses API 함수 (이름 변경)
async def create_response_with_responses_api_fallback(
        model: str,
        instructions: str,
        user_input: str,
        conversation_messages: List[Dict],
        available_tools: List[Dict],
        needs_web_search: bool,
        model_config: Dict
) -> str:
    """
    Responses API를 사용한 응답 생성 (Assistant API 폴백)
    Google Functions와 웹 검색을 지원
    강화된 에러 처리 포함
    """

    print(f"🔍 create_response_with_responses_api_fallback called with:")
    print(f"  - Model: {model}")
    print(f"  - Instructions present: {bool(instructions)}")
    print(f"  - User input: {user_input}")
    print(f"  - Conversation messages: {len(conversation_messages)}")
    print(f"  - Available tools: {len(available_tools)}")
    print(f"  - Needs web search: {needs_web_search}")
    print(f"  - Model config: {model_config}")

    # 1. 웹 검색이 필요한 경우
    if needs_web_search and model_config.get("supports_web_search", False):
        print("🔍 Using Responses API with web search")

        async def web_search_call():
            # 대화 컨텍스트를 포함한 입력 구성
            context_input = build_context_input(user_input, conversation_messages)
            
            return await client.responses.create(
                model=model,
                instructions=instructions,
                input=context_input,
                tools=[{"type": "web_search"}]
            )

        response = await safe_openai_call_with_retry(web_search_call, user_content=user_input)

        if isinstance(response, dict) and "error" in response:
            return response["error"]

        return extract_response_content(response, include_sources=True)

    # 2. Google 도구가 필요한 경우
    elif available_tools:
        print("🛠️ Using Responses API with Google tools")

        # Google 도구를 Responses API 형식으로 변환
        responses_tools = convert_tools_for_responses_api(available_tools)

        async def tools_call():
            # 대화 컨텍스트를 포함한 입력 구성
            context_input = build_context_input(user_input, conversation_messages)
            
            return await client.responses.create(
                model=model,
                instructions=instructions,
                input=context_input,
                tools=responses_tools
            )

        response = await safe_openai_call_with_retry(tools_call, user_content=user_input)

        if isinstance(response, dict) and "error" in response:
            return response["error"]

        return await process_tool_calls_in_response(response)

    # 3. 일반 대화
    else:
        print("💬 Using Responses API for general conversation")

        async def general_call():
            # 대화 컨텍스트를 포함한 입력 구성
            context_input = build_context_input(user_input, conversation_messages)
            
            return await client.responses.create(
                model=model,
                instructions=instructions,
                input=context_input
            )

        response = await safe_openai_call_with_retry(general_call, user_content=user_input)

        if isinstance(response, dict) and "error" in response:
            # Responses API 완전 실패 시 Chat Completions로 폴백
            print("⚠️ Responses API completely failed, trying Chat Completions fallback")
            return await safe_fallback_to_chat_completions(
                model, conversation_messages, available_tools, model_config, user_input
            )

        return extract_response_content(response)


def extract_response_content(response, include_sources: bool = False) -> str:
    """Responses API 응답에서 텍스트 내용 추출"""
    content = ""
    sources = []

    for output_item in response.output:
        if output_item.type == 'message' and hasattr(output_item, 'content'):
            for content_item in output_item.content:
                if content_item.type == 'output_text':
                    # 텍스트 내용 정규화 - 줄바꿈 처리 개선
                    raw_text = content_item.text
                    
                    # 연속된 공백을 하나로 정규화하되, 줄바꿈은 보존
                    import re
                    # 먼저 \r\n을 \n으로 통일
                    normalized_text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
                    
                    # 줄바꿈 문자는 보존하면서 연속된 공백만 정리
                    # 단, 줄 끝의 공백은 제거하고 줄바꿈은 유지
                    lines = normalized_text.split('\n')
                    processed_lines = []
                    
                    for line in lines:
                        # 각 줄의 앞뒤 공백 제거하고 연속 공백을 하나로
                        cleaned_line = re.sub(r'\s+', ' ', line.strip())
                        processed_lines.append(cleaned_line)
                    
                    # 빈 줄도 보존하면서 텍스트 재구성
                    content += '\n'.join(processed_lines)

                    # 웹 검색 소스 추출
                    if include_sources and hasattr(content_item, 'annotations'):
                        for annotation in content_item.annotations:
                            if annotation.type == 'url_citation':
                                sources.append({
                                    'title': getattr(annotation, 'title', ''),
                                    'url': getattr(annotation, 'url', ''),
                                })

    # 소스 정보 추가 - 마크다운 포맷팅 개선
    if include_sources and sources:
        content += "\n\n## 참고 출처\n\n"
        for i, source in enumerate(sources, 1):
            title = source['title'] if source['title'] else f"출처 {i}"
            # 각 리스트 항목 뒤에 적절한 줄바꿈 추가 (마크다운 리스트 포맷)
            content += f"{i}. **[{title}]({source['url']})**\n\n"
        print(f"📚 Found {len(sources)} web search sources")

    return content.strip()  # 마지막에 불필요한 공백/줄바꿈 제거


def convert_tools_for_responses_api(chat_tools: List[Dict]) -> List[Dict]:
    """Chat Completions API 도구를 Responses API 형식으로 변환"""
    responses_tools = []

    for tool in chat_tools:
        if tool.get("type") == "function":
            # Google 함수들을 Responses API 형식으로 변환
            responses_tools.append({
                "type": "function",
                "function": tool["function"]
            })

    return responses_tools


async def process_tool_calls_in_response(response) -> str:
    """Responses API에서 도구 호출 결과 처리"""
    content = ""

    for output_item in response.output:
        if output_item.type == 'message' and hasattr(output_item, 'content'):
            for content_item in output_item.content:
                if content_item.type == 'output_text':
                    content += content_item.text
                elif content_item.type == 'tool_call':
                    # 도구 호출 실행
                    function_name = content_item.function.name
                    function_args = json.loads(content_item.function.arguments)

                    print(f"🔧 Executing tool: {function_name}({function_args})")
                    result = await execute_google_function(function_name, function_args)

                    # 결과 포맷팅
                    if function_name == "get_calendar_events" and isinstance(result, list):
                        content += "\n\n" + format_calendar_events_as_table(result)
                    else:
                        content += f"\n\n## 🔧 {function_name} 실행 결과\n\n"
                        if isinstance(result, (dict, list)):
                            content += f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"
                        else:
                            content += str(result)

    return content


async def fallback_to_chat_completions(
        model: str,
        messages: List[Dict],
        tools: List[Dict],
        model_config: Dict
) -> str:
    """Chat Completions API로 폴백 (기존 버전)"""
    print("⚠️ Falling back to Chat Completions API")

    chat_params = {
        "model": model,
        "messages": messages,
        "max_tokens": model_config["max_tokens"],
        "temperature": model_config["temperature"]
    }

    if tools:
        chat_params["tools"] = tools
        chat_params["tool_choice"] = "auto"

    response = await client.chat.completions.create(**chat_params)

    # Function calls 처리
    if response.choices[0].message.tool_calls:
        content = response.choices[0].message.content or ""

        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            result = await execute_google_function(function_name, function_args)

            if function_name == "get_calendar_events" and isinstance(result, list):
                content += "\n\n" + format_calendar_events_as_table(result)
            else:
                content += f"\n\n## 🔧 {function_name} 실행 결과\n\n"
                if isinstance(result, (dict, list)):
                    content += f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"
                else:
                    content += str(result)

        return content

    return response.choices[0].message.content


async def safe_fallback_to_chat_completions(
        model: str,
        messages: List[Dict],
        tools: List[Dict],
        model_config: Dict,
        user_content: str
) -> str:
    """안전한 Chat Completions API 폴백 (에러 처리 포함)"""
    print("🛡️ Safe fallback to Chat Completions API")

    async def chat_call():
        chat_params = {
            "model": model,
            "messages": messages,
            "max_tokens": model_config["max_tokens"],
            "temperature": model_config["temperature"]
        }

        if tools:
            chat_params["tools"] = tools
            chat_params["tool_choice"] = "auto"

        return await client.chat.completions.create(**chat_params)

    response = await safe_openai_call_with_retry(
        chat_call,
        max_retries=2,  # 폴백이므로 재시도 횟수 줄임
        user_content=user_content
    )

    if isinstance(response, dict) and "error" in response:
        return response["error"]

    # Function calls 처리
    if response.choices[0].message.tool_calls:
        content = response.choices[0].message.content or ""

        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            result = await execute_google_function(function_name, function_args)

            if function_name == "get_calendar_events" and isinstance(result, list):
                content += "\n\n" + format_calendar_events_as_table(result)
            else:
                content += f"\n\n## 🔧 {function_name} 실행 결과\n\n"
                if isinstance(result, (dict, list)):
                    content += f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"
                else:
                    content += str(result)

        return content

    return response.choices[0].message.content


# Assistant API 관련 함수들
async def get_or_create_assistant(session_id: str, model: str, instructions: str = None) -> str:
    """세션용 Assistant를 가져오거나 생성"""

    # 이미 Assistant가 있는지 확인
    if session_id in assistants_db:
        assistant_id = assistants_db[session_id]
        try:
            # Assistant 존재 확인
            assistant = await client.beta.assistants.retrieve(assistant_id)
            print(f"🤖 Using existing assistant: {assistant_id}")
            return assistant_id
        except Exception as e:
            print(f"⚠️ Existing assistant not found: {e}")
            # Assistant가 삭제되었다면 새로 생성
            del assistants_db[session_id]

    # 새 Assistant 생성
    try:
        print(f"🆕 Creating new assistant for session: {session_id}")

        # Google 도구들을 Assistant 형식으로 변환
        tools = []
        if GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated():
            tools.extend(get_google_tools())
            print(f"🛠️ Added {len(tools)} Google tools to assistant")

        # 벡터 스토어 생성 또는 가져오기 (선택적)
        tool_resources = {}
        try:
            vector_store_id = await create_or_get_vector_store(session_id)
            if vector_store_id:
                tool_resources["file_search"] = {
                    "vector_store_ids": [vector_store_id]
                }
                # 파일 검색 도구 추가
                tools.append({"type": "file_search"})
                print(f"🗂️ Added vector store to assistant: {vector_store_id}")
        except Exception as vs_error:
            print(f"⚠️ Vector store creation failed, continuing without: {vs_error}")

        # instructions가 제공되지 않은 경우 기본값 사용
        if not instructions:
            instructions = """당신은 NSales Pro의 전문적인 영업 AI 도우미입니다. 

주요 역할:
- 영업 데이터 분석 및 인사이트 제공
- 프로젝트 정보 조회 및 관리 지원
- 업무 관련 질문에 대한 전문적 답변
- Google Calendar 및 Gmail 통합 기능 활용

지침:
- 항상 한국어로 친근하고 전문적으로 답변하세요
- 이전 대화 내용을 기억하고 문맥을 유지하세요
- Google 서비스 도구를 적극 활용하여 실제 데이터를 제공하세요
- 최신 정보가 필요한 경우 웹 검색을 활용하세요

Google 서비스 멘션:
- @캘린더 → 캘린더 일정 조회
- @메일 → 이메일 조회/발송  
- @일정생성 → 새 일정 생성
- @빈시간 → 빈 시간 검색"""

        # Assistant 생성 (벡터 스토어 리소스 포함)
        assistant_params = {
            "name": f"NSales Pro Assistant - {session_id[:8]}",
            "instructions": instructions,
            "model": model,
            "tools": tools
        }

        # 벡터 스토어가 있는 경우 tool_resources 추가
        if tool_resources:
            assistant_params["tool_resources"] = tool_resources

        assistant = await client.beta.assistants.create(**assistant_params)

        assistant_id = assistant.id
        assistants_db[session_id] = assistant_id
        print(f"✅ Created assistant: {assistant_id}")

        return assistant_id

    except Exception as e:
        print(f"🚨 Failed to create assistant: {e}")
        raise e


async def get_or_create_thread(session_id: str) -> str:
    """세션용 Thread를 가져오거나 생성하고 기존 대화 히스토리 동기화"""

    # 이미 Thread가 있는지 확인
    if session_id in threads_db:
        thread_id = threads_db[session_id]
        try:
            # Thread 존재 확인
            thread = await client.beta.threads.retrieve(thread_id)
            print(f"🧵 Using existing thread: {thread_id}")
            return thread_id
        except Exception as e:
            print(f"⚠️ Existing thread not found: {e}")
            # Thread가 삭제되었다면 새로 생성
            del threads_db[session_id]

    # 새 Thread 생성
    try:
        print(f"🆕 Creating new thread for session: {session_id}")

        # 기존 세션 메시지들을 Thread에 추가할 메시지로 준비
        initial_messages = []
        session_messages = messages_db.get(session_id, [])

        # 최근 20개 메시지만 Thread에 포함 (토큰 절약)
        recent_messages = session_messages[-20:] if len(session_messages) > 20 else session_messages

        for msg in recent_messages:
            # Assistant API Thread는 system 메시지를 지원하지 않으므로 제외
            if msg.get("role") in ["user", "assistant"]:
                initial_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Thread 생성 (기존 메시지 포함)
        if initial_messages:
            thread = await client.beta.threads.create(messages=initial_messages)
            print(f"📚 Thread created with {len(initial_messages)} existing messages")
        else:
            thread = await client.beta.threads.create()
            print(f"📝 Empty thread created")

        thread_id = thread.id
        threads_db[session_id] = thread_id
        print(f"✅ Created thread: {thread_id}")

        return thread_id

    except Exception as e:
        print(f"🚨 Failed to create thread: {e}")
        raise e


async def create_response_with_assistant_api(
        session_id: str,
        user_input: str,
        model: str,
        model_config: Dict,
        instructions: str = None
) -> str:
    """Assistant API를 사용한 응답 생성"""

    try:
        print(f"🎯 Using Assistant API for session: {session_id}")
        print(f"🔍 Session messages count: {len(messages_db.get(session_id, []))}")

        # Assistant와 Thread 준비
        assistant_id = await get_or_create_assistant(session_id, model, instructions)
        thread_id = await get_or_create_thread(session_id)

        print(f"📝 Assistant ID: {assistant_id}")
        print(f"🧵 Thread ID: {thread_id}")

        # 사용자 메시지를 Thread에 추가
        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        # Run 생성 및 실행
        async def assistant_call():
            return await client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=assistant_id,
                timeout=60  # 60초 타임아웃
            )

        run = await safe_openai_call_with_retry(assistant_call, user_content=user_input)

        if isinstance(run, dict) and "error" in run:
            return run["error"]

        # Run 상태 확인
        if run.status == 'completed':
            # 최신 메시지 가져오기
            messages = await client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=1
            )

            if messages.data:
                latest_message = messages.data[0]
                if latest_message.role == "assistant" and latest_message.content:
                    # 텍스트 내용 추출
                    content = ""
                    for content_block in latest_message.content:
                        if content_block.type == "text":
                            content += content_block.text.value

                    print(f"✅ Assistant response completed")
                    return content

        elif run.status == 'requires_action':
            # 도구 호출 처리
            print(f"🔧 Assistant requires action: tool calls")
            return await handle_assistant_tool_calls(run, thread_id)

        elif run.status in ['failed', 'expired', 'cancelled']:
            error_msg = f"Assistant 실행 실패: {run.status}"
            if hasattr(run, 'last_error') and run.last_error:
                error_msg += f" - {run.last_error.message}"
            return error_msg

        else:
            return f"Assistant 실행 상태: {run.status}. 잠시 후 다시 시도해주세요."

    except Exception as e:
        return handle_openai_error(e, user_content=user_input)


async def handle_assistant_tool_calls(run, thread_id: str) -> str:
    """Assistant의 도구 호출 처리"""

    try:
        tool_outputs = []

        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"🔧 Assistant tool call: {function_name}({function_args})")

            # Google 함수 실행
            result = await execute_google_function(function_name, function_args)

            # 결과 포맷팅
            if function_name == "get_calendar_events" and isinstance(result, list):
                output = format_calendar_events_as_table(result)
            else:
                output = json.dumps(result, ensure_ascii=False, indent=2)

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": output
            })

        # 도구 출력 제출 및 Run 완료 대기
        completed_run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

        if completed_run.status == 'completed':
            # 최신 응답 가져오기
            messages = await client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=1
            )

            if messages.data:
                latest_message = messages.data[0]
                if latest_message.role == "assistant" and latest_message.content:
                    content = ""
                    for content_block in latest_message.content:
                        if content_block.type == "text":
                            content += content_block.text.value

                    print(f"✅ Assistant tool calls completed")
                    return content

        # 최종 응답 반환
        final_content = ""
        if completed_run.status == 'completed':
            messages = await client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=1
            )
            if messages.data and messages.data[0].content:
                for content_block in messages.data[0].content:
                    if content_block.type == "text":
                        final_content += content_block.text.value

        # 도구 실행 결과 요약
        tool_results_summary = "\n".join([f"- {tool['tool_call_id']}: {tool['output'][:100]}..." for tool in tool_outputs])

        # 최종적으로 생성된 AI의 답변을 반환합니다.
        if final_content:
            # AI 응답과 도구 실행 결과를 함께 제공할 수 있습니다.
            # return f"{final_content}\n\n--- 도구 실행 요약 ---\n{tool_results_summary}"
            return final_content
        else:
            # 만약 AI의 최종 답변이 없다면, 도구 실행 결과라도 반환합니다.
            return f"도구 실행이 완료되었습니다. 요약:\n{tool_results_summary}"

    except Exception as e:
        print(f"🚨 Assistant tool call error: {e}")
        return f"도구 실행 중 오류가 발생했습니다: {str(e)}"


# 체계적인 OpenAI 에러 처리 함수들
def handle_openai_error(e: Exception, user_content: str = "", request_id: str = None) -> str:
    """
    OpenAI API 에러를 체계적으로 처리하고 사용자 친화적인 메시지 반환
    """
    print(f"🚨 OpenAI API Error: {type(e).__name__}: {e}")

    # Request ID 로깅 (디버깅용)
    if request_id:
        print(f"🔍 Request ID: {request_id}")
    elif hasattr(e, 'request_id'):
        print(f"🔍 Request ID: {e.request_id}")

    if isinstance(e, openai.APIConnectionError):
        return handle_connection_error(e)
    elif isinstance(e, openai.RateLimitError):
        return handle_rate_limit_error(e)
    elif isinstance(e, openai.AuthenticationError):
        return handle_auth_error(e)
    elif isinstance(e, openai.PermissionDeniedError):
        return handle_permission_error(e)
    elif isinstance(e, openai.NotFoundError):
        return handle_not_found_error(e)
    elif isinstance(e, openai.UnprocessableEntityError):
        return handle_validation_error(e, user_content)
    elif isinstance(e, openai.InternalServerError):
        return handle_server_error(e)
    elif isinstance(e, openai.BadRequestError):
        return handle_bad_request_error(e, user_content)
    else:
        return handle_generic_error(e, user_content)


def handle_connection_error(e: openai.APIConnectionError) -> str:
    """네트워크 연결 에러 처리"""
    print(f"🌐 Connection Error: {e}")
    return "네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인하고 잠시 후 다시 시도해주세요."


def handle_rate_limit_error(e: openai.RateLimitError) -> str:
    """API 속도 제한 에러 처리"""
    print(f"⏱️ Rate Limit Error: {e}")
    return "현재 요청이 많아 처리가 지연되고 있습니다. 잠시 후 다시 시도해주세요."


def handle_auth_error(e: openai.AuthenticationError) -> str:
    """인증 에러 처리"""
    print(f"🔐 Authentication Error: {e}")
    return "AI 서비스 인증에 문제가 있습니다. 관리자에게 문의해주세요."


def handle_permission_error(e: openai.PermissionDeniedError) -> str:
    """권한 에러 처리"""
    print(f"🚫 Permission Error: {e}")
    return "AI 서비스 접근 권한이 없습니다. 관리자에게 문의해주세요."


def handle_not_found_error(e: openai.NotFoundError) -> str:
    """리소스 없음 에러 처리"""
    print(f"❓ Not Found Error: {e}")
    return "요청한 AI 모델이나 리소스를 찾을 수 없습니다. 다른 모델을 선택해주세요."


def handle_validation_error(e: openai.UnprocessableEntityError, user_content: str) -> str:
    """입력 검증 에러 처리"""
    print(f"⚠️ Validation Error: {e}")

    error_message = str(e).lower()
    if "context_length_exceeded" in error_message or "maximum context length" in error_message:
        return "메시지가 너무 길어서 처리할 수 없습니다. 더 짧은 메시지로 나누어 보내주세요."
    elif "invalid_request" in error_message:
        return "요청 형식에 문제가 있습니다. 다시 시도해주세요."
    else:
        return f"입력 내용에 문제가 있습니다: {user_content[:50]}{'...' if len(user_content) > 50 else ''}"


def handle_server_error(e: openai.InternalServerError) -> str:
    """서버 에러 처리"""
    print(f"🔥 Server Error: {e}")
    return "AI 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."


def handle_bad_request_error(e: openai.BadRequestError, user_content: str) -> str:
    """잘못된 요청 에러 처리"""
    print(f"❌ Bad Request Error: {e}")

    error_message = str(e).lower()
    if "safety" in error_message or "policy" in error_message:
        return "요청한 내용이 AI 사용 정책에 위배됩니다. 다른 방식으로 질문해주세요."
    elif "model" in error_message:
        return "선택한 AI 모델에 문제가 있습니다. 다른 모델을 선택해주세요."
    else:
        return "요청에 문제가 있습니다. 내용을 확인하고 다시 시도해주세요."


def handle_generic_error(e: Exception, user_content: str) -> str:
    """일반 에러 처리"""
    print(f"🔍 Generic Error: {type(e).__name__}: {e}")
    return f"예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해주세요."


async def safe_openai_call_with_retry(
        api_call_func,
        max_retries: int = 3,
        base_delay: float = 1.0,
        user_content: str = ""
):
    """
    재시도 로직이 포함된 안전한 OpenAI API 호출
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            # API 호출 시도
            response = await api_call_func()

            # Request ID 추출 및 로깅
            if hasattr(response, '_request_id'):
                print(f"✅ OpenAI Request ID: {response._request_id}")

            return response

        except (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError) as e:
            last_exception = e

            # 재시도 가능한 에러들
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # 지수 백오프
                print(f"🔄 Retry {attempt + 1}/{max_retries} after {delay}s due to: {type(e).__name__}")
                await asyncio.sleep(delay)
            else:
                print(f"❌ Max retries exceeded for {type(e).__name__}")

        except Exception as e:
            # 재시도 불가능한 에러들
            last_exception = e
            print(f"💥 Non-retryable error: {type(e).__name__}: {e}")
            break

    # 모든 재시도 실패 시 에러 처리
    return {"error": handle_openai_error(last_exception, user_content)}


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
    titleGenerated: Optional[bool] = False
    titleGeneratedAt: Optional[datetime] = None


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
    functionCall: Optional[str] = None  # Function name if this chunk is from function execution
    functionStatus: Optional[str] = None  # 'running', 'completed', 'error'


# 📁 개선된 파일 처리 시스템 (OpenAI Files API + 로컬 폴백)
async def process_file_with_openai(file_content: bytes, filename: str, content_type: str, session_id: str = None,
                                   add_to_vector_store: bool = False) -> str:
    """OpenAI Files API를 사용한 고급 파일 처리 (벡터 스토어 통합)"""
    try:
        print(f"🔍 Processing file with OpenAI: {filename} ({content_type})")

        # OpenAI Files API에 파일 업로드
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
            temp_file.write(file_content)
            temp_file.flush()

            # OpenAI Files API 업로드
            file_object = await client.files.create(
                file=open(temp_file.name, "rb"),
                purpose="assistants"  # 문서 분석용
            )

            print(f"✅ File uploaded to OpenAI: {file_object.id}")

            # 파일 처리 완료까지 대기
            await client.files.wait_for_processing(file_object.id)

            # 벡터 스토어에 추가 (선택적)
            if add_to_vector_store and session_id:
                try:
                    vector_store_id = await create_or_get_vector_store(session_id)
                    if await add_file_to_vector_store(vector_store_id, file_object.id):
                        print(f"📚 File added to vector store for future reference")
                        # 벡터 스토어에 추가된 경우 파일을 삭제하지 않음
                        file_should_be_deleted = False
                    else:
                        file_should_be_deleted = True
                except Exception as vs_error:
                    print(f"⚠️ Failed to add file to vector store: {vs_error}")
                    file_should_be_deleted = True
            else:
                file_should_be_deleted = True

            # Assistant API를 통해 파일 분석
            analysis_result = await analyze_file_with_assistant(file_object.id, filename)

            # 파일 정리 (벡터 스토어에 추가되지 않은 경우만)
            if file_should_be_deleted:
                try:
                    await client.files.delete(file_object.id)
                    print(f"🗑️ Cleaned up file: {file_object.id}")
                except:
                    pass  # 삭제 실패는 무시

            # 임시 파일 정리
            os.unlink(temp_file.name)

            return analysis_result

    except Exception as e:
        print(f"🚨 OpenAI Files API error: {e}")
        # 폴백: 로컬 처리
        return await process_file_locally(file_content, filename, content_type)


async def analyze_file_with_assistant(file_id: str, filename: str) -> str:
    """Assistant API를 사용하여 파일 분석"""
    try:
        # 임시 Assistant 생성 (파일 분석 전용)
        assistant = await client.beta.assistants.create(
            name="Document Analyzer",
            instructions="""당신은 전문적인 문서 분석 AI입니다. 
            
업무:
- 업로드된 문서의 내용을 정확하게 추출하고 분석
- 한국어와 영어 문서 모두 처리 가능
- 문서의 핵심 내용, 구조, 중요 정보를 요약

응답 형식:
1. 📄 문서 요약: 주요 내용 요약
2. 📋 핵심 정보: 중요한 데이터, 수치, 날짜 등
3. 📝 전체 텍스트: 원본 텍스트 (구조화된 형태)

한국어로 응답해주세요.""",
            model="gpt-4o",
            tools=[{"type": "file_search"}]
        )

        # Thread 생성
        thread = await client.beta.threads.create()

        # 파일과 함께 메시지 생성
        message = await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"다음 파일을 분석해주세요: {filename}",
            attachments=[{
                "file_id": file_id,
                "tools": [{"type": "file_search"}]
            }]
        )

        # Assistant 실행
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            timeout=60
        )

        if run.status == 'completed':
            # 응답 메시지 가져오기
            messages = await client.beta.threads.messages.list(
                thread_id=thread.id,
                order="desc",
                limit=1
            )

            if messages.data:
                response_content = ""
                for content_block in messages.data[0].content:
                    if content_block.type == "text":
                        response_content += content_block.text.value

                # 정리
                await client.beta.assistants.delete(assistant.id)

                return response_content

        # 실패 시 폴백
        await client.beta.assistants.delete(assistant.id)
        raise Exception(f"Assistant API run failed: {run.status}")

    except Exception as e:
        print(f"🚨 Assistant file analysis error: {e}")
        raise e


async def process_file_locally(file_content: bytes, filename: str, content_type: str) -> str:
    """로컬 파일 처리 (폴백)"""
    print(f"🔄 Fallback to local processing: {filename}")

    try:
        if content_type == "application/pdf" or filename.lower().endswith('.pdf'):
            return await extract_text_from_pdf_local(file_content)
        elif content_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"] or filename.lower().endswith(
            '.docx'):
            return await extract_text_from_docx_local(file_content)
        elif content_type.startswith('image/'):
            return await process_image_with_hybrid_approach(file_content, filename)
        elif content_type == "text/plain" or filename.lower().endswith('.txt'):
            return file_content.decode('utf-8', errors='ignore')
        else:
            return f"지원하지 않는 파일 형식: {content_type}"
    except Exception as e:
        return f"로컬 파일 처리 오류: {str(e)}"


# 로컬 처리 함수들 (기존 함수들을 이름 변경)
async def extract_text_from_pdf_local(file_content: bytes) -> str:
    """PDF 파일에서 텍스트 추출 (로컬)"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return f"📄 PDF 문서 내용:\n\n{text.strip()}"
    except Exception as e:
        return f"PDF 읽기 오류: {str(e)}"


async def extract_text_from_docx_local(file_content: bytes) -> str:
    """DOCX 파일에서 텍스트 추출 (로컬)"""
    try:
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return f"📄 Word 문서 내용:\n\n{text.strip()}"
    except Exception as e:
        return f"DOCX 읽기 오류: {str(e)}"


def encode_image_to_base64(file_content: bytes) -> str:
    """이미지를 base64로 인코딩"""
    return base64.b64encode(file_content).decode('utf-8')


async def analyze_image_with_gpt4o_vision(file_content: bytes, filename: str, prompt: str = None) -> str:
    """GPT-4o Vision API를 사용하여 이미지 분석"""
    try:
        # 이미지를 base64로 인코딩
        base64_image = encode_image_to_base64(file_content)
        
        # 기본 프롬프트 설정
        if not prompt:
            prompt = """이 이미지를 자세히 분석해주세요. 다음 내용을 포함해주세요:
1. 이미지에 보이는 주요 내용과 객체들
2. 텍스트가 있다면 모든 텍스트 내용
3. 문서나 표가 있다면 구조와 데이터
4. 전체적인 맥락과 의미
5. 비즈니스나 업무와 관련된 정보가 있다면 상세히 설명

한국어로 상세하고 구체적으로 답변해주세요."""

        # GPT-4o Vision API 호출
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"  # 고해상도 분석
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.1  # 더 정확한 분석을 위해 낮은 temperature
        )
        
        vision_result = response.choices[0].message.content
        return f"🔍 GPT-4o Vision 분석 결과:\n\n{vision_result}"
        
    except Exception as e:
        print(f"GPT-4o Vision API 오류: {e}")
        return f"GPT-4o Vision 분석 오류: {str(e)}"


async def extract_text_from_image_local(file_content: bytes) -> str:
    """이미지에서 OCR로 텍스트 추출 (로컬)"""
    try:
        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image, lang='kor+eng')
        extracted_text = text.strip() if text.strip() else "이미지에서 텍스트를 찾을 수 없습니다."
        return f"🖼️ 이미지 OCR 결과:\n\n{extracted_text}"
    except Exception as e:
        return f"이미지 OCR 오류: {str(e)}"


async def process_image_with_hybrid_approach(file_content: bytes, filename: str) -> str:
    """이미지를 OCR과 GPT-4o Vision을 모두 사용하여 처리 (하이브리드 접근)"""
    try:
        print(f"🖼️ Processing image with hybrid approach: {filename}")
        
        # 1. GPT-4o Vision 분석 시도
        vision_result = await analyze_image_with_gpt4o_vision(file_content, filename)
        
        # 2. OCR 분석도 수행 (텍스트 추출 보완)
        ocr_result = await extract_text_from_image_local(file_content)
        
        # 3. 결과 결합
        combined_result = f"""📋 **이미지 종합 분석 결과** (파일: {filename})

{vision_result}

---

{ocr_result}

---

💡 **분석 방법**: GPT-4o Vision API와 OCR을 모두 사용하여 이미지의 시각적 정보와 텍스트 정보를 종합적으로 분석했습니다."""

        return combined_result
        
    except Exception as e:
        print(f"Hybrid image processing error: {e}")
        # 폴백: OCR만 사용
        return await extract_text_from_image_local(file_content)


def is_image_file(file: any) -> bool:
    """파일이 이미지인지 확인"""
    if hasattr(file, 'content_type') and file.content_type:
        return file.content_type.startswith('image/')
    if hasattr(file, 'filename') and file.filename:
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return any(file.filename.lower().endswith(ext) for ext in image_extensions)
    return False


async def create_multimodal_message_content(text: str, image_files: list = None) -> list:
    """멀티모달 메시지 콘텐츠 생성 (텍스트 + 이미지)"""
    content = []
    
    # 텍스트 추가
    if text:
        content.append({"type": "text", "text": text})
    
    # 이미지 파일들 추가
    if image_files:
        for file in image_files:
            try:
                file_content = await file.read()
                base64_image = encode_image_to_base64(file_content)
                
                # 이미지 타입 감지
                content_type = file.content_type or 'image/jpeg'
                image_format = content_type.split('/')[-1] if '/' in content_type else 'jpeg'
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{content_type};base64,{base64_image}",
                        "detail": "high"
                    }
                })
                
                print(f"🖼️ Added image to multimodal message: {file.filename} ({image_format})")
                
            except Exception as e:
                print(f"Failed to process image {file.filename}: {e}")
                # 이미지 처리 실패 시 텍스트로 알림 추가
                content.append({
                    "type": "text", 
                    "text": f"\n[이미지 처리 실패: {file.filename} - {str(e)}]"
                })
    
    return content


async def send_multimodal_message_to_gpt4o(
    conversation_messages: list,
    user_text: str,
    image_files: list = None,
    model: str = "gpt-4o",
    tools: list = None
) -> str:
    """멀티모달 메시지를 GPT-4o에 전송"""
    try:
        # 멀티모달 콘텐츠 생성
        multimodal_content = await create_multimodal_message_content(user_text, image_files)
        
        # 기존 대화에 멀티모달 메시지 추가
        messages = conversation_messages.copy()
        messages.append({
            "role": "user",
            "content": multimodal_content
        })
        
        # GPT-4o API 호출 매개변수 구성
        chat_params = {
            "model": model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        # 도구가 있으면 추가
        if tools:
            chat_params["tools"] = tools
            chat_params["tool_choice"] = "auto"
        
        # GPT-4o Vision API 호출
        response = await client.chat.completions.create(**chat_params)
        
        # Function calls 처리 (기존 로직과 동일)
        if response.choices[0].message.tool_calls:
            content = response.choices[0].message.content or ""
            
            for tool_call in response.choices[0].message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                result = await execute_google_function(function_name, function_args)
                
                if isinstance(result, dict) and "error" in result:
                    content += f"\n\n## ❌ {function_name} 실행 오류\n\n{result['error']}"
                else:
                    content += f"\n\n## ✅ {function_name} 실행 완료\n\n"
                    if isinstance(result, (dict, list)):
                        content += f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"
                    else:
                        content += str(result)
            
            return content
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Multimodal message error: {e}")
        raise e


async def process_uploaded_file(file: UploadFile, session_id: str = None, add_to_vector_store: bool = False) -> str:
    """업로드된 파일을 처리하여 텍스트 추출 (OpenAI Files API 우선 사용, 벡터 스토어 통합)"""
    try:
        file_content = await file.read()
        file_type = file.content_type.lower() if file.content_type else ""
        filename = file.filename or "unknown_file"

        print(f"📁 Processing uploaded file: {filename} ({file_type})")

        # 파일 크기 확인 (OpenAI 제한: 512MB)
        file_size_mb = len(file_content) / (1024 * 1024)

        # 지원되는 파일 형식 확인
        supported_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain"
        ]

        supported_extensions = [".pdf", ".docx", ".txt"]
        is_supported_type = (
                file_type in supported_types or
                any(filename.lower().endswith(ext) for ext in supported_extensions) or
                file_type.startswith('image/')
        )

        # OpenAI Files API 사용 조건
        use_openai_files = (
                is_supported_type and
                file_size_mb < 500 and  # 512MB 제한보다 약간 낮게
                file_type != "text/plain"  # 텍스트 파일은 로컬에서 처리
        )

        if use_openai_files:
            print(f"🚀 Using OpenAI Files API for enhanced processing")
            return await process_file_with_openai(file_content, filename, file_type, session_id, add_to_vector_store)
        else:
            print(f"🔄 Using local processing (file too large or unsupported)")
            return await process_file_locally(file_content, filename, file_type)

    except Exception as e:
        print(f"🚨 File processing error: {e}")
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
        messageCount=0,
        titleGenerated=False,
        titleGeneratedAt=None
    )

    sessions_db[session_id] = session.dict()
    messages_db[session_id] = []
    return session


def get_session(session_id: str) -> ChatSession:
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions_db[session_id].copy()
    
    # Handle legacy sessions missing required fields
    if "title" not in session_data:
        session_data["title"] = f"채팅 {session_id[:8]}"
    if "updatedAt" not in session_data:
        session_data["updatedAt"] = session_data.get("createdAt", datetime.now())
    if "createdAt" not in session_data:
        session_data["createdAt"] = datetime.now()
    if "messageCount" not in session_data:
        session_data["messageCount"] = len(messages_db.get(session_id, []))
    if "titleGenerated" not in session_data:
        session_data["titleGenerated"] = False
    if "titleGeneratedAt" not in session_data:
        session_data["titleGeneratedAt"] = None
    
    # Update the stored session with missing fields for future use
    sessions_db[session_id].update(session_data)
    
    return ChatSession(**session_data)


def migrate_legacy_sessions():
    """Legacy sessions을 새로운 스키마로 마이그레이션"""
    migrated_count = 0
    for session_id, session_data in sessions_db.items():
        updated = False
        if "title" not in session_data:
            session_data["title"] = f"채팅 {session_id[:8]}"
            updated = True
        if "updatedAt" not in session_data:
            session_data["updatedAt"] = session_data.get("createdAt", datetime.now())
            updated = True
        if "createdAt" not in session_data:
            session_data["createdAt"] = datetime.now()
            updated = True
        if "messageCount" not in session_data:
            session_data["messageCount"] = len(messages_db.get(session_id, []))
            updated = True
        if "titleGenerated" not in session_data:
            session_data["titleGenerated"] = False
            updated = True
        if "titleGeneratedAt" not in session_data:
            session_data["titleGeneratedAt"] = None
            updated = True
        
        if updated:
            migrated_count += 1
    
    if migrated_count > 0:
        logger.info(f"✅ Migrated {migrated_count} legacy sessions to new schema")


def update_session_message_count(session_id: str):
    if session_id in sessions_db:
        sessions_db[session_id]["messageCount"] = len(messages_db.get(session_id, []))
        sessions_db[session_id]["updatedAt"] = datetime.now()


def update_session_title(session_id: str, new_title: str, auto_generated: bool = False):
    """세션 제목 업데이트"""
    if session_id in sessions_db:
        sessions_db[session_id]["title"] = new_title
        sessions_db[session_id]["updatedAt"] = datetime.now()
        if auto_generated:
            sessions_db[session_id]["titleGenerated"] = True
            sessions_db[session_id]["titleGeneratedAt"] = datetime.now()


async def auto_generate_title_if_needed(session_id: str) -> Optional[str]:
    """자동 제목 생성이 필요한 경우 생성하여 업데이트"""
    if not title_generator or not TITLE_GENERATOR_AVAILABLE:
        return None
    
    try:
        # 세션과 메시지 데이터 가져오기
        if session_id not in sessions_db or session_id not in messages_db:
            return None
            
        session_data = sessions_db[session_id]
        messages = messages_db[session_id]
        
        # 제목 생성 조건 확인
        if not title_generator.should_generate_title(messages, session_data["title"]):
            return None
        
        # 제목 생성
        new_title = await title_generator.generate_title(messages)
        
        if new_title:
            # 제목 업데이트
            update_session_title(session_id, new_title, auto_generated=True)
            logger.info(f"Auto-generated title for session {session_id}: {new_title}")
            return new_title
        else:
            # 폴백 제목 사용
            fallback_title = title_generator.get_fallback_title(messages)
            update_session_title(session_id, fallback_title, auto_generated=True)
            logger.info(f"Using fallback title for session {session_id}: {fallback_title}")
            return fallback_title
            
    except Exception as e:
        logger.error(f"Failed to generate title for session {session_id}: {str(e)}")
        return None


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
    migrate_legacy_sessions()  # Legacy sessions 마이그레이션
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
        print("✅ Google OAuth 인증 성공! 사용자가 5173 포트로 리다이렉트됩니다.")
        return RedirectResponse(url="http://localhost:5173?google_auth=success&message=Google 서비스 연동이 성공적으로 완료되었습니다!")
    else:
        print("❌ Google OAuth 인증 실패! 사용자가 5173 포트로 리다이렉트됩니다.")
        return RedirectResponse(url="http://localhost:5173?google_auth=error&message=Google 서비스 연동에 실패했습니다. 다시 시도해주세요.")


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
    sessions = []
    for session_id, session_data in sessions_db.items():
        # Handle legacy sessions missing required fields
        cleaned_session = session_data.copy()
        if "title" not in cleaned_session:
            cleaned_session["title"] = f"채팅 {session_id[:8]}"
        if "updatedAt" not in cleaned_session:
            cleaned_session["updatedAt"] = cleaned_session.get("createdAt", datetime.now())
        if "createdAt" not in cleaned_session:
            cleaned_session["createdAt"] = datetime.now()
        if "messageCount" not in cleaned_session:
            cleaned_session["messageCount"] = len(messages_db.get(session_id, []))
        if "titleGenerated" not in cleaned_session:
            cleaned_session["titleGenerated"] = False
        if "titleGeneratedAt" not in cleaned_session:
            cleaned_session["titleGeneratedAt"] = None
        
        sessions.append(cleaned_session)
        # Update the stored session with missing fields for future use
        sessions_db[session_id].update(cleaned_session)

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


@app.post("/api/v1/chat/sessions/{session_id}/generate-title")
async def generate_session_title(session_id: str):
    """세션의 AI 기반 제목 생성 (수동 트리거)"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # 세션 메시지 가져오기
        messages = messages_db.get(session_id, [])
        
        if len(messages) < 2:
            return {"success": False, "message": "메시지가 충분하지 않습니다"}
        
        # 제목 생성
        generated_title = await title_generator.generate_title(messages)
        
        if not generated_title:
            # 생성 실패시 폴백 제목 사용
            fallback_title = title_generator.get_fallback_title(messages)
            return {"success": False, "title": fallback_title, "message": "AI 제목 생성 실패, 폴백 제목 사용"}
        
        # 세션 제목 업데이트
        sessions_db[session_id]["title"] = generated_title
        sessions_db[session_id]["titleGenerated"] = True
        sessions_db[session_id]["titleGeneratedAt"] = datetime.now()
        sessions_db[session_id]["updatedAt"] = datetime.now()
        
        logger.info(f"✨ Manual title generated for session {session_id}: {generated_title}")
        
        return {
            "success": True, 
            "title": generated_title,
            "message": "AI 제목이 성공적으로 생성되었습니다"
        }
        
    except Exception as e:
        logger.error(f"❌ Manual title generation failed for session {session_id}: {str(e)}")
        return {"success": False, "message": f"제목 생성 중 오류 발생: {str(e)}"}


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


@app.get("/api/v1/chat/sessions/{session_id}/tokens")
async def get_token_usage(session_id: str):
    """세션의 토큰 사용량 정보 조회"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")

    # 현재 토큰 사용량 계산
    current_messages = messages_db.get(session_id, [])
    current_tokens = calculate_conversation_tokens(current_messages)

    # 저장된 토큰 사용량 정보
    usage_info = token_usage_db.get(session_id, {
        "total_tokens": current_tokens,
        "messages_count": len(current_messages),
        "optimizations": 0,
        "tokens_saved": 0,
        "last_updated": datetime.now().isoformat()
    })

    # 실시간 정보 업데이트
    usage_info.update({
        "current_tokens": current_tokens,
        "max_tokens": MAX_CONVERSATION_TOKENS,
        "optimization_threshold": SUMMARY_TRIGGER_TOKENS,
        "has_summary": session_id in conversation_summaries,
        "efficiency_percentage": round((1 - current_tokens / MAX_CONVERSATION_TOKENS) * 100,
                                       1) if current_tokens < MAX_CONVERSATION_TOKENS else 0
    })

    return usage_info


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

        # 파일 분류: 이미지 파일과 문서 파일 분리
        image_files = []
        document_files = []
        file_contents = []
        
        if files:
            for file in files:
                if file.filename:  # 파일이 실제로 업로드된 경우
                    print(f"Processing file: {file.filename}, type: {file.content_type}")
                    
                    if is_image_file(file):
                        # 이미지 파일은 멀티모달 처리를 위해 별도 보관
                        image_files.append(file)
                        print(f"🖼️ Image file detected: {file.filename}")
                    else:
                        # 문서 파일은 기존 방식으로 처리
                        document_files.append(file)
                        file_text = await process_uploaded_file(file, sessionId, add_to_vector_store=True)
                        file_contents.append(f"[파일: {file.filename}]\n{file_text}")

        # 메시지 내용 구성 (텍스트 + 문서 파일 내용)
        message_content = content
        if file_contents:
            message_content += "\n\n" + "\n\n".join(file_contents)
        
        # 이미지 파일이 있으면 멀티모달 메시지 사용 여부 결정
        use_multimodal = len(image_files) > 0 and model == "gpt-4o"

        # 사용자 메시지 저장
        # 멀티모달의 경우 이미지 정보 추가 표시
        display_content = message_content
        if use_multimodal and image_files:
            image_info = ", ".join([f"🖼️ {file.filename}" for file in image_files])
            display_content += f"\n\n[첨부된 이미지: {image_info}]"
            
        user_message = ChatMessage(
            id=generate_id(),
            content=display_content,
            role="user",
            timestamp=datetime.now(),
            sessionId=sessionId
        )
        session_messages.append(user_message.model_dump())

        # OpenAI API에 전달할 메시지 구성
        system_prompt = "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 첨부된 파일의 내용을 분석하여 관련된 답변을 제공해주세요. 최신 정보가 필요하거나 실시간 데이터, 뉴스, 시장 동향 등을 질문받으면 웹 검색을 적극 활용하여 정확하고 최신의 정보를 제공하세요."
        
        conversation_messages = [{"role": "system", "content": system_prompt}]

        # 기존 대화 내용 추가 (최근 20개 메시지만 유지)
        recent_messages = session_messages[-21:] if len(session_messages) > 21 else session_messages[:-1]  # 현재 메시지 제외
        for msg in recent_messages:
            conversation_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 선택된 모델 정보 가져오기
        selected_model = model if model in AVAILABLE_MODELS else "gpt-4o"
        model_config = AVAILABLE_MODELS[selected_model]

        # OpenAI API 호출
        try:
            print(f"Using model: {selected_model} ({model_config['name']})")
            print(f"Conversation length: {len(conversation_messages)} messages")
            print(f"Files processed: {len(file_contents)} documents, {len(image_files)} images")
            print(f"Multimodal mode: {use_multimodal}")

            # 사용 가능한 도구 목록 구성
            available_tools = []
            if GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated():
                available_tools.extend(get_google_tools())

            if use_multimodal:
                # 멀티모달 메시지로 처리 (이미지 + 텍스트)
                print("🔄 Using multimodal message processing...")
                ai_content = await send_multimodal_message_to_gpt4o(
                    conversation_messages,
                    message_content,
                    image_files,
                    selected_model,
                    available_tools
                )
            else:
                # 기존 방식으로 처리
                print("🔄 Using traditional text-only processing...")
                
                # 현재 사용자 메시지 추가 (텍스트만)
                conversation_messages.append({"role": "user", "content": message_content})
                
                # 웹 검색 여부는 form 데이터에서 확인 (일단 False로 설정)
                needs_web_search = False  # 파일 업로드 시에는 웹 검색 비활성화

                # 최적의 OpenAI API 선택하여 사용
                ai_content = await create_response_with_best_api(
                    sessionId,
                    selected_model,
                    system_prompt,
                    message_content,  # 파일 내용이 포함된 메시지
                    conversation_messages,
                    available_tools,
                    needs_web_search,
                    model_config
                )

            print(f"OpenAI Response: {ai_content}")

        except Exception as e:
            # 개선된 에러 처리
            ai_content = handle_openai_error(e, user_content=content)

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

    # 📊 토큰 최적화된 대화 메시지 구성
    optimized_messages = await get_optimized_conversation_messages(request.sessionId, max_messages=18)

    conversation_messages = [{"role": "system", "content": system_prompt}]

    # 최적화된 메시지 추가
    for msg in optimized_messages:
        if msg.get("role") != "system":  # 시스템 메시지는 이미 추가됨
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

    # 개선된 OpenAI API 호출 (Responses API 우선 사용)
    try:
        print(f"Using model: {selected_model} ({model_config['name']})")
        print(f"Conversation length: {len(conversation_messages)} messages")

        # 웹 검색 여부 확인
        needs_web_search = getattr(request, 'webSearch', False)

        # 최적의 OpenAI API 선택하여 사용
        ai_content = await create_response_with_best_api(
            request.sessionId,
            selected_model,
            system_prompt,
            request.content,
            conversation_messages,
            available_tools,
            needs_web_search,
            model_config
        )

        print(f"OpenAI Response: {ai_content}")

    except Exception as e:
        # 개선된 에러 처리
        ai_content = handle_openai_error(e, user_content=request.content)

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

    # 자동 제목 생성 시도 (백그라운드에서 실행)
    await auto_generate_title_if_needed(request.sessionId)

    return ChatResponse(**ai_message.dict())


# 스트리밍 채팅 (통합 API 선택 로직 사용)
@app.post("/api/v1/chat/stream")
async def stream_chat(request: ChatRequest):
    """통합 API 선택을 사용한 스트리밍 채팅"""

    # 세션 존재 확인
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

    # 모델 선택 및 설정
    selected_model = request.model if request.model in AVAILABLE_MODELS else "gpt-4o"
    model_config = AVAILABLE_MODELS[selected_model]

    # 세션의 기존 메시지 히스토리 가져오기
    session_messages = messages_db.get(request.sessionId, [])

    # 현재 한국 시간 정보 생성
    korea_tz = timezone(timedelta(hours=9))
    current_time_kst = datetime.now(korea_tz)

    # Google 서비스 사용 안내를 포함한 시스템 프롬프트 구성
    system_prompt = f"""당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요. 최신 정보가 필요하거나 실시간 데이터, 뉴스, 시장 동향 등을 질문받으면 웹 검색을 적극 활용하여 정확하고 최신의 정보를 제공하세요.

**현재 시간 정보:**
- 현재 날짜: {current_time_kst.strftime('%Y년 %m월 %d일 (%A)')}
- 현재 시간: {current_time_kst.strftime('%H시 %M분')}
- 시간대: 한국 표준시 (KST, UTC+9)

"오늘", "이번 주", "이번 달" 등의 시간 표현을 사용할 때는 위의 한국 시간 기준으로 해석해주세요."""

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
        system_prompt += "\n\n**🛠️ Google 서비스 활용 가능:**\n캘린더 조회, 이메일 관리, 일정 생성 등의 요청 시 Google 함수를 적극 활용하여 실제 데이터를 제공해주세요."

    # 📊 토큰 최적화된 대화 메시지 구성 (스트리밍)
    optimized_messages = await get_optimized_conversation_messages(request.sessionId, max_messages=18)

    conversation_messages = [{"role": "system", "content": system_prompt}]

    # 최적화된 메시지 추가 (현재 메시지는 제외)
    for msg in optimized_messages:
        if msg.get("role") != "system":  # 시스템 메시지는 이미 추가됨
            conversation_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # 현재 사용자 메시지 추가
    conversation_messages.append({
        "role": "user",
        "content": request.content
    })

    # Google 도구 준비
    available_tools = []
    if GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated():
        available_tools.extend(GOOGLE_TOOLS)
        print(f"🛠️ Google 도구 {len(GOOGLE_TOOLS)}개 추가됨")
        print(f"🎯 멘션 감지: {mention_detected}")
        if mention_detected:
            print(f"🔥 강제 Function Calling 활성화 예정: @캘린더 → get_calendar_events")

    # 웹 검색 여부 확인
    needs_web_search = getattr(request, 'webSearch', False)

    # Google 멘션이 감지된 경우 직접 Function Calling 처리
    if mention_detected and available_tools:
        print("🎯 멘션 감지됨 - 직접 Function Calling 처리")
        return await stream_with_direct_function_calling(
            request.sessionId,
            selected_model,
            conversation_messages,
            available_tools,
            model_config,
            user_message
        )

    # 일반적인 경우 통합 API 사용
    return await stream_with_unified_api(
        request.sessionId,
        selected_model,
        system_prompt,
        request.content,
        conversation_messages,
        available_tools,
        needs_web_search,
        model_config,
        user_message,
        mention_detected
    )


async def stream_with_unified_api(
        session_id: str,
        model: str,
        instructions: str,
        user_input: str,
        conversation_messages: List[Dict],
        available_tools: List[Dict],
        needs_web_search: bool,
        model_config: Dict,
        user_message: ChatMessage,
        mention_detected: bool = False
):
    """통합 API 선택을 사용한 스트리밍 응답 생성"""

    async def generate_unified_stream():
        ai_message_id = generate_id()
        full_content = ""

        try:
            # 1. 통합 API 선택 로직 실행
            print(f"🔍 Stream API Selection Debug:")
            print(f"  - Model: {model}")
            print(f"  - supports_assistant: {model_config.get('supports_assistant', False)}")
            print(f"  - needs_web_search: {needs_web_search}")
            print(f"  - available_tools: {len(available_tools) if available_tools else 0}")

            # Assistant API는 현재 스트리밍 미지원이므로 가능한 API 사용
            # 먼저 Chat Completions로 시도 (더 안정적)
            use_responses_api = needs_web_search and model_config.get("supports_web_search", False)

            if use_responses_api:
                print("🌐 Using Responses API for streaming")
                # Responses API 스트리밍
                async for chunk_str in stream_with_responses_api(
                        model, instructions, user_input, conversation_messages,
                        available_tools, needs_web_search, model_config, ai_message_id, session_id
                ):
                    # chunk_str은 이미 "data: {...}\n\n" 형태
                    if chunk_str.startswith("data:"):
                        try:
                            chunk_data = json.loads(chunk_str[5:].strip())
                            full_content += chunk_data.get("content", "")
                        except:
                            pass
                    yield chunk_str
            else:
                print("💬 Using Chat Completions API for streaming")
                # Chat Completions 스트리밍 (폴백)
                async for chunk_str in stream_with_chat_completions_fallback(
                        model, conversation_messages, ai_message_id, session_id
                ):
                    # chunk_str은 이미 "data: {...}\n\n" 형태
                    if chunk_str.startswith("data:"):
                        try:
                            chunk_data = json.loads(chunk_str[5:].strip())
                            full_content += chunk_data.get("content", "")
                        except:
                            pass
                    yield chunk_str

        except Exception as e:
            print(f"🚨 Streaming error: {e}")
            print(f"🚨 Error type: {type(e)}")
            print(f"🚨 Error details: {str(e)}")
            import traceback
            print(f"🚨 Traceback: {traceback.format_exc()}")
            error_content = handle_openai_error(e, user_content=user_input)

            error_chunk = {
                "id": ai_message_id,
                "content": error_content,
                "role": "assistant",
                "timestamp": datetime.now().isoformat(),
                "sessionId": session_id,
                "isComplete": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            full_content = error_content

        # AI 응답 저장
        ai_message = ChatMessage(
            id=ai_message_id,
            content=full_content,
            role="assistant",
            timestamp=datetime.now(),
            sessionId=session_id
        )

        messages_db[session_id].append(ai_message.dict())
        update_session_message_count(session_id)

    return StreamingResponse(
        generate_unified_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


async def stream_with_responses_api(
        model: str,
        instructions: str,
        user_input: str,
        conversation_messages: List[Dict],
        available_tools: List[Dict],
        needs_web_search: bool,
        model_config: Dict,
        ai_message_id: str,
        session_id: str
):
    """Responses API를 사용한 스트리밍"""

    # Responses API는 스트리밍 미지원이므로 일반 응답 후 청크로 나누어 전송
    try:
        print(f"🔍 Calling Responses API fallback with:")
        print(f"  - Model: {model}")
        print(f"  - Instructions length: {len(instructions) if instructions else 0}")
        print(f"  - User input: {user_input[:50]}...")
        print(f"  - Conversation messages: {len(conversation_messages)}")
        print(f"  - Available tools: {len(available_tools)}")
        print(f"  - Needs web search: {needs_web_search}")

        ai_content = await create_response_with_responses_api_fallback(
            model, instructions, user_input, conversation_messages,
            available_tools, needs_web_search, model_config
        )

        print(f"✅ Responses API success, content length: {len(ai_content) if ai_content else 0}")

        # 텍스트를 청크로 나누어 스트리밍 시뮬레이션 - 줄바꿈 보존
        import re
        
        # 단어와 공백/줄바꿈을 모두 보존하면서 토큰화
        # \S+는 공백이 아닌 문자들(단어), \s+는 공백 문자들(스페이스, 탭, 줄바꿈 등)
        tokens = re.findall(r'\S+|\s+', ai_content)
        current_content = ""

        for i, token in enumerate(tokens):
            current_content += token

            # 공백/줄바꿈 토큰은 스트리밍하지 않고, 단어 토큰만 스트리밍
            if token.strip():  # 공백이 아닌 토큰(단어)만 전송
                chunk_data = {
                    "id": ai_message_id,
                    "content": token,
                    "role": "assistant",
                    "timestamp": datetime.now().isoformat(),
                    "sessionId": session_id,
                    "isComplete": False
                }

                yield f"data: {json.dumps(chunk_data)}\n\n"

                # 단어 간 약간의 딜레이 (자연스러운 스트리밍 효과)
                await asyncio.sleep(0.05)
            else:
                # 공백/줄바꿈 토큰도 전송 (포맷팅 보존을 위해)
                chunk_data = {
                    "id": ai_message_id,
                    "content": token,
                    "role": "assistant",
                    "timestamp": datetime.now().isoformat(),
                    "sessionId": session_id,
                    "isComplete": False
                }

                yield f"data: {json.dumps(chunk_data)}\n\n"

        # 완료 청크
        final_chunk = {
            "id": ai_message_id,
            "content": "",
            "role": "assistant",
            "timestamp": datetime.now().isoformat(),
            "sessionId": session_id,
            "isComplete": True
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"

    except Exception as e:
        print(f"🚨 Responses API streaming error: {e}")
        raise e


async def stream_with_chat_completions_fallback(
        model: str,
        conversation_messages: List[Dict],
        ai_message_id: str,
        session_id: str
):
    """Chat Completions API를 사용한 스트리밍 폴백"""

    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=conversation_messages,
            stream=True,
            max_tokens=4000,
            temperature=0.7
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content

                chunk_data = {
                    "id": ai_message_id,
                    "content": content,
                    "role": "assistant",
                    "timestamp": datetime.now().isoformat(),
                    "sessionId": session_id,
                    "isComplete": False
                }

                yield f"data: {json.dumps(chunk_data)}\n\n"

        # 완료 청크
        final_chunk = {
            "id": ai_message_id,
            "content": "",
            "role": "assistant",
            "timestamp": datetime.now().isoformat(),
            "sessionId": session_id,
            "isComplete": True
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"

    except Exception as e:
        print(f"🚨 Chat Completions streaming error: {e}")
        raise e


async def stream_with_realtime_api(request: ChatRequest, user_message: ChatMessage, model: str):
    """OpenAI Realtime API를 사용한 진짜 스트리밍"""

    async def generate_realtime_stream():
        ai_message_id = generate_id()
        full_content = ""

        try:
            print(f"🎙️ Using Realtime API with model: {model}")

            async with client.beta.realtime.connect(model=model) as connection:
                # 세션 설정 (텍스트 모드)
                await connection.session.update(session={'modalities': ['text']})

                # 대화 아이템 생성
                await connection.conversation.item.create(
                    item={
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": request.content}],
                    }
                )

                # 응답 생성 시작
                await connection.response.create()

                # 실시간 이벤트 처리
                async for event in connection:
                    if event.type == 'response.text.delta':
                        # 실시간 텍스트 델타
                        delta_text = event.delta
                        full_content += delta_text

                        chunk = ChatStreamChunk(
                            id=ai_message_id,
                            content=delta_text,
                            role="assistant",
                            timestamp=datetime.now(),
                            sessionId=request.sessionId,
                            isComplete=False
                        )
                        yield f"data: {chunk.json()}\n\n"

                    elif event.type == 'response.text.done':
                        # 텍스트 완료
                        print(f"✅ Realtime text complete")

                    elif event.type == 'response.done':
                        # 전체 응답 완료
                        final_chunk = ChatStreamChunk(
                            id=ai_message_id,
                            content="",
                            role="assistant",
                            timestamp=datetime.now(),
                            sessionId=request.sessionId,
                            isComplete=True
                        )
                        yield f"data: {final_chunk.json()}\n\n"
                        break

                    elif event.type == 'error':
                        # 에러 처리
                        error_msg = f"Realtime API 오류: {event.error.message}"
                        print(f"🚨 Realtime API Error: {error_msg}")

                        error_chunk = ChatStreamChunk(
                            id=ai_message_id,
                            content=error_msg,
                            role="assistant",
                            timestamp=datetime.now(),
                            sessionId=request.sessionId,
                            isComplete=True
                        )
                        yield f"data: {error_chunk.json()}\n\n"
                        break

            # AI 응답 저장
            if full_content:
                ai_message = ChatMessage(
                    id=ai_message_id,
                    content=full_content,
                    role="assistant",
                    timestamp=datetime.now(),
                    sessionId=request.sessionId
                )

                messages_db[request.sessionId].append(ai_message.dict())
                update_session_message_count(request.sessionId)

        except Exception as e:
            error_msg = handle_openai_error(e, user_content=request.content)
            print(f"🚨 Realtime API Exception: {error_msg}")

            error_chunk = ChatStreamChunk(
                id=ai_message_id,
                content=error_msg,
                role="assistant",
                timestamp=datetime.now(),
                sessionId=request.sessionId,
                isComplete=True
            )
            yield f"data: {error_chunk.json()}\n\n"

    return StreamingResponse(
        generate_realtime_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


async def stream_with_chat_completions(request: ChatRequest, user_message: ChatMessage, model: str):
    """Chat Completions API를 사용한 스트리밍 (폴백)"""

    async def generate_chat_stream():
        ai_message_id = generate_id()
        full_content = ""

        try:
            print(f"💬 Using Chat Completions streaming with model: {model}")

            # 세션 메시지 히스토리 구성
            session_messages = messages_db.get(request.sessionId, [])
            system_prompt = "당신은 NSales Pro의 영업 AI 도우미입니다. 한국어로 친근하고 전문적으로 답변해주세요."

            conversation_messages = [{"role": "system", "content": system_prompt}]

            # 최근 메시지들 추가
            recent_messages = session_messages[-20:] if len(session_messages) > 20 else session_messages
            for msg in recent_messages:
                conversation_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # 현재 사용자 메시지 추가
            conversation_messages.append({"role": "user", "content": request.content})

            # 스트리밍 요청
            stream = await client.chat.completions.create(
                model=model,
                messages=conversation_messages,
                max_tokens=2000,
                temperature=0.7,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    delta_content = chunk.choices[0].delta.content
                    full_content += delta_content

                    chunk_obj = ChatStreamChunk(
                        id=ai_message_id,
                        content=delta_content,
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=request.sessionId,
                        isComplete=False
                    )
                    yield f"data: {chunk_obj.json()}\n\n"

                # 스트림 완료 체크
                if chunk.choices[0].finish_reason:
                    final_chunk = ChatStreamChunk(
                        id=ai_message_id,
                        content="",
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=request.sessionId,
                        isComplete=True
                    )
                    yield f"data: {final_chunk.json()}\n\n"
                    break

            # AI 응답 저장
            if full_content:
                ai_message = ChatMessage(
                    id=ai_message_id,
                    content=full_content,
                    role="assistant",
                    timestamp=datetime.now(),
                    sessionId=request.sessionId
                )

                messages_db[request.sessionId].append(ai_message.dict())
                update_session_message_count(request.sessionId)

        except Exception as e:
            error_msg = handle_openai_error(e, user_content=request.content)
            print(f"🚨 Chat Completions Streaming Error: {error_msg}")

            error_chunk = ChatStreamChunk(
                id=ai_message_id,
                content=error_msg,
                role="assistant",
                timestamp=datetime.now(),
                sessionId=request.sessionId,
                isComplete=True
            )
            yield f"data: {error_chunk.json()}\n\n"

    return StreamingResponse(
        generate_chat_stream(),
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

        # 현재 한국 시간 정보 생성
        korea_tz = timezone(timedelta(hours=9))
        current_time_kst = datetime.now(korea_tz)

        # Google 서비스 사용 안내를 포함한 시스템 프롬프트 구성
        system_prompt = f"""당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요. 최신 정보가 필요하거나 실시간 데이터, 뉴스, 시장 동향 등을 질문받으면 웹 검색을 적극 활용하여 정확하고 최신의 정보를 제공하세요.
                        **현재 시간 정보:**
                        - 현재 날짜: {current_time_kst.strftime('%Y년 %m월 %d일 (%A)')}
                        - 현재 시간: {current_time_kst.strftime('%H시 %M분')}
                        - 시간대: 한국 표준시 (KST, UTC+9)
                        
                        "오늘", "이번 주", "이번 달" 등의 시간 표현을 사용할 때는 위의 한국 시간 기준으로 해석해주세요.
                        """

        # 멘션 기반 서비스 활성화 로직
        mention_detected = False
        google_mention_keywords = ['@캘린더', '@메일', '@일정생성', '@빈시간']

        for keyword in google_mention_keywords:
            if keyword in request.content:
                mention_detected = True
                break

        # Google 서비스가 사용 가능하고 멘션이 감지된 경우 안내 추가
        if GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated() and mention_detected:
            print(f"🎯 Google 멘션 감지됨: {request.content}")
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
            print(f"🔍 Debug - mention_detected: {mention_detected}")
            print(f"🔍 Debug - GOOGLE_SERVICES_AVAILABLE: {GOOGLE_SERVICES_AVAILABLE}")
            print(
                f"🔍 Debug - is_authenticated: {auth_service.is_authenticated() if GOOGLE_SERVICES_AVAILABLE else 'N/A'}")

            # 웹 검색 여부는 프론트엔드에서 결정 (webSearch 파라미터로 전달)
            needs_web_search = getattr(request, 'webSearch', False)

            # 웹 검색 도구 추가
            if needs_web_search and model_config["supports_web_search"]:
                available_tools.append({"type": "web_search"})

            # Google 서비스 도구 추가 (인증된 경우만)
            if GOOGLE_SERVICES_AVAILABLE and auth_service.is_authenticated():
                available_tools.extend(GOOGLE_TOOLS)
                print(f"🔗 Google 서비스 도구 {len(GOOGLE_TOOLS)}개 추가됨")
                print(f"🔍 사용 가능한 도구들: {[tool['function']['name'] for tool in GOOGLE_TOOLS]}")
            search_content = request.content

            if needs_web_search and model_config["supports_web_search"]:
                print("🔍 Web search detected in stream - using Responses API")
                
                # 웹 검색 시작 상태 표시
                search_start_chunk = ChatStreamChunk(
                    id=ai_message_id,
                    content="🔍 웹 검색 중...",
                    role="assistant",
                    timestamp=datetime.now(),
                    sessionId=request.sessionId,
                    isComplete=False
                )
                yield f"data: {search_start_chunk.json()}\n\n"
                await asyncio.sleep(0.1)
                
                try:
                    # 웹 검색이 필요한 경우 스트리밍 대신 일반 응답 사용 (대화 컨텍스트 포함)
                    context_input = build_context_input(search_content, conversation_messages)
                    response = await client.responses.create(
                        model=selected_model,
                        instructions=system_prompt,
                        input=context_input,
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
                        sources_text = "\n\n## 참고 출처\n\n"
                        for i, source in enumerate(sources, 1):
                            title = source['title'] if source['title'] else f"출처 {i}"
                            sources_text += f"{i}. **[{title}]({source['url']})**\n"
                        ai_content += sources_text
                        print(f"📚 Found {len(sources)} web search sources in stream")

                    full_content = ai_content


                    # 웹 검색 결과를 한 번에 스트리밍 (마크다운 구조 보존)
                    web_search_chunk = ChatStreamChunk(
                        id=ai_message_id,
                        content=ai_content,
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=request.sessionId,
                        isComplete=False
                    )
                    yield f"data: {web_search_chunk.json()}\n\n"
                    await asyncio.sleep(0.5)  # 웹 검색 결과 표시 시간

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
                    # 스트리밍 파라미터 구성
                    stream_params = {
                        "model": selected_model,
                        "messages": conversation_messages,
                        "max_tokens": model_config["max_tokens"],
                        "temperature": model_config["temperature"],
                        "stream": True
                    }

                    # 도구가 있으면 추가
                    if available_tools:
                        stream_params["tools"] = available_tools
                        # 멘션이 감지된 경우 Function Calling 강제 활성화
                        if mention_detected:
                            stream_params["tool_choice"] = {"type": "function",
                                                            "function": {"name": "get_calendar_events"}}
                            print(f"🎯 강제 Function Calling 활성화: get_calendar_events")
                        else:
                            stream_params["tool_choice"] = "auto"
                        print(f"🛠️ 스트리밍 Function Calling 활성화: {len(available_tools)}개 도구")

                    stream = await client.chat.completions.create(**stream_params)
            else:
                # 임시로 스트리밍 대신 일반 API 사용
                chat_params = {
                    "model": selected_model,
                    "messages": conversation_messages,
                    "max_tokens": model_config["max_tokens"],
                    "temperature": model_config["temperature"]
                }

                # 도구가 있으면 추가 (웹 검색 도구 또는 Google 도구)
                if available_tools:
                    chat_params["tools"] = available_tools
                    # 멘션이 감지된 경우 Function Calling 강제 활성화
                    if mention_detected:
                        chat_params["tool_choice"] = {"type": "function", "function": {"name": "get_calendar_events"}}
                        print(f"🎯 강제 Function Calling 활성화: get_calendar_events")
                    else:
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
                                # 함수 실행 상태 표시 (한 번에 출력)
                                status_content = f"\n\n🔄 {function_name} 실행 중...\n"
                                status_chunk = ChatStreamChunk(
                                    id=ai_message_id,
                                    content=status_content,
                                    role="assistant",
                                    timestamp=datetime.now(),
                                    sessionId=request.sessionId,
                                    isComplete=False,
                                    functionCall=function_name,
                                    functionStatus="running"
                                )
                                yield f"data: {status_chunk.json()}\n\n"
                                await asyncio.sleep(0.1)

                                # 함수 실행
                                function_result = FUNCTION_MAP[function_name](**function_args)

                                # 결과를 스트리밍으로 출력
                                if isinstance(function_result, (dict, list)):
                                    result_content = f"## ✅ {function_name} 실행 완료\n\n```json\n{json.dumps(function_result, ensure_ascii=False, indent=2)}\n```\n\n"
                                else:
                                    result_content = f"## ✅ {function_name} 실행 완료\n\n{function_result}\n\n"
                                ai_content += result_content

                                # 함수 결과는 한 번에 스트리밍 (마크다운 파싱 개선)
                                result_chunk = ChatStreamChunk(
                                    id=ai_message_id,
                                    content=result_content,
                                    role="assistant",
                                    timestamp=datetime.now(),
                                    sessionId=request.sessionId,
                                    isComplete=False,
                                    functionCall=function_name,
                                    functionStatus="completed"
                                )
                                yield f"data: {result_chunk.json()}\n\n"
                                await asyncio.sleep(0.2)

                            except Exception as e:
                                error_content = f"## ❌ {function_name} 실행 오류\n\n{str(e)}\n\n"
                                ai_content += error_content

                                # 에러 내용은 한 번에 스트리밍 (마크다운 파싱 개선)
                                error_chunk = ChatStreamChunk(
                                    id=ai_message_id,
                                    content=error_content,
                                    role="assistant",
                                    timestamp=datetime.now(),
                                    sessionId=request.sessionId,
                                    isComplete=False,
                                    functionCall=function_name,
                                    functionStatus="error"
                                )
                                yield f"data: {error_chunk.json()}\n\n"
                                await asyncio.sleep(0.2)
                else:
                    # 일반 응답을 문장 단위로 스트리밍 (마크다운 파싱 개선)
                    import re
                    sentences = re.split(r'(\. |\? |\! |\n\n|\n)', ai_content)
                    
                    for sentence in sentences:
                        if sentence.strip():
                            stream_chunk = ChatStreamChunk(
                                id=ai_message_id,
                                content=sentence,
                                role="assistant",
                                timestamp=datetime.now(),
                                sessionId=request.sessionId,
                                isComplete=False
                            )
                            yield f"data: {stream_chunk.json()}\n\n"
                            
                            # 문장 유형에 따른 적응적 지연
                            if sentence.endswith(('.', '!', '?')):
                                await asyncio.sleep(0.3)
                            elif sentence == '\n\n':
                                await asyncio.sleep(0.2)
                            elif sentence == '\n':
                                await asyncio.sleep(0.15)
                            else:
                                await asyncio.sleep(0.1)

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
                                isComplete=False,
                                functionCall=function_name,
                                functionStatus="running"
                            )
                            yield f"data: {status_chunk.json()}\n\n"

                            # 함수 실행
                            function_result = FUNCTION_MAP[function_name](**function_args)

                            # 결과를 스트리밍으로 출력
                            if isinstance(function_result, (dict, list)):
                                result_content = f"## ✅ {function_name} 실행 완료\n\n```json\n{json.dumps(function_result, ensure_ascii=False, indent=2)}\n```\n\n"
                            else:
                                result_content = f"## ✅ {function_name} 실행 완료\n\n{function_result}\n\n"
                            full_content += result_content

                            # 함수 결과는 한 번에 스트리밍 (마크다운 파싱 개선)
                            result_chunk = ChatStreamChunk(
                                id=ai_message_id,
                                content=result_content,
                                role="assistant",
                                timestamp=datetime.now(),
                                sessionId=request.sessionId,
                                isComplete=False,
                                functionCall=function_name,
                                functionStatus="completed"
                            )
                            yield f"data: {result_chunk.json()}\n\n"
                            await asyncio.sleep(0.2)

                        except Exception as e:
                            error_content = f"## ❌ {function_name} 실행 오류\n\n{str(e)}\n\n"
                            full_content += error_content

                            # 에러 내용은 한 번에 스트리밍 (마크다운 파싱 개선)
                            error_chunk = ChatStreamChunk(
                                id=ai_message_id,
                                content=error_content,
                                role="assistant",
                                timestamp=datetime.now(),
                                sessionId=request.sessionId,
                                isComplete=False,
                                functionCall=function_name,
                                functionStatus="error"
                            )
                            yield f"data: {error_chunk.json()}\n\n"
                            await asyncio.sleep(0.2)

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
                    user_message = messages[i - 1]

                if not user_message:
                    raise HTTPException(status_code=400, detail="Cannot regenerate: no previous user message found")

                try:
                    # 세션의 기존 메시지 히스토리 가져오기 (재생성할 메시지 제외)
                    session_messages = messages_db.get(session_id, [])

                    # OpenAI API에 전달할 메시지 구성
                    conversation_messages = [
                        {"role": "system",
                         "content": "당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요."}
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


# ===========================
# 🗂️ 벡터 스토어 관리 API 엔드포인트
# ===========================

@app.get("/api/v1/vector-stores")
async def list_available_vector_stores():
    """사용 가능한 벡터 스토어 목록 조회"""
    try:
        stores = await list_vector_stores()
        return {
            "success": True,
            "vector_stores": stores,
            "total_count": len(stores)
        }
    except Exception as e:
        logger.error(f"❌ Failed to list vector stores: {str(e)}")
        raise HTTPException(status_code=500, detail=f"벡터 스토어 목록 조회 실패: {str(e)}")


@app.post("/api/v1/sessions/{session_id}/vector-store")
async def create_session_vector_store(session_id: str, name: str = None):
    """세션별 벡터 스토어 생성"""
    try:
        # 세션 존재 확인
        if session_id not in sessions_db:
            raise HTTPException(status_code=404, detail="Session not found")

        vector_store_id = await create_or_get_vector_store(session_id, name)
        return {
            "success": True,
            "vector_store_id": vector_store_id,
            "session_id": session_id,
            "message": "벡터 스토어가 성공적으로 생성되었습니다."
        }
    except Exception as e:
        logger.error(f"❌ Failed to create vector store for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"벡터 스토어 생성 실패: {str(e)}")


@app.post("/api/v1/sessions/{session_id}/vector-store/search")
async def search_session_vector_store(session_id: str, query: str, limit: int = 5):
    """세션별 벡터 스토어에서 검색"""
    try:
        # 세션 존재 확인
        if session_id not in sessions_db:
            raise HTTPException(status_code=404, detail="Session not found")

        # 벡터 스토어 확인
        if session_id not in vector_stores_db:
            raise HTTPException(status_code=404, detail="Vector store not found for this session")

        vector_store_id = vector_stores_db[session_id]
        search_results = await search_vector_store(vector_store_id, query, limit)

        return {
            "success": True,
            "query": query,
            "results": search_results,
            "total_results": len(search_results)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to search vector store for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"벡터 스토어 검색 실패: {str(e)}")


@app.post("/api/v1/knowledge-base/create")
async def create_knowledge_base(documents: List[str], session_id: str = None):
    """지식 베이스 생성 (문서 목록으로부터)"""
    try:
        if not documents:
            raise HTTPException(status_code=400, detail="Documents list cannot be empty")

        vector_store_id = await create_knowledge_base_embeddings(documents, session_id)
        return {
            "success": True,
            "vector_store_id": vector_store_id,
            "documents_count": len(documents),
            "session_id": session_id,
            "message": "지식 베이스가 성공적으로 생성되었습니다."
        }
    except Exception as e:
        logger.error(f"❌ Failed to create knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=f"지식 베이스 생성 실패: {str(e)}")


async def stream_with_direct_function_calling(
        session_id: str,
        model: str,
        conversation_messages: List[Dict],
        available_tools: List[Dict],
        model_config: Dict,
        user_message: ChatMessage
):
    """멘션 감지 시 직접 Function Calling 실행"""

    async def generate_direct_function_stream():
        ai_message_id = generate_id()
        full_content = ""

        try:
            print(f"🎯 Direct Function Calling - Model: {model}")
            print(f"🔧 Available tools: {[tool['function']['name'] for tool in available_tools]}")

            # 자동 Function Calling (OpenAI가 적절한 함수 선택)
            chat_params = {
                "model": model,
                "messages": conversation_messages,
                "max_tokens": model_config["max_tokens"],
                "temperature": model_config["temperature"],
                "tools": available_tools,
                "tool_choice": "auto",  # Let OpenAI choose the appropriate function
                "stream": True
            }

            print(f"🚀 Creating stream with auto Function Calling...")
            print(f"📝 Last user message: {user_message.content}")
            stream = await client.chat.completions.create(**chat_params)

            tool_calls = []
            current_tool_call = None

            async for chunk in stream:
                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason

                print(
                    f"🔄 Stream chunk - finish_reason: {finish_reason}, delta: content={bool(delta.content)}, tool_calls={bool(delta.tool_calls)}")

                # 일반 텍스트 콘텐츠 처리
                if delta.content:
                    print(f"📝 Content chunk: {delta.content[:50]}...")
                    content_chunk = ChatStreamChunk(
                        id=ai_message_id,
                        content=delta.content,
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=session_id,
                        isComplete=False
                    )
                    yield f"data: {content_chunk.json()}\n\n"
                    full_content += delta.content

                # Function Calling 처리
                if delta.tool_calls:
                    print(f"🔧 Tool call delta detected: {delta.tool_calls}")
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
                                print(f"🆕 New tool call: {current_tool_call['function']['name']}")
                            else:
                                # 함수 arguments 누적
                                current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments or ""
                                print(
                                    f"📝 Accumulating arguments: {current_tool_call['function']['arguments'][:100]}...")

                # 스트림 완료 체크
                if finish_reason == "tool_calls" and current_tool_call:
                    print(f"✅ Tool calls completed: {current_tool_call}")
                    tool_calls.append(current_tool_call)
                    break
                elif finish_reason == "stop":
                    print("⏹️ Stream finished with stop")
                    break

            # Function 호출 실행
            if tool_calls:
                print(f"🔧 Executing {len(tool_calls)} function calls")

                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])

                    print(f"📞 Calling function: {function_name}({function_args})")

                    if function_name in FUNCTION_MAP:
                        try:
                            # 실행 상태 표시
                            status_chunk = ChatStreamChunk(
                                id=ai_message_id,
                                content=f"\n\n🔄 {function_name} 실행 중...\n",
                                role="assistant",
                                timestamp=datetime.now(),
                                sessionId=session_id,
                                isComplete=False,
                                functionCall=function_name,
                                functionStatus="running"
                            )
                            yield f"data: {status_chunk.json()}\n\n"

                            # 함수 실행
                            function_result = FUNCTION_MAP[function_name](**function_args)

                            # 구조화된 결과 생성
                            structured_result = {
                                "type": "function_result",
                                "function_name": function_name,
                                "result": function_result,
                                "timestamp": datetime.now().isoformat()
                            }

                            # UI에서 사용할 수 있는 구조화된 결과 스트리밍
                            result_content = f"\n## 🔧 {function_name} 실행 결과\n\n"
                            if isinstance(function_result, dict) or isinstance(function_result, list):
                                result_content += f"```json\n{json.dumps(function_result, indent=2, ensure_ascii=False)}\n```\n\n"
                            else:
                                result_content += f"{function_result}\n\n"
                            full_content += result_content

                            # 결과를 한 번에 스트리밍
                            result_chunk = ChatStreamChunk(
                                id=ai_message_id,
                                content=result_content,
                                role="assistant",
                                timestamp=datetime.now(),
                                sessionId=session_id,
                                isComplete=False,
                                functionCall=function_name,
                                functionStatus="completed"
                            )
                            yield f"data: {result_chunk.json()}\n\n"

                        except Exception as e:
                            error_content = f"## ❌ {function_name} 실행 오류\n\n{str(e)}\n\n"
                            full_content += error_content

                            # 에러 내용은 한 번에 스트리밍 (마크다운 파싱 개선)
                            error_chunk = ChatStreamChunk(
                                id=ai_message_id,
                                content=error_content,
                                role="assistant",
                                timestamp=datetime.now(),
                                sessionId=session_id,
                                isComplete=False,
                                functionCall=function_name,
                                functionStatus="error"
                            )
                            yield f"data: {error_chunk.json()}\n\n"
                            await asyncio.sleep(0.2)

            # 완료 신호
            final_chunk = ChatStreamChunk(
                id=ai_message_id,
                content="",
                role="assistant",
                timestamp=datetime.now(),
                sessionId=session_id,
                isComplete=True
            )
            yield f"data: {final_chunk.json()}\n\n"

            # AI 응답 저장
            ai_message = ChatMessage(
                id=ai_message_id,
                content=full_content,
                role="assistant",
                timestamp=datetime.now(),
                sessionId=session_id
            )
            messages_db[session_id].append(ai_message.dict())
            update_session_message_count(session_id)

        except Exception as e:
            error_msg = f"## ❌ Direct Function Calling 오류\n\n{str(e)}"
            print(error_msg)

            error_chunk = ChatStreamChunk(
                id=ai_message_id,
                content=error_msg,
                role="assistant",
                timestamp=datetime.now(),
                sessionId=session_id,
                isComplete=True
            )
            yield f"data: {error_chunk.json()}\n\n"

    return StreamingResponse(
        generate_direct_function_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


# ===========================
# 🛠️ 새로운 AI Tools 시스템 API
# ===========================

@app.get("/api/v1/tools/status")
async def get_tools_status():
    """AI Tools 시스템 상태 조회"""
    if not TOOLS_SYSTEM_AVAILABLE:
        return {"available": False, "error": "Tools 시스템을 사용할 수 없습니다."}

    status = tool_manager.get_status()
    tools_info = tool_manager.registry.get_available_tools_info()

    return {
        "available": True,
        "status": status,
        "tools": tools_info,
        "google_auth_status": auth_service.is_authenticated() if GOOGLE_SERVICES_AVAILABLE else False
    }


@app.get("/api/v1/tools/list")
async def list_available_tools():
    """사용 가능한 모든 도구 목록 조회"""
    if not TOOLS_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Tools 시스템을 사용할 수 없습니다.")

    return {
        "tools": tool_manager.registry.get_available_tools_info(),
        "schemas": tool_manager.registry.get_openai_schemas()
    }


class EnhancedChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None
    model: str = "gpt-4o"
    use_tools: bool = True
    tool_categories: Optional[List[str]] = None  # ["calendar", "email", "crm", "utility"]


class EnhancedChatStreamChunk(BaseModel):
    id: str
    content: str
    role: str
    timestamp: datetime
    sessionId: str
    isComplete: bool = False
    # Tools 관련 필드
    toolCall: Optional[str] = None
    toolStatus: Optional[str] = None  # "running", "completed", "error"
    toolResult: Optional[Dict] = None


@app.post("/api/v1/chat/enhanced")
async def enhanced_chat_stream(request: EnhancedChatRequest):
    """새로운 AI Tools 시스템을 사용하는 향상된 채팅 API"""

    if not TOOLS_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Tools 시스템을 사용할 수 없습니다.")

    session_id = request.sessionId or str(uuid.uuid4())

    # 현재 한국 시간 정보 생성
    korea_tz = timezone(timedelta(hours=9))
    current_time_kst = datetime.now(korea_tz)

    # Google 서비스 사용 안내를 포함한 시스템 프롬프트 구성
    system_prompt = f"""당신은 NSales Pro의 영업 AI 도우미입니다. 영업 데이터 분석, 프로젝트 정보 조회, 업무 관련 질문에 도움을 주세요. 한국어로 친근하고 전문적으로 답변해주세요. 이전 대화 내용을 기억하고 문맥을 유지하여 답변하세요. 최신 정보가 필요하거나 실시간 데이터, 뉴스, 시장 동향 등을 질문받으면 웹 검색을 적극 활용하여 정확하고 최신의 정보를 제공하세요.

**현재 시간 정보:**
- 현재 날짜: {current_time_kst.strftime('%Y년 %m월 %d일 (%A)')}
- 현재 시간: {current_time_kst.strftime('%H시 %M분')}
- 시간대: 한국 표준시 (KST, UTC+9)

"오늘", "이번 주", "이번 달" 등의 시간 표현을 사용할 때는 위의 한국 시간 기준으로 해석해주세요."""

    # 세션 초기화
    if session_id not in messages_db:
        messages_db[session_id] = []
        sessions_db[session_id] = {
            "id": session_id,
            "createdAt": datetime.now(),
            "messageCount": 0,
            "model": request.model
        }

    async def generate_enhanced_stream():
        ai_message_id = str(uuid.uuid4())
        full_content = ""

        try:
            # 사용자 메시지 저장
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                content=request.message,
                role="user",
                timestamp=datetime.now(),
                sessionId=session_id
            )
            messages_db[session_id].append(user_message.dict())

            # 대화 히스토리 구성
            conversation_messages = [{"role": "system", "content": system_prompt}]
            for msg in messages_db[session_id]:
                conversation_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # 사용할 도구들 선택
            available_tools = []
            if request.use_tools:
                if request.tool_categories:
                    # 특정 카테고리의 도구만 사용
                    for category in request.tool_categories:
                        tools_in_category = tool_manager.registry.get_tools_by_category(category)
                        available_tools.extend([tool.get_schema() for tool in tools_in_category])
                else:
                    # 모든 도구 사용
                    available_tools = tool_manager.registry.get_openai_schemas()

            print(f"🛠️ Using {len(available_tools)} tools for enhanced chat")

            # OpenAI Chat Completions API 호출
            response = await client.chat.completions.create(
                model=request.model,
                messages=conversation_messages,
                tools=available_tools if available_tools else None,
                stream=True,
                temperature=0.7
            )

            # 스트리밍 응답 처리
            tool_calls = []
            current_tool_call = None

            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content_piece = chunk.choices[0].delta.content
                    full_content += content_piece

                    # 내용 스트리밍
                    stream_chunk = EnhancedChatStreamChunk(
                        id=ai_message_id,
                        content=content_piece,
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=session_id,
                        isComplete=False
                    )
                    yield f"data: {stream_chunk.json()}\n\n"

                # Tool calls 감지
                if chunk.choices[0].delta.tool_calls:
                    for tool_call_delta in chunk.choices[0].delta.tool_calls:
                        if tool_call_delta.index is not None:
                            # 새로운 tool call 시작
                            if len(tool_calls) <= tool_call_delta.index:
                                tool_calls.append({
                                    "id": "",
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""}
                                })

                            current_tool_call = tool_calls[tool_call_delta.index]

                            if tool_call_delta.id:
                                current_tool_call["id"] = tool_call_delta.id
                            if tool_call_delta.function.name:
                                current_tool_call["function"]["name"] = tool_call_delta.function.name
                            if tool_call_delta.function.arguments:
                                current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments

            # Tool calls 실행
            if tool_calls:
                print(f"🔧 Executing {len(tool_calls)} tool calls")

                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]

                    # 실행 시작 알림
                    start_chunk = EnhancedChatStreamChunk(
                        id=ai_message_id,
                        content=f"\n\n🔄 {function_name} 실행 중...\n",
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=session_id,
                        isComplete=False,
                        toolCall=function_name,
                        toolStatus="running"
                    )
                    yield f"data: {start_chunk.json()}\n\n"

                    try:
                        # 새로운 Tools 시스템으로 실행
                        mock_tool_call = type('MockToolCall', (), {
                            'function': type('MockFunction', (), {
                                'name': function_name,
                                'arguments': tool_call["function"]["arguments"]
                            })()
                        })()

                        result = await tool_manager.registry.execute_tool_call(mock_tool_call)

                        # 결과 파싱
                        try:
                            result_data = json.loads(result)
                        except:
                            result_data = {"success": False, "error": "결과 파싱 실패"}

                        # 성공 결과 스트리밍
                        if result_data.get("success"):
                            result_content = f"✅ **{function_name} 완료**\n\n"
                            if result_data.get("message"):
                                result_content += f"📋 {result_data['message']}\n\n"

                            # 구조화된 데이터가 있으면 표시
                            if result_data.get("data"):
                                result_content += f"**결과 데이터:**\n```json\n{json.dumps(result_data['data'], indent=2, ensure_ascii=False)}\n```\n\n"
                        else:
                            result_content = f"❌ **{function_name} 실패**: {result_data.get('error', '알 수 없는 오류')}\n\n"

                        full_content += result_content

                        # 결과 스트리밍
                        result_chunk = EnhancedChatStreamChunk(
                            id=ai_message_id,
                            content=result_content,
                            role="assistant",
                            timestamp=datetime.now(),
                            sessionId=session_id,
                            isComplete=False,
                            toolCall=function_name,
                            toolStatus="completed" if result_data.get("success") else "error",
                            toolResult=result_data
                        )
                        yield f"data: {result_chunk.json()}\n\n"

                    except Exception as e:
                        error_content = f"## ❌ {function_name} 실행 오류\n\n{str(e)}\n\n"
                        full_content += error_content

                        error_chunk = EnhancedChatStreamChunk(
                            id=ai_message_id,
                            content=error_content,
                            role="assistant",
                            timestamp=datetime.now(),
                            sessionId=session_id,
                            isComplete=False,
                            toolCall=function_name,
                            toolStatus="error"
                        )
                        yield f"data: {error_chunk.json()}\n\n"

                # Tool calls 결과를 바탕으로 최종 응답 생성
                if any(tool_calls):
                    # Tool calls 메시지 추가
                    messages_with_tools = conversation_messages + [
                        {"role": "assistant", "content": "", "tool_calls": [
                            {
                                "id": tc["id"],
                                "type": "function",
                                "function": {
                                    "name": tc["function"]["name"],
                                    "arguments": tc["function"]["arguments"]
                                }
                            } for tc in tool_calls
                        ]}
                    ]

                    # Tool 실행 결과를 메시지에 추가
                    for tc in tool_calls:
                        tool_result = await tool_manager.registry.execute_tool_call(
                            type('MockToolCall', (), {
                                'function': type('MockFunction', (), {
                                    'name': tc["function"]["name"],
                                    'arguments': tc["function"]["arguments"]
                                })()
                            })()
                        )
                        messages_with_tools.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": tool_result
                        })

                    # 최종 응답 생성
                    final_response = await client.chat.completions.create(
                        model=request.model,
                        messages=messages_with_tools,
                        stream=True,
                        temperature=0.7
                    )

                    summary_content = "\n\n💬 **AI 요약:**\n"
                    full_content += summary_content

                    summary_chunk = EnhancedChatStreamChunk(
                        id=ai_message_id,
                        content=summary_content,
                        role="assistant",
                        timestamp=datetime.now(),
                        sessionId=session_id,
                        isComplete=False
                    )
                    yield f"data: {summary_chunk.json()}\n\n"

                    async for chunk in final_response:
                        if chunk.choices[0].delta.content:
                            content_piece = chunk.choices[0].delta.content
                            full_content += content_piece

                            stream_chunk = EnhancedChatStreamChunk(
                                id=ai_message_id,
                                content=content_piece,
                                role="assistant",
                                timestamp=datetime.now(),
                                sessionId=session_id,
                                isComplete=False
                            )
                            yield f"data: {stream_chunk.json()}\n\n"

            # 완료 신호
            final_chunk = EnhancedChatStreamChunk(
                id=ai_message_id,
                content="",
                role="assistant",
                timestamp=datetime.now(),
                sessionId=session_id,
                isComplete=True
            )
            yield f"data: {final_chunk.json()}\n\n"

            # AI 응답 저장
            ai_message = ChatMessage(
                id=ai_message_id,
                content=full_content,
                role="assistant",
                timestamp=datetime.now(),
                sessionId=session_id
            )
            messages_db[session_id].append(ai_message.dict())
            update_session_message_count(session_id)

        except Exception as e:
            error_msg = f"## ❌ Enhanced Chat 오류\n\n{str(e)}"
            print(error_msg)

            error_chunk = EnhancedChatStreamChunk(
                id=ai_message_id,
                content=error_msg,
                role="assistant",
                timestamp=datetime.now(),
                sessionId=session_id,
                isComplete=True,
                toolStatus="error"
            )
            yield f"data: {error_chunk.json()}\n\n"

    return StreamingResponse(
        generate_enhanced_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
