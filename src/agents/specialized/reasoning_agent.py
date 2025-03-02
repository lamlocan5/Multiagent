from typing import Dict, Any, List, Optional
import asyncio

from langchain.schema.runnable import Runnable
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from src.agents.base import BaseAgent

class ReasoningAgent(BaseAgent):
    """
    Specialized agent for complex reasoning and problem-solving tasks.
    """
    
    def __init__(
        self, 
        llm: Runnable,
        name: str = "Reasoning Agent",
        description: str = "Specialized in logical reasoning, problem-solving, and structured thinking"
    ):
        super().__init__(name, description)
        self.llm = llm
    
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a reasoning task using chain-of-thought techniques.
        
        Args:
            task: Task details including query, context, etc.
            
        Returns:
            Reasoned answer with explanation
        """
        query = task.get("query", "")
        context = task.get("context", "")
        require_formal = task.get("require_formal", False)
        step_by_step = task.get("step_by_step", True)
        
        # Define the system prompt based on reasoning requirements
        system_prompt = """
        You are an advanced reasoning assistant, specialized in logical analysis and problem-solving.
        You excel at breaking down complex problems into manageable steps and finding logical solutions.
        
        When given a question or problem:
        1. First, identify the key elements of the problem
        2. Break down the problem into smaller parts if needed
        3. Apply appropriate reasoning techniques (deductive, inductive, etc.)
        4. Provide clear explanations for each step in your reasoning
        5. Arrive at a well-justified conclusion
        
        {additional_instructions}
        """
        
        # Additional instructions based on task requirements
        additional_instructions = ""
        
        if step_by_step:
            additional_instructions += "\nProvide your reasoning in clear, numbered steps."
        
        if require_formal:
            additional_instructions += "\nUse formal notation where appropriate, showing logical relationships precisely."
        
        # Check if it's a Vietnamese query and add language instruction
        if any(c in "àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỵỷỹđ" for c in query.lower()):
            additional_instructions += "\nRespond in Vietnamese since the query is in Vietnamese."
        
        human_prompt = """
        Question or problem: {query}
        
        {context_section}
        
        Please provide your reasoning and answer.
        """
        
        context_section = f"Additional context:\n{context}" if context else ""
        
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt.format(additional_instructions=additional_instructions)),
            ("human", human_prompt.format(query=query, context_section=context_section))
        ])
        
        # Create the reasoning chain
        chain = chat_prompt | self.llm
        
        # Execute the chain with chain-of-thought reasoning
        response = await chain.ainvoke({})
        
        # Extract the reasoning chain and answer
        return {
            "answer": response.content,
            "confidence": 0.9,  # Confidence is typically high for reasoning tasks
            "reasoning_chain": response.content,  # In a more sophisticated version, we'd separate this
            "task_type": "reasoning"
        }
    
    async def evaluate_suitability(self, task: Dict[str, Any]) -> float:
        """
        Evaluate how suitable this agent is for the given task.
        
        Reasoning agent is most suitable for logical and analytical tasks.
        """
        query = task.get("query", "").lower()
        
        # Keywords that suggest a reasoning task
        reasoning_keywords = [
            "why", "how", "explain", "solve", "analyze", "reason", "think", "logic",
            "step by step", "compare", "contrast", "evaluate", "tại sao", "giải thích", 
            "phân tích", "suy luận", "so sánh", "đánh giá"  # Vietnamese equivalents
        ]
        
        # Check if query contains reasoning keywords
        keyword_match = any(keyword in query for keyword in reasoning_keywords)
        
        # Check if task explicitly requests reasoning
        explicit_match = task.get("task_type", "") in ["reasoning", "logic", "problem_solving"]
        
        # Calculate suitability score
        if explicit_match:
            return 0.95
        elif keyword_match:
            return 0.8
        elif query.endswith("?"):  # Questions are often reasoning tasks
            return 0.6
        else:
            return 0.4  # Reasonable default for many tasks

def get_reasoning_agent(llm) -> ReasoningAgent:
    """Factory function to create and configure a reasoning agent."""
    return ReasoningAgent(llm=llm) 