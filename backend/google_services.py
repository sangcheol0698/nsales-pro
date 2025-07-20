"""
Google Services Integration
Google Calendar, Gmail API와 AI 통합을 위한 서비스 클래스들
"""

import os
import json
import pickle
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google API 스코프 정의
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

@dataclass
class CalendarEvent:
    """캘린더 이벤트 데이터 클래스"""
    id: Optional[str] = None
    summary: str = ""
    description: str = ""
    start_datetime: str = ""
    end_datetime: str = ""
    location: str = ""
    attendees: List[str] = None
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []

@dataclass
class EmailMessage:
    """이메일 메시지 데이터 클래스"""
    to: List[str]
    subject: str
    body: str
    cc: List[str] = None
    bcc: List[str] = None
    html_body: str = ""
    
    def __post_init__(self):
        if self.cc is None:
            self.cc = []
        if self.bcc is None:
            self.bcc = []

class GoogleAuthService:
    """Google OAuth2 인증 서비스"""
    
    def __init__(self):
        self.credentials_file = "credentials.json"
        self.token_file = "token.pickle"
        self.redirect_uri = "http://localhost:8000/api/v1/google/callback"
        
    def get_authorization_url(self) -> str:
        """OAuth2 인증 URL 생성"""
        try:
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'  # 항상 동의 화면 표시
            )
            
            return auth_url
            
        except Exception as e:
            print(f"Authorization URL 생성 실패: {e}")
            return ""
    
    def handle_callback(self, code: str) -> bool:
        """OAuth2 콜백 처리 및 토큰 저장"""
        try:
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            flow.fetch_token(code=code)
            
            # 토큰을 파일에 저장
            with open(self.token_file, 'wb') as token:
                pickle.dump(flow.credentials, token)
            
            print("Google 인증 성공!")
            return True
            
        except Exception as e:
            print(f"인증 콜백 처리 실패: {e}")
            return False
    
    def get_credentials(self) -> Optional[Credentials]:
        """저장된 인증 정보 로드"""
        creds = None
        
        # 토큰 파일에서 인증 정보 로드
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # 토큰이 유효하지 않거나 만료된 경우 갱신
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # 갱신된 토큰 저장
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"토큰 갱신 실패: {e}")
                return None
        
        return creds if creds and creds.valid else None
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        return self.get_credentials() is not None

class GoogleCalendarService:
    """Google Calendar API 서비스"""
    
    def __init__(self, auth_service: GoogleAuthService):
        self.auth_service = auth_service
        self._service = None
    
    def _get_service(self):
        """Calendar API 서비스 객체 생성"""
        if not self._service:
            creds = self.auth_service.get_credentials()
            if not creds:
                raise Exception("Google 인증이 필요합니다.")
            
            self._service = build('calendar', 'v3', credentials=creds)
        
        return self._service
    
    async def get_events(self, start_date: str, end_date: str, max_results: int = 50) -> List[Dict]:
        """캘린더 이벤트 조회"""
        try:
            service = self._get_service()
            
            # 날짜 형식 변환 (ISO 8601)
            start_datetime = f"{start_date}T00:00:00Z"
            end_datetime = f"{end_date}T23:59:59Z"
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_datetime,
                timeMax=end_datetime,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # 이벤트 정보 정리
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', '제목 없음'),
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'attendees': [att.get('email') for att in event.get('attendees', [])]
                })
            
            return formatted_events
            
        except HttpError as e:
            print(f"Calendar API 오류: {e}")
            return []
        except Exception as e:
            print(f"일정 조회 실패: {e}")
            return []
    
    async def create_event(self, event_data: CalendarEvent) -> Dict:
        """캘린더 이벤트 생성"""
        try:
            service = self._get_service()
            
            # 이벤트 데이터 구성
            event_body = {
                'summary': event_data.summary,
                'description': event_data.description,
                'start': {
                    'dateTime': event_data.start_datetime,
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': event_data.end_datetime,
                    'timeZone': 'Asia/Seoul',
                },
            }
            
            # 선택적 필드 추가
            if event_data.location:
                event_body['location'] = event_data.location
            
            if event_data.attendees:
                event_body['attendees'] = [{'email': email} for email in event_data.attendees]
            
            # 이벤트 생성
            event = service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()
            
            return {
                'success': True,
                'event_id': event['id'],
                'event_link': event.get('htmlLink', ''),
                'message': f"'{event_data.summary}' 일정이 생성되었습니다."
            }
            
        except HttpError as e:
            return {
                'success': False,
                'error': f"Calendar API 오류: {e}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"일정 생성 실패: {e}"
            }
    
    async def update_event(self, event_id: str, event_data: CalendarEvent) -> Dict:
        """캘린더 이벤트 수정"""
        try:
            service = self._get_service()
            
            # 기존 이벤트 조회
            existing_event = service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # 업데이트할 필드만 수정
            if event_data.summary:
                existing_event['summary'] = event_data.summary
            if event_data.description:
                existing_event['description'] = event_data.description
            if event_data.start_datetime:
                existing_event['start'] = {
                    'dateTime': event_data.start_datetime,
                    'timeZone': 'Asia/Seoul'
                }
            if event_data.end_datetime:
                existing_event['end'] = {
                    'dateTime': event_data.end_datetime,
                    'timeZone': 'Asia/Seoul'
                }
            if event_data.location:
                existing_event['location'] = event_data.location
            
            # 이벤트 업데이트
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=existing_event
            ).execute()
            
            return {
                'success': True,
                'event_id': updated_event['id'],
                'message': f"일정이 수정되었습니다."
            }
            
        except HttpError as e:
            return {
                'success': False,
                'error': f"Calendar API 오류: {e}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"일정 수정 실패: {e}"
            }
    
    async def delete_event(self, event_id: str) -> Dict:
        """캘린더 이벤트 삭제"""
        try:
            service = self._get_service()
            
            service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return {
                'success': True,
                'message': "일정이 삭제되었습니다."
            }
            
        except HttpError as e:
            return {
                'success': False,
                'error': f"Calendar API 오류: {e}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"일정 삭제 실패: {e}"
            }

class GoogleGmailService:
    """Google Gmail API 서비스"""
    
    def __init__(self, auth_service: GoogleAuthService):
        self.auth_service = auth_service
        self._service = None
    
    def _get_service(self):
        """Gmail API 서비스 객체 생성"""
        if not self._service:
            creds = self.auth_service.get_credentials()
            if not creds:
                raise Exception("Google 인증이 필요합니다.")
            
            self._service = build('gmail', 'v1', credentials=creds)
        
        return self._service
    
    async def send_email(self, email_data: EmailMessage) -> Dict:
        """이메일 전송"""
        try:
            import base64
            import email.mime.text
            import email.mime.multipart
            
            service = self._get_service()
            
            # 이메일 메시지 구성
            if email_data.html_body:
                # HTML 이메일
                message = email.mime.multipart.MIMEMultipart('alternative')
                text_part = email.mime.text.MIMEText(email_data.body, 'plain', 'utf-8')
                html_part = email.mime.text.MIMEText(email_data.html_body, 'html', 'utf-8')
                message.attach(text_part)
                message.attach(html_part)
            else:
                # 텍스트 이메일
                message = email.mime.text.MIMEText(email_data.body, 'plain', 'utf-8')
            
            message['To'] = ', '.join(email_data.to)
            message['Subject'] = email_data.subject
            
            if email_data.cc:
                message['Cc'] = ', '.join(email_data.cc)
            if email_data.bcc:
                message['Bcc'] = ', '.join(email_data.bcc)
            
            # 메시지 인코딩
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # 이메일 전송
            result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message_id': result['id'],
                'message': f"이메일이 {', '.join(email_data.to)}에게 전송되었습니다."
            }
            
        except HttpError as e:
            return {
                'success': False,
                'error': f"Gmail API 오류: {e}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"이메일 전송 실패: {e}"
            }
    
    async def get_messages(self, query: str = "", max_results: int = 10) -> List[Dict]:
        """이메일 메시지 조회"""
        try:
            service = self._get_service()
            
            # 메시지 목록 조회
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # 메시지 상세 정보 조회
            detailed_messages = []
            for message in messages:
                msg_detail = service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()
                
                # 헤더 정보 추출
                headers = msg_detail['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '제목 없음')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '발신자 불명')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # 본문 내용 추출 (간단한 버전)
                body = ""
                if 'parts' in msg_detail['payload']:
                    for part in msg_detail['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            if 'data' in part['body']:
                                import base64
                                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                break
                elif msg_detail['payload']['mimeType'] == 'text/plain':
                    if 'data' in msg_detail['payload']['body']:
                        import base64
                        body = base64.urlsafe_b64decode(msg_detail['payload']['body']['data']).decode('utf-8')
                
                detailed_messages.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body[:500] + "..." if len(body) > 500 else body,  # 본문 미리보기
                    'snippet': msg_detail.get('snippet', '')
                })
            
            return detailed_messages
            
        except HttpError as e:
            print(f"Gmail API 오류: {e}")
            return []
        except Exception as e:
            print(f"메시지 조회 실패: {e}")
            return []

# 글로벌 서비스 인스턴스
auth_service = GoogleAuthService()
calendar_service = GoogleCalendarService(auth_service)
gmail_service = GoogleGmailService(auth_service)