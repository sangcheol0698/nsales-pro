"""
AI 기반 채팅 제목 자동 생성 모듈
"""
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TitleGenerator:
    """채팅 대화 내용을 분석하여 자동으로 제목을 생성하는 클래스"""
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.model = "gpt-3.5-turbo"  # 빠르고 비용 효율적
        
    def should_generate_title(self, messages: List[Dict[str, Any]], current_title: str) -> bool:
        """제목 생성이 필요한지 판단"""
        if len(messages) < 2:
            return False
            
        # 기본 제목 패턴 확인 ("새 채팅 N" 형태)
        if not current_title.startswith("새 채팅"):
            return False
            
        # 사용자와 어시스턴트 메시지가 최소 1개씩 있는지 확인
        user_messages = [m for m in messages if m.get('role') == 'user']
        assistant_messages = [m for m in messages if m.get('role') == 'assistant']
        
        return len(user_messages) >= 1 and len(assistant_messages) >= 1
    
    def _create_conversation_summary(self, messages: List[Dict[str, Any]]) -> str:
        """대화 내용을 요약하여 제목 생성에 적합한 형태로 변환"""
        summary_parts = []
        
        # 처음 3개 메시지만 사용 (토큰 절약)
        recent_messages = messages[:3]
        
        for msg in recent_messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            
            if role == 'user':
                # 사용자 메시지에서 핵심 키워드 추출
                summary_parts.append(f"사용자: {content[:100]}")
            elif role == 'assistant':
                # 어시스턴트 응답에서 주제 파악
                summary_parts.append(f"AI: {content[:100]}")
        
        return "\n".join(summary_parts)
    
    async def generate_title(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """대화 내용을 바탕으로 제목 생성"""
        try:
            conversation_summary = self._create_conversation_summary(messages)
            
            # 제목 생성 프롬프트
            prompt = f"""다음 채팅 대화의 핵심 주제를 바탕으로 간결하고 명확한 제목을 생성해주세요.

규칙:
- 15자 이내로 작성
- 대화의 핵심 주제 반영
- 명사형으로 작성
- 이모지 사용 금지
- 영업/업무 관련 키워드 우선 사용
- 한국어로 작성

대화 내용:
{conversation_summary}

제목:"""

            response = await self.client.chat.completions.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 채팅 제목을 생성하는 AI입니다. 간결하고 정확한 제목을 만들어주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7,
                timeout=10.0
            )
            
            generated_title = response.choices[0].message.content.strip()
            
            # 제목 유효성 검사
            if not generated_title or len(generated_title) > 15:
                logger.warning(f"Generated title validation failed: {generated_title}")
                return None
                
            logger.info(f"Generated title: {generated_title}")
            return generated_title
            
        except Exception as e:
            logger.error(f"Title generation failed: {str(e)}")
            return None
    
    def get_fallback_title(self, messages: List[Dict[str, Any]]) -> str:
        """제목 생성 실패시 사용할 폴백 제목"""
        # 첫 번째 사용자 메시지의 일부를 사용
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '').strip()
                if content:
                    # 첫 15자 사용
                    fallback = content[:15]
                    if len(content) > 15:
                        fallback += "..."
                    return fallback
        
        return f"채팅 {datetime.now().strftime('%m월%d일')}"