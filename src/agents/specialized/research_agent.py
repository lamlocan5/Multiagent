from typing import Dict, Any, List, Optional
import asyncio

from langchain.schema.runnable import Runnable
from langchain.prompts import ChatPromptTemplate
from langchain.schema.vectorstore import VectorStore

from src.agents.base import BaseAgent
from src.rag.retrieval.hybrid_search import HybridSearchRetriever
from src.web.search import web_search

class ResearchAgent(BaseAgent):
    """
    Specialized agent for research tasks involving RAG and web search.
    """
    
    def __init__(
        self, 
        llm: Runnable,
        retriever: HybridSearchRetriever,
        name: str = "Research Agent",
        description: str = "Specialized in retrieving and synthesizing information from various sources"
    ):
        super().__init__(name, description)
        self.llm = llm
        self.retriever = retriever
    
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a research task by retrieving relevant information and generating an answer.
        
        Args:
            task: Task details including query, filters, etc.
            
        Returns:
            Answer with sources and confidence
        """
        query = task.get("query", "")
        use_web_search = task.get("use_web_search", False)
        filters = task.get("filters", {})
        
        # Step 1: Retrieve relevant documents from vector store
        docs = await self.retriever.search(
            query=query,
            filters=filters,
            top_k=5
        )
        
        # Step 2: Optionally perform web search for additional context
        web_results = []
        if use_web_search:
            web_results = await web_search(query, num_results=3)
        
        # Step 3: Combine all sources
        all_sources = docs + [{"content": result, "metadata": {"source": "web"}} for result in web_results]
        
        # Step 4: Generate answer with chain-of-thought reasoning
        context = "\n\n".join([doc["content"] for doc in all_sources])
        
        system_prompt = """
        You are a research assistant specialized in analyzing and synthesizing information from multiple sources.
        You will receive a query and context information. Your goal is to provide a comprehensive and accurate answer.
        
        Use the following steps:
        1. Analyze the query to understand what information is being requested
        2. Review the provided context carefully
        3. Synthesize the relevant information from all sources
        4. Present a clear and concise answer
        5. Indicate the confidence level in your answer based on the available information
        
        If the context doesn't contain sufficient information to answer the query, acknowledge this limitation.
        """
        
        human_prompt = """
        Query: {query}
        
        Context:
        {context}
        
        Respond in Vietnamese if the query is in Vietnamese.
        """
        
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        
        chain = chat_prompt | self.llm
        
        response = await chain.ainvoke({
            "query": query,
            "context": context
        })
        
        # Step 5: Extract and format the final answer
        return {
            "answer": response.content,
            "sources": [{"content": doc["content"], "metadata": doc["metadata"], "score": doc["score"]} for doc in docs[:3]],
            "confidence": 0.85,  # This should be calculated based on retrieval scores and answer certainty
            "reasoning": "Synthesized information from multiple sources to provide a comprehensive answer."
        }
    
    async def evaluate_suitability(self, task: Dict[str, Any]) -> float:
        """
        Evaluate how suitable this agent is for the given task.
        
        Research agent is most suitable for information retrieval and synthesis tasks.
        """
        query = task.get("query", "").lower()
        
        # Keywords that suggest a research task
        research_keywords = [
            "find", "search", "lookup", "research", "information", "data",
            "tìm", "kiếm", "tra cứu", "nghiên cứu", "thông tin", "dữ liệu"  # Vietnamese equivalents
        ]
        
        # Check if query contains research keywords
        keyword_match = any(keyword in query for keyword in research_keywords)
        
        # Check if task specifies RAG or web search
        explicit_match = task.get("task_type", "") in ["research", "rag", "web_search"]
        
        # Calculate suitability score
        if explicit_match:
            return 0.95
        elif keyword_match:
            return 0.8
        else:
            return 0.3  # Default moderate score for any query
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Return tools available to this agent."""
        return [
            {
                "name": "vector_search",
                "description": "Search the vector database for relevant information"
            },
            {
                "name": "web_search",
                "description": "Search the web for additional information"
            }
        ]

def get_research_agent(llm, retriever) -> ResearchAgent:
    """Factory function to create and configure a research agent."""
    return ResearchAgent(llm=llm, retriever=retriever) 