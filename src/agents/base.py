"""Base agent implementation for the multiagent system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Callable
import asyncio
import time

from langchain.schema.runnable import Runnable
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from src.utils.logging import get_logger

logger = get_logger(__name__)

class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    
    This abstract class defines the interface that all specialized agents must implement.
    """
    
    def __init__(
        self,
        llm: Runnable,
        name: str = "Base Agent",
        description: str = "General-purpose agent",
        functions: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            llm: Language model to use for the agent
            name: Name of the agent
            description: Description of the agent's capabilities
            functions: Optional list of functions the agent can call
        """
        self.llm = llm
        self.name = name
        self.description = description
        self.functions = functions or []
        
        # Initialize common prompt templates
        self._initialize_prompts()
        
        logger.info(f"Initialized agent: {name}")
    
    def _initialize_prompts(self):
        """Initialize common prompt templates used by the agent."""
        # Default system message
        self.system_message = (
            "You are an AI assistant that helps users with their tasks. "
            "Provide clear, accurate, and helpful responses."
        )
        
        # Default thinking prompt
        self.thinking_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_message + "\n\nThink step by step about the following question."),
            ("user", "{query}")
        ])
        
        # Default response prompt
        self.response_prompt = ChatPromptTemplate.from_messages([
            ("system", "Now, use the following thinking to craft your response: {thinking}"),
            ("user", "Provide your final answer.")
        ])
    
    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task using this agent.
        
        Args:
            task: Dictionary containing task details
            
        Returns:
            Results of processing the task
        """
        pass
    
    @abstractmethod
    async def get_suitability_score(self, task: Dict[str, Any]) -> float:
        """
        Determine how suitable this agent is for a given task.
        
        Args:
            task: Dictionary containing task details
            
        Returns:
            Suitability score from 0.0 to 1.0
        """
        pass
    
    async def _think(self, query: str) -> str:
        """
        Generate step-by-step thinking about a query.
        
        Args:
            query: Question or task to think about
            
        Returns:
            Detailed thinking process
        """
        chain = LLMChain(llm=self.llm, prompt=self.thinking_prompt)
        result = await chain.arun(query=query)
        return result
    
    async def _respond(self, query: str, thinking: str) -> str:
        """
        Generate a response based on query and thinking.
        
        Args:
            query: Original question or task
            thinking: Step-by-step thinking about the query
            
        Returns:
            Final response
        """
        chain = LLMChain(llm=self.llm, prompt=self.response_prompt)
        result = await chain.arun(query=query, thinking=thinking)
        return result
    
    async def _search_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """
        Search a knowledge base for relevant information.
        
        Args:
            query: Search query
            
        Returns:
            List of relevant documents/information
        """
        # This is a stub method that should be implemented by subclasses
        # or replaced with a real implementation using RAG components
        logger.warning(f"Knowledge base search not implemented in base agent: {query}")
        return []
    
    async def _call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a function with the given arguments.
        
        Args:
            function_name: Name of the function to call
            arguments: Arguments to pass to the function
            
        Returns:
            Result of the function call
        """
        logger.info(f"Calling function {function_name} with arguments: {arguments}")
        
        start_time = time.time()
        
        # Check if function exists
        function_map = {func["name"]: func for func in self.functions}
        if function_name not in function_map:
            return {
                "error": f"Function '{function_name}' not found",
                "result": None
            }
        
        try:
            # In a real implementation, this would dispatch to actual functions
            # This is just a placeholder
            if hasattr(self, f"_func_{function_name}"):
                func = getattr(self, f"_func_{function_name}")
                result = await func(**arguments)
            else:
                return {
                    "error": f"Function '{function_name}' implementation not found",
                    "result": None
                }
            
            execution_time = time.time() - start_time
            
            return {
                "result": result,
                "error": None,
                "execution_time": execution_time
            }
        except Exception as e:
            logger.error(f"Error calling function {function_name}: {str(e)}")
            return {
                "error": str(e),
                "result": None,
                "execution_time": time.time() - start_time
            }
