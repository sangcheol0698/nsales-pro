"""
Tool Registry System
AI 에이전트가 사용할 수 있는 모든 도구들을 등록하고 관리하는 시스템
"""

from typing import Dict, List, Any, Optional
import json
from .base import BaseTool, ToolResult, ToolError


class ToolRegistry:
    """AI 도구 레지스트리"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[str, List[str]] = {
            "calendar": [],
            "email": [],
            "crm": [],
            "utility": [],
            "external": []
        }
    
    def register(self, tool: BaseTool, category: str = "utility") -> None:
        """도구 등록"""
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        
        self._tools[tool.name] = tool
        
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(tool.name)
        
        print(f"✅ Tool registered: {tool.name} ({category})")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """도구 조회"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """모든 도구 반환"""
        return self._tools.copy()
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """카테고리별 도구 조회"""
        if category not in self._categories:
            return []
        
        return [self._tools[name] for name in self._categories[category]]
    
    def get_openai_schemas(self) -> List[Dict[str, Any]]:
        """OpenAI Function Calling용 스키마 목록 반환"""
        return [tool.get_schema() for tool in self._tools.values()]
    
    def get_available_tools_info(self) -> Dict[str, Any]:
        """사용 가능한 도구들의 정보 반환"""
        tools_info = {}
        
        for category, tool_names in self._categories.items():
            if tool_names:  # 빈 카테고리는 제외
                tools_info[category] = []
                for name in tool_names:
                    tool = self._tools[name]
                    tools_info[category].append({
                        "name": tool.name,
                        "description": tool.description
                    })
        
        return tools_info
    
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """도구 실행"""
        if tool_name not in self._tools:
            return ToolResult(
                success=False,
                error=f"도구 '{tool_name}'을 찾을 수 없습니다."
            ).to_json()
        
        tool = self._tools[tool_name]
        return await tool.safe_execute(**kwargs)
    
    async def execute_tool_call(self, tool_call) -> str:
        """OpenAI tool call 객체를 사용한 도구 실행"""
        try:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"🔧 Tool Call: {function_name}({function_args})")
            
            return await self.execute_tool(function_name, **function_args)
            
        except json.JSONDecodeError as e:
            return ToolResult(
                success=False,
                error=f"잘못된 도구 인수 형식: {str(e)}"
            ).to_json()
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"도구 실행 중 오류: {str(e)}"
            ).to_json()
    
    def list_tools(self) -> str:
        """등록된 모든 도구 목록을 사용자 친화적 형식으로 반환"""
        if not self._tools:
            return "등록된 도구가 없습니다."
        
        result = "🛠️ **사용 가능한 AI 도구들:**\n\n"
        
        for category, tool_names in self._categories.items():
            if tool_names:
                # 카테고리명 한글화
                category_names = {
                    "calendar": "📅 캘린더",
                    "email": "📧 이메일",
                    "crm": "👥 고객관리",
                    "utility": "🔧 유틸리티",
                    "external": "🌐 외부서비스"
                }
                
                result += f"### {category_names.get(category, category)}\n"
                
                for name in tool_names:
                    tool = self._tools[name]
                    result += f"- **{tool.name}**: {tool.description}\n"
                
                result += "\n"
        
        return result