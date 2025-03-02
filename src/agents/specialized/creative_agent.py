from typing import Dict, Any, List, Optional
import asyncio
import random

from langchain.schema.runnable import Runnable
from langchain.prompts import ChatPromptTemplate

from src.agents.base import BaseAgent

class CreativeAgent(BaseAgent):
    """
    Specialized agent for creative tasks such as content generation, ideation, and storytelling.
    """
    
    def __init__(
        self, 
        llm: Runnable,
        name: str = "Creative Agent",
        description: str = "Specialized in creative writing, content generation, and innovative thinking"
    ):
        super().__init__(name, description)
        self.llm = llm
        self.creative_modes = [
            "storyteller", "poet", "marketer", "visionary", 
            "designer", "innovator", "content_creator"
        ]
    
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a creative task using appropriate creative techniques.
        
        Args:
            task: Task details including query, style guides, etc.
            
        Returns:
            Creative content with metadata
        """
        query = task.get("query", "")
        creative_mode = task.get("creative_mode", self._detect_creative_mode(query))
        style = task.get("style", "")
        format_type = task.get("format", "free")
        tone = task.get("tone", "balanced")
        
        # Select the appropriate system prompt based on creative mode
        system_prompt = self._get_system_prompt(creative_mode, style, tone)
        
        human_prompt = """
        Creative request: {query}
        
        {format_instructions}
        
        Please provide your creative response.
        """
        
        # Format instructions based on requested format
        format_instructions = self._get_format_instructions(format_type)
        
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt.format(query=query, format_instructions=format_instructions))
        ])
        
        # Create the creative chain
        chain = chat_prompt | self.llm
        
        # Execute the chain
        response = await chain.ainvoke({})
        
        # Extract the creative content
        return {
            "answer": response.content,
            "confidence": 0.85,
            "creative_mode": creative_mode,
            "style": style,
            "tone": tone,
            "task_type": "creative"
        }
    
    def _detect_creative_mode(self, query: str) -> str:
        """Detect the appropriate creative mode based on the query."""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["story", "tell", "narrative", "fiction", "kể", "truyện"]):
            return "storyteller"
        elif any(term in query_lower for term in ["poem", "poetry", "verse", "thơ", "bài thơ"]):
            return "poet"
        elif any(term in query_lower for term in ["marketing", "advertise", "promotion", "quảng cáo"]):
            return "marketer"
        elif any(term in query_lower for term in ["vision", "future", "imagine", "tương lai", "tầm nhìn"]):
            return "visionary"
        elif any(term in query_lower for term in ["design", "visual", "layout", "thiết kế"]):
            return "designer"
        elif any(term in query_lower for term in ["innovate", "new idea", "concept", "idea", "ý tưởng", "sáng tạo"]):
            return "innovator"
        else:
            return "content_creator"  # Default mode
    
    def _get_system_prompt(self, creative_mode: str, style: str, tone: str) -> str:
        """Get the appropriate system prompt for the creative mode."""
        base_prompt = """
        You are an expert creative assistant, specializing in {mode_description}.
        Your creative style is {style_description}.
        Your tone should be {tone_description}.
        
        Approach creative tasks with originality, imagination, and attention to detail.
        Draw on diverse knowledge and perspectives to create compelling and engaging content.
        """
        
        # Define mode descriptions
        mode_descriptions = {
            "storyteller": "crafting engaging narratives and stories",
            "poet": "composing expressive poetry and verse",
            "marketer": "creating persuasive marketing and promotional content",
            "visionary": "developing forward-thinking and innovative concepts",
            "designer": "conceptualizing visual and design ideas",
            "innovator": "generating novel solutions and inventive ideas",
            "content_creator": "producing engaging general content across various formats"
        }
        
        # Style description based on input or default
        style_description = style if style else "versatile and adaptable to different contexts"
        
        # Tone descriptions
        tone_descriptions = {
            "formal": "formal and professional",
            "casual": "casual and conversational",
            "humorous": "light-hearted and humorous",
            "serious": "serious and thoughtful",
            "inspirational": "uplifting and motivational",
            "balanced": "well-balanced and appropriate to the context"
        }
        
        tone_description = tone_descriptions.get(tone, tone_descriptions["balanced"])
        mode_description = mode_descriptions.get(creative_mode, mode_descriptions["content_creator"])
        
        return base_prompt.format(
            mode_description=mode_description,
            style_description=style_description,
            tone_description=tone_description
        )
    
    def _get_format_instructions(self, format_type: str) -> str:
        """Get formatting instructions based on requested format."""
        formats = {
            "blog": "Format your response as a blog post with a title, introduction, main sections with headings, and a conclusion.",
            "social": "Format your response as a concise social media post, keeping it engaging and shareable.",
            "article": "Format your response as a well-structured article with a headline, byline, introduction, body paragraphs, and conclusion.",
            "script": "Format your response as a script or dialogue with character names and actions clearly indicated.",
            "bullet_points": "Format your response as organized bullet points for easy scanning.",
            "free": "Use whatever format best suits the creative request."
        }
        
        return formats.get(format_type, formats["free"])
    
    async def evaluate_suitability(self, task: Dict[str, Any]) -> float:
        """
        Evaluate how suitable this agent is for the given task.
        
        Creative agent is most suitable for content generation and creative tasks.
        """
        query = task.get("query", "").lower()
        
        # Keywords that suggest a creative task
        creative_keywords = [
            "create", "write", "design", "generate", "story", "poem", "content", "creative",
            "innovative", "tạo", "viết", "thiết kế", "truyện", "thơ", "nội dung", "sáng tạo"  # Vietnamese equivalents
        ]
        
        # Check if query contains creative keywords
        keyword_match = any(keyword in query for keyword in creative_keywords)
        
        # Check if task explicitly requests creative content
        explicit_match = task.get("task_type", "") in ["creative", "content_generation"]
        creative_mode_specified = "creative_mode" in task
        
        # Calculate suitability score
        if explicit_match or creative_mode_specified:
            return 0.95
        elif keyword_match:
            return 0.85
        else:
            return 0.3  # Default low score for non-creative tasks

def get_creative_agent(llm) -> CreativeAgent:
    """Factory function to create and configure a creative agent."""
    return CreativeAgent(llm=llm) 