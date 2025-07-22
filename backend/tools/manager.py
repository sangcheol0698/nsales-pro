"""
Tool Manager
AI 도구들을 초기화하고 관리하는 매니저 클래스
"""

from .registry import ToolRegistry
from .google_tools import (
    GoogleCalendarViewTool, 
    GoogleCalendarCreateTool, 
    GoogleCalendarFindFreeTool,
    GmailSendTool, 
    GmailViewTool
)


class ToolManager:
    """AI 도구 매니저"""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self._initialize_tools()
    
    def _initialize_tools(self):
        """모든 도구 초기화 및 등록"""
        
        # Google Calendar Tools
        try:
            self.registry.register(GoogleCalendarViewTool(), "calendar")
            self.registry.register(GoogleCalendarCreateTool(), "calendar") 
            self.registry.register(GoogleCalendarFindFreeTool(), "calendar")
            print("✅ Google Calendar 도구들이 등록되었습니다.")
        except Exception as e:
            print(f"⚠️ Google Calendar 도구 등록 실패: {e}")
        
        # Gmail Tools
        try:
            self.registry.register(GmailSendTool(), "email")
            self.registry.register(GmailViewTool(), "email")
            print("✅ Gmail 도구들이 등록되었습니다.")
        except Exception as e:
            print(f"⚠️ Gmail 도구 등록 실패: {e}")
    
    def get_registry(self) -> ToolRegistry:
        """레지스트리 반환"""
        return self.registry
    
    def get_status(self) -> dict:
        """도구 시스템 상태 반환"""
        tools = self.registry.get_all_tools()
        categories = self.registry._categories
        
        status = {
            "total_tools": len(tools),
            "categories": {},
            "tools": list(tools.keys())
        }
        
        for category, tool_names in categories.items():
            if tool_names:
                status["categories"][category] = len(tool_names)
        
        return status


# 전역 도구 매니저 인스턴스
tool_manager = ToolManager()