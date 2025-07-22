"""
Base classes for AI Tools
모든 AI 도구의 기본 클래스와 인터페이스 정의
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
import json
import traceback


@dataclass
class ToolResult:
    """도구 실행 결과"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        result = {
            "success": self.success
        }
        
        if self.success:
            result["data"] = self.data
            if self.message:
                result["message"] = self.message
        else:
            result["error"] = self.error
            
        return json.dumps(result, ensure_ascii=False)


class ToolError(Exception):
    """도구 실행 중 발생하는 예외"""
    pass


class BaseTool(ABC):
    """모든 AI 도구의 기본 클래스"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """OpenAI Function Calling용 스키마 반환"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """도구 실행"""
        pass
    
    async def safe_execute(self, **kwargs) -> str:
        """안전한 도구 실행 (예외 처리 포함)"""
        try:
            result = await self.execute(**kwargs)
            return result.to_json()
        except ToolError as e:
            return ToolResult(
                success=False,
                error=f"{self.name} 도구 오류: {str(e)}"
            ).to_json()
        except Exception as e:
            # 디버깅을 위한 상세 에러 로깅
            error_details = f"{self.name} 예상치 못한 오류: {str(e)}"
            print(f"Tool Error: {error_details}")
            print(f"Traceback: {traceback.format_exc()}")
            
            return ToolResult(
                success=False,
                error=error_details
            ).to_json()