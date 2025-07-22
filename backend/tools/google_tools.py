"""
Google Services Tools
Google 캘린더, Gmail을 위한 AI 도구들
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from .base import BaseTool, ToolResult, ToolError

# 기존 Google 서비스 import
try:
    from google_services import auth_service, calendar_service, gmail_service, CalendarEvent, EmailMessage
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google 서비스를 사용할 수 없습니다.")


class GoogleCalendarViewTool(BaseTool):
    """Google 캘린더 일정 조회 도구"""
    
    def __init__(self):
        super().__init__(
            name="get_calendar_events",
            description="사용자의 Google 캘린더에서 일정을 조회합니다. '오늘 일정', '이번주 일정', '이번달 일정' 등의 자연어 요청을 처리합니다."
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "시작 날짜 (YYYY-MM-DD 형식). 예: 오늘=2025-07-22, 이번주=2025-07-22, 이번달=2025-07-01"
                        },
                        "end_date": {
                            "type": "string", 
                            "description": "종료 날짜 (YYYY-MM-DD 형식). 예: 오늘=2025-07-22, 이번주=2025-07-28, 이번달=2025-07-31"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "최대 조회할 일정 수 (기본값: 50)",
                            "default": 50
                        },
                        "month": {
                            "type": "string",
                            "description": "특정 월 조회 (YYYY-MM 형식, 예: 2025-07). 이 파라미터를 사용하면 start_date, end_date는 무시됩니다."
                        }
                    },
                    "required": []
                }
            }
        }
    
    async def execute(self, start_date: str = None, end_date: str = None, max_results: int = 50, month: str = None, **kwargs) -> ToolResult:
        if not GOOGLE_AVAILABLE:
            raise ToolError("Google 서비스를 사용할 수 없습니다.")
        
        if not auth_service.is_authenticated():
            raise ToolError("Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요.")
        
        try:
            # month 파라미터 처리
            if month:
                try:
                    if '-' in month:
                        year, month_num = month.split('-')
                        year, month_num = int(year), int(month_num)
                    else:
                        year = datetime.now().year
                        month_num = int(month)
                        
                    first_day = datetime(year, month_num, 1)
                    if month_num == 12:
                        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
                    else:
                        last_day = datetime(year, month_num + 1, 1) - timedelta(days=1)
                        
                    start_date = first_day.strftime('%Y-%m-%d')
                    end_date = last_day.strftime('%Y-%m-%d')
                except:
                    raise ToolError(f"잘못된 month 파라미터입니다: {month}. YYYY-MM 형식으로 입력해주세요.")
            
            # 기본 날짜 설정
            if not start_date or not end_date:
                today = datetime.now()
                if not start_date:
                    start_date = today.strftime('%Y-%m-%d')
                if not end_date:
                    end_date = today.strftime('%Y-%m-%d')
            
            # 일정 조회
            events = calendar_service.get_events(start_date, end_date, max_results)
            
            if not events:
                return ToolResult(
                    success=True,
                    data=[],
                    message=f"{start_date}부터 {end_date}까지 등록된 일정이 없습니다."
                )
            
            # 일정 정보 포맷팅
            formatted_events = []
            for event in events:
                start_time = event['start']
                end_time = event['end']
                
                # 날짜/시간 포맷팅
                if 'T' in start_time:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    time_str = f"{start_dt.strftime('%m/%d %H:%M')} - {end_dt.strftime('%H:%M')}"
                else:
                    time_str = f"{start_time} (종일)"
                
                formatted_events.append({
                    "id": event['id'],
                    "title": event['summary'],
                    "time": time_str,
                    "location": event['location'] or "장소 미정",
                    "description": event['description'] or "설명 없음",
                    "attendees": event['attendees']
                })
            
            return ToolResult(
                success=True,
                data=formatted_events,
                message=f"{start_date}부터 {end_date}까지 {len(events)}개의 일정이 있습니다."
            )
            
        except Exception as e:
            raise ToolError(f"일정 조회 중 오류가 발생했습니다: {str(e)}")


class GoogleCalendarCreateTool(BaseTool):
    """Google 캘린더 일정 생성 도구"""
    
    def __init__(self):
        super().__init__(
            name="create_calendar_event",
            description="Google 캘린더에 새로운 일정을 생성합니다. 회의, 약속, 업무 일정 등을 추가할 때 사용합니다."
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "일정 제목 (예: '팀 미팅', '고객 상담', '프로젝트 회의')"
                        },
                        "description": {
                            "type": "string",
                            "description": "일정 상세 설명 (선택사항)"
                        },
                        "start_datetime": {
                            "type": "string",
                            "description": "시작 일시 (ISO 8601 형식: 2025-07-22T15:00:00+09:00)"
                        },
                        "end_datetime": {
                            "type": "string",
                            "description": "종료 일시 (ISO 8601 형식: 2025-07-22T16:00:00+09:00)"
                        },
                        "location": {
                            "type": "string",
                            "description": "장소 (예: '회의실 A', '온라인', '카페')"
                        },
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "참석자 이메일 목록 (선택사항)"
                        }
                    },
                    "required": ["summary", "start_datetime", "end_datetime"]
                }
            }
        }
    
    async def execute(self, summary: str, start_datetime: str, end_datetime: str, 
                     description: str = "", location: str = "", attendees: List[str] = None, **kwargs) -> ToolResult:
        if not GOOGLE_AVAILABLE:
            raise ToolError("Google 서비스를 사용할 수 없습니다.")
        
        if not auth_service.is_authenticated():
            raise ToolError("Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요.")
        
        try:
            # 날짜/시간 유효성 검사
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            
            if start_dt >= end_dt:
                raise ToolError("시작 시간이 종료 시간보다 늦거나 같습니다.")
            
            # 일정 생성
            event_data = CalendarEvent(
                summary=summary,
                description=description,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=location,
                attendees=attendees or []
            )
            
            result = calendar_service.create_event(event_data)
            
            if result['success']:
                return ToolResult(
                    success=True,
                    data={
                        "event_id": result['event_id'],
                        "event_link": result.get('event_link', '')
                    },
                    message=result['message']
                )
            else:
                raise ToolError(result['error'])
                
        except ValueError:
            raise ToolError("날짜/시간 형식이 올바르지 않습니다. ISO 8601 형식을 사용해주세요.")
        except Exception as e:
            raise ToolError(f"일정 생성 중 오류가 발생했습니다: {str(e)}")


class GoogleCalendarFindFreeTool(BaseTool):
    """빈 시간 찾기 도구"""
    
    def __init__(self):
        super().__init__(
            name="find_free_time",
            description="지정된 기간에서 비어있는 시간대를 찾습니다. 회의 일정을 잡을 때 사용합니다."
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "검색 시작 날짜 (YYYY-MM-DD 형식)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "검색 종료 날짜 (YYYY-MM-DD 형식)"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "필요한 시간 (분 단위, 기본값: 60분)",
                            "default": 60
                        },
                        "work_hours_only": {
                            "type": "boolean",
                            "description": "업무 시간(9-18시)만 검색할지 여부 (기본값: true)",
                            "default": True
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            }
        }
    
    async def execute(self, start_date: str, end_date: str, duration_minutes: int = 60, 
                     work_hours_only: bool = True, **kwargs) -> ToolResult:
        if not GOOGLE_AVAILABLE:
            raise ToolError("Google 서비스를 사용할 수 없습니다.")
        
        if not auth_service.is_authenticated():
            raise ToolError("Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요.")
        
        try:
            # 기간 내 모든 일정 조회
            events = calendar_service.get_events(start_date, end_date)
            
            # 빈 시간 계산
            free_slots = []
            current_date = datetime.fromisoformat(start_date)
            end_date_dt = datetime.fromisoformat(end_date)
            
            while current_date.date() <= end_date_dt.date():
                if work_hours_only:
                    day_start = current_date.replace(hour=9, minute=0, second=0, microsecond=0)
                    day_end = current_date.replace(hour=18, minute=0, second=0, microsecond=0)
                else:
                    day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    day_end = current_date.replace(hour=23, minute=59, second=59, microsecond=0)
                
                # 해당 날짜의 일정들 필터링 및 정렬
                day_events = []
                for event in events:
                    event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                    if event_start.date() == current_date.date():
                        day_events.append(event)
                
                day_events.sort(key=lambda x: x['start'])
                
                # 빈 시간 슬롯 찾기
                current_time = day_start
                for event in day_events:
                    event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                    
                    # 이벤트 시작 전까지 빈 시간 확인
                    if (event_start - current_time).total_seconds() >= duration_minutes * 60:
                        free_slots.append({
                            "date": current_date.strftime('%Y-%m-%d'),
                            "start_time": current_time.strftime('%H:%M'),
                            "end_time": event_start.strftime('%H:%M'),
                            "duration_minutes": int((event_start - current_time).total_seconds() / 60)
                        })
                    
                    current_time = max(current_time, event_end)
                
                # 마지막 일정 후 빈 시간 확인
                if (day_end - current_time).total_seconds() >= duration_minutes * 60:
                    free_slots.append({
                        "date": current_date.strftime('%Y-%m-%d'),
                        "start_time": current_time.strftime('%H:%M'),
                        "end_time": day_end.strftime('%H:%M'),
                        "duration_minutes": int((day_end - current_time).total_seconds() / 60)
                    })
                
                current_date += timedelta(days=1)
            
            # 요청된 시간 이상의 슬롯만 필터링
            suitable_slots = [slot for slot in free_slots if slot['duration_minutes'] >= duration_minutes]
            
            if not suitable_slots:
                return ToolResult(
                    success=True,
                    data=[],
                    message=f"{start_date}부터 {end_date}까지 {duration_minutes}분 이상의 빈 시간이 없습니다."
                )
            
            return ToolResult(
                success=True,
                data=suitable_slots[:10],  # 최대 10개만 반환
                message=f"{duration_minutes}분 이상의 빈 시간 {len(suitable_slots)}개를 찾았습니다."
            )
            
        except Exception as e:
            raise ToolError(f"빈 시간 검색 중 오류가 발생했습니다: {str(e)}")


class GmailSendTool(BaseTool):
    """Gmail 이메일 전송 도구"""
    
    def __init__(self):
        super().__init__(
            name="send_email",
            description="Gmail을 통해 이메일을 전송합니다. 업무 메일, 알림, 일정 공유 등에 사용합니다."
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
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
                            "description": "이메일 본문 내용"
                        },
                        "cc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "참조(CC) 이메일 주소 목록 (선택사항)"
                        },
                        "html_body": {
                            "type": "string",
                            "description": "HTML 형식의 이메일 본문 (선택사항)"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        }
    
    async def execute(self, to: List[str], subject: str, body: str, 
                     cc: List[str] = None, html_body: str = "", **kwargs) -> ToolResult:
        if not GOOGLE_AVAILABLE:
            raise ToolError("Google 서비스를 사용할 수 없습니다.")
        
        if not auth_service.is_authenticated():
            raise ToolError("Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요.")
        
        try:
            email_data = EmailMessage(
                to=to,
                subject=subject,
                body=body,
                cc=cc or [],
                html_body=html_body
            )
            
            result = gmail_service.send_email(email_data)
            
            if result['success']:
                return ToolResult(
                    success=True,
                    data={"message_id": result['message_id']},
                    message=result['message']
                )
            else:
                raise ToolError(result['error'])
                
        except Exception as e:
            raise ToolError(f"이메일 전송 중 오류가 발생했습니다: {str(e)}")


class GmailViewTool(BaseTool):
    """Gmail 이메일 조회 도구"""
    
    def __init__(self):
        super().__init__(
            name="get_emails",
            description="Gmail에서 이메일 목록을 조회합니다. 최근 메일 확인, 중요 메일 검색, 특정 발신자 메일 찾기 등에 사용합니다."
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Gmail 검색 쿼리 (예: 'from:sender@email.com', 'subject:중요', 'is:unread' 등)"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "최대 조회할 이메일 수 (기본값: 10)",
                            "default": 10
                        }
                    },
                    "required": []
                }
            }
        }
    
    async def execute(self, query: str = "", max_results: int = 10, **kwargs) -> ToolResult:
        if not GOOGLE_AVAILABLE:
            raise ToolError("Google 서비스를 사용할 수 없습니다.")
        
        if not auth_service.is_authenticated():
            raise ToolError("Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요.")
        
        try:
            messages = gmail_service.get_messages(query, max_results)
            
            if not messages:
                query_desc = f"'{query}' 조건의 " if query else ""
                return ToolResult(
                    success=True,
                    data=[],
                    message=f"{query_desc}이메일이 없습니다."
                )
            
            return ToolResult(
                success=True,
                data=messages,
                message=f"{len(messages)}개의 이메일을 찾았습니다."
            )
            
        except Exception as e:
            raise ToolError(f"이메일 조회 중 오류가 발생했습니다: {str(e)}")