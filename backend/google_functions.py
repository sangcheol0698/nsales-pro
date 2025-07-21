"""
Google Services AI Functions
AI가 사용할 수 있는 Google Calendar, Gmail 함수들
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from google_services import (
    auth_service, 
    calendar_service, 
    gmail_service,
    CalendarEvent,
    EmailMessage
)

# Google 서비스용 AI 도구 정의
GOOGLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "사용자의 Google 캘린더에서 일정을 조회합니다. '오늘 일정', '이번주 일정', '이번달 일정', '내일 일정' 등의 자연어 요청을 처리합니다. 현재 날짜는 2025년 7월 21일입니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "시작 날짜 (YYYY-MM-DD 형식). 예: 오늘=2025-07-21, 이번주=2025-07-21, 이번달=2025-07-01, 내일=2025-07-22"
                    },
                    "end_date": {
                        "type": "string", 
                        "description": "종료 날짜 (YYYY-MM-DD 형식). 예: 오늘=2025-07-21, 이번주=2025-07-27, 이번달=2025-07-31, 내일=2025-07-22"
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
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Google 캘린더에 새로운 일정을 생성합니다. 회의, 약속, 업무 일정 등을 추가할 때 사용합니다.",
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
                        "description": "시작 일시 (ISO 8601 형식: 2025-07-21T15:00:00+09:00)"
                    },
                    "end_datetime": {
                        "type": "string",
                        "description": "종료 일시 (ISO 8601 형식: 2025-07-21T16:00:00+09:00)"
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
    },
    {
        "type": "function",
        "function": {
            "name": "update_calendar_event",
            "description": "기존 Google 캘린더 일정을 수정합니다. 시간 변경, 제목 수정, 참석자 추가 등에 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "수정할 일정의 ID"
                    },
                    "summary": {
                        "type": "string",
                        "description": "새로운 일정 제목 (선택사항)"
                    },
                    "description": {
                        "type": "string",
                        "description": "새로운 일정 설명 (선택사항)"
                    },
                    "start_datetime": {
                        "type": "string",
                        "description": "새로운 시작 일시 (ISO 8601 형식, 선택사항)"
                    },
                    "end_datetime": {
                        "type": "string",
                        "description": "새로운 종료 일시 (ISO 8601 형식, 선택사항)"
                    },
                    "location": {
                        "type": "string",
                        "description": "새로운 장소 (선택사항)"
                    }
                },
                "required": ["event_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_calendar_event",
            "description": "Google 캘린더에서 일정을 삭제합니다. 취소된 회의나 불필요한 일정을 제거할 때 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "삭제할 일정의 ID"
                    }
                },
                "required": ["event_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Gmail을 통해 이메일을 전송합니다. 업무 메일, 알림, 일정 공유 등에 사용합니다.",
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_emails",
            "description": "Gmail에서 이메일 목록을 조회합니다. 최근 메일 확인, 중요 메일 검색, 특정 발신자 메일 찾기 등에 사용합니다.",
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
    },
    {
        "type": "function",
        "function": {
            "name": "find_free_time",
            "description": "지정된 기간에서 비어있는 시간대를 찾습니다. 회의 일정을 잡을 때 사용합니다.",
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
]

# AI 함수 구현
def get_calendar_events(start_date: str = None, end_date: str = None, max_results: int = 50, **kwargs) -> str:
    """캘린더 일정 조회 함수"""
    try:
        if not auth_service.is_authenticated():
            return json.dumps({
                "error": "Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요."
            }, ensure_ascii=False)
        
        # 파라미터 검증 및 변환
        if 'month' in kwargs:
            # month 파라미터가 있는 경우 start_date, end_date로 변환
            month_str = kwargs['month']
            try:
                if '-' in month_str:  # YYYY-MM 형식
                    year, month = month_str.split('-')
                    year, month = int(year), int(month)
                else:  # 현재 연도의 월로 가정
                    from datetime import datetime
                    year = datetime.now().year
                    month = int(month_str)
                    
                # 해당 월의 첫째 날과 마지막 날 계산
                from datetime import datetime, timedelta
                first_day = datetime(year, month, 1)
                if month == 12:
                    last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
                    
                start_date = first_day.strftime('%Y-%m-%d')
                end_date = last_day.strftime('%Y-%m-%d')
            except:
                return json.dumps({
                    "error": f"잘못된 month 파라미터입니다: {month_str}. YYYY-MM 형식으로 입력해주세요."
                }, ensure_ascii=False)
        
        # 현재 날짜 기반으로 기본값 설정
        if not start_date or not end_date:
            from datetime import datetime
            today = datetime.now()
            if not start_date:
                start_date = today.strftime('%Y-%m-%d')
            if not end_date:
                end_date = today.strftime('%Y-%m-%d')
        
        events = calendar_service.get_events(start_date, end_date, max_results)
        
        if not events:
            return json.dumps({
                "message": f"{start_date}부터 {end_date}까지 등록된 일정이 없습니다.",
                "events": []
            }, ensure_ascii=False)
        
        # 일정 정보를 자연스럽게 포맷팅
        formatted_events = []
        for event in events:
            start_time = event['start']
            end_time = event['end']
            
            # 날짜/시간 포맷팅
            if 'T' in start_time:  # 시간이 포함된 경우
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                time_str = f"{start_dt.strftime('%m/%d %H:%M')} - {end_dt.strftime('%H:%M')}"
            else:  # 종일 일정
                time_str = f"{start_time} (종일)"
            
            formatted_events.append({
                "id": event['id'],
                "title": event['summary'],
                "time": time_str,
                "location": event['location'] or "장소 미정",
                "description": event['description'] or "설명 없음",
                "attendees": event['attendees']
            })
        
        return json.dumps({
            "message": f"{start_date}부터 {end_date}까지 {len(events)}개의 일정이 있습니다.",
            "events": formatted_events
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"일정 조회 중 오류가 발생했습니다: {str(e)}"
        }, ensure_ascii=False)

def create_calendar_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    location: str = "",
    attendees: List[str] = None
) -> str:
    """캘린더 일정 생성 함수"""
    try:
        if not auth_service.is_authenticated():
            return json.dumps({
                "error": "Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요."
            }, ensure_ascii=False)
        
        # 날짜/시간 유효성 검사
        try:
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            
            if start_dt >= end_dt:
                return json.dumps({
                    "error": "시작 시간이 종료 시간보다 늦거나 같습니다."
                }, ensure_ascii=False)
                
        except ValueError:
            return json.dumps({
                "error": "날짜/시간 형식이 올바르지 않습니다. ISO 8601 형식을 사용해주세요."
            }, ensure_ascii=False)
        
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
            return json.dumps({
                "success": True,
                "message": result['message'],
                "event_id": result['event_id'],
                "event_link": result.get('event_link', '')
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "error": result['error']
            }, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({
            "error": f"일정 생성 중 오류가 발생했습니다: {str(e)}"
        }, ensure_ascii=False)

def update_calendar_event(
    event_id: str,
    summary: str = "",
    description: str = "",
    start_datetime: str = "",
    end_datetime: str = "",
    location: str = ""
) -> str:
    """캘린더 일정 수정 함수"""
    try:
        if not auth_service.is_authenticated():
            return json.dumps({
                "error": "Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요."
            }, ensure_ascii=False)
        
        # 수정할 데이터 구성
        event_data = CalendarEvent(
            summary=summary,
            description=description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=location
        )
        
        result = calendar_service.update_event(event_id, event_data)
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"일정 수정 중 오류가 발생했습니다: {str(e)}"
        }, ensure_ascii=False)

def delete_calendar_event(event_id: str) -> str:
    """캘린더 일정 삭제 함수"""
    try:
        if not auth_service.is_authenticated():
            return json.dumps({
                "error": "Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요."
            }, ensure_ascii=False)
        
        result = calendar_service.delete_event(event_id)
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"일정 삭제 중 오류가 발생했습니다: {str(e)}"
        }, ensure_ascii=False)

def send_email(
    to: List[str],
    subject: str,
    body: str,
    cc: List[str] = None,
    html_body: str = ""
) -> str:
    """이메일 전송 함수"""
    try:
        if not auth_service.is_authenticated():
            return json.dumps({
                "error": "Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요."
            }, ensure_ascii=False)
        
        # 이메일 데이터 구성
        email_data = EmailMessage(
            to=to,
            subject=subject,
            body=body,
            cc=cc or [],
            html_body=html_body
        )
        
        result = gmail_service.send_email(email_data)
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"이메일 전송 중 오류가 발생했습니다: {str(e)}"
        }, ensure_ascii=False)

def get_emails(query: str = "", max_results: int = 10) -> str:
    """이메일 조회 함수"""
    try:
        if not auth_service.is_authenticated():
            return json.dumps({
                "error": "Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요."
            }, ensure_ascii=False)
        
        messages = gmail_service.get_messages(query, max_results)
        
        if not messages:
            query_desc = f"'{query}' 조건의 " if query else ""
            return json.dumps({
                "message": f"{query_desc}이메일이 없습니다.",
                "emails": []
            }, ensure_ascii=False)
        
        return json.dumps({
            "message": f"{len(messages)}개의 이메일을 찾았습니다.",
            "emails": messages
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"이메일 조회 중 오류가 발생했습니다: {str(e)}"
        }, ensure_ascii=False)

def find_free_time(
    start_date: str,
    end_date: str,
    duration_minutes: int = 60,
    work_hours_only: bool = True
) -> str:
    """빈 시간 찾기 함수"""
    try:
        if not auth_service.is_authenticated():
            return json.dumps({
                "error": "Google 인증이 필요합니다. /api/v1/google/auth 에서 인증을 완료해주세요."
            }, ensure_ascii=False)
        
        # 기간 내 모든 일정 조회
        events = calendar_service.get_events(start_date, end_date)
        
        # 빈 시간 계산 로직
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
            
            # 해당 날짜의 일정들 필터링
            day_events = []
            for event in events:
                event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                if event_start.date() == current_date.date():
                    day_events.append(event)
            
            # 시간순 정렬
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
            return json.dumps({
                "message": f"{start_date}부터 {end_date}까지 {duration_minutes}분 이상의 빈 시간이 없습니다.",
                "free_slots": []
            }, ensure_ascii=False)
        
        return json.dumps({
            "message": f"{duration_minutes}분 이상의 빈 시간 {len(suitable_slots)}개를 찾았습니다.",
            "free_slots": suitable_slots[:10]  # 최대 10개만 반환
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"빈 시간 검색 중 오류가 발생했습니다: {str(e)}"
        }, ensure_ascii=False)

# 함수 매핑
FUNCTION_MAP = {
    "get_calendar_events": get_calendar_events,
    "create_calendar_event": create_calendar_event,
    "update_calendar_event": update_calendar_event,
    "delete_calendar_event": delete_calendar_event,
    "send_email": send_email,
    "get_emails": get_emails,
    "find_free_time": find_free_time,
}