from typing import Dict, Any, List, Optional, Tuple
import asyncio
import time
from langchain.schema.runnable import Runnable

from src.agents.base import BaseAgent
from src.utils.logging import get_logger

logger = get_logger(__name__)

class AgentCoordinator:
    """
    Coordinator for managing multiple specialized agents.
    
    This class handles:
    1. Selecting the most appropriate agent for a task
    2. Managing parallel execution when needed
    3. Coordinating interactions between agents
    4. Fallback strategies when agents fail
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        default_agent: Optional[BaseAgent] = None,
        enable_parallel: bool = False,
        confidence_threshold: float = 0.5
    ):
        """
        Initialize the agent coordinator.
        
        Args:
            agents: List of available specialized agents
            default_agent: Fallback agent to use if no suitable agent is found
            enable_parallel: Whether to enable parallel execution of agents
            confidence_threshold: Minimum confidence to select an agent
        """
        self.agents = agents
        self.default_agent = default_agent or (agents[0] if agents else None)
        self.enable_parallel = enable_parallel
        self.confidence_threshold = confidence_threshold
        
        # Validate configuration
        if not agents:
            raise ValueError("At least one agent must be provided")
        
        logger.info(f"Initialized agent coordinator with {len(agents)} agents")
        for agent in agents:
            logger.info(f"  - {agent.name}: {agent.description}")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task using the most appropriate agent(s).
        
        Args:
            task: Dictionary containing task details
            
        Returns:
            Results from the selected agent(s)
        """
        start_time = time.time()
        
        # Check if a specific agent is requested
        if task.get("preferred_agent"):
            agent = self._get_agent_by_name(task["preferred_agent"])
            if agent:
                logger.info(f"Using preferred agent: {agent.name}")
                result = await self._execute_agent(agent, task)
                return self._prepare_result(result, agent, time.time() - start_time)
        
        # Otherwise, evaluate all agents for suitability
        agent_scores = await self._evaluate_agents(task)
        
        # Log agent suitability scores for debugging
        logger.debug(f"Agent suitability scores for task: {task.get('query', '')[:30]}...")
        for agent_name, score in agent_scores:
            logger.debug(f"  - {agent_name}: {score:.3f}")
        
        if not agent_scores:
            logger.warning("No suitable agents found, using default agent")
            if not self.default_agent:
                raise ValueError("No default agent available")
            
            result = await self._execute_agent(self.default_agent, task)
            return self._prepare_result(result, self.default_agent, time.time() - start_time)
        
        # Get the best agent(s)
        best_agent_name, best_score = agent_scores[0]
        best_agent = self._get_agent_by_name(best_agent_name)
        
        # If parallel execution is enabled and multiple agents have high scores,
        # execute them in parallel and combine results
        if self.enable_parallel and len(agent_scores) > 1:
            # Get agents with scores above threshold
            parallel_agents = [
                self._get_agent_by_name(name)
                for name, score in agent_scores
                if score >= self.confidence_threshold
            ]
            
            if len(parallel_agents) > 1:
                logger.info(f"Running {len(parallel_agents)} agents in parallel")
                results = await self._execute_parallel(parallel_agents, task)
                return self._combine_results(results, parallel_agents, time.time() - start_time)
        
        # Single agent execution
        logger.info(f"Selected agent: {best_agent.name} (score: {best_score:.3f})")
        result = await self._execute_agent(best_agent, task)
        return self._prepare_result(result, best_agent, time.time() - start_time)
    
    async def _evaluate_agents(self, task: Dict[str, Any]) -> List[Tuple[str, float]]:
        """
        Evaluate all agents for suitability for the task.
        
        Args:
            task: Task details
            
        Returns:
            List of (agent_name, score) tuples, sorted by descending score
        """
        scores = []
        
        # Evaluate all agents in parallel
        evaluation_tasks = [
            agent.evaluate_suitability(task)
            for agent in self.agents
        ]
        
        if evaluation_tasks:
            results = await asyncio.gather(*evaluation_tasks)
            
            for i, score in enumerate(results):
                if score > 0:  # Only include agents with positive scores
                    scores.append((self.agents[i].name, score))
        
        # Sort by descending score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
    
    async def _execute_agent(self, agent: BaseAgent, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single agent on the task.
        
        Args:
            agent: Agent to execute
            task: Task details
            
        Returns:
            Agent's results
        """
        try:
            # Log activity
            await agent.log_activity(f"Processing task: {task.get('query', '')[:50]}...")
            
            # Process task
            return await agent.process(task)
        except Exception as e:
            logger.error(f"Agent {agent.name} failed: {str(e)}")
            
            # If this was the default agent, we have no fallback
            if agent == self.default_agent:
                raise
            
            # Fall back to default agent
            logger.info(f"Falling back to default agent: {self.default_agent.name}")
            await self.default_agent.log_activity(
                f"Processing task as fallback: {task.get('query', '')[:50]}..."
            )
            return await self.default_agent.process(task)
    
    async def _execute_parallel(
        self, 
        agents: List[BaseAgent], 
        task: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple agents in parallel.
        
        Args:
            agents: List of agents to execute
            task: Task details
            
        Returns:
            List of results from each agent
        """
        execution_tasks = [
            self._execute_agent(agent, task)
            for agent in agents
        ]
        
        return await asyncio.gather(*execution_tasks)
    
    def _combine_results(
        self, 
        results: List[Dict[str, Any]], 
        agents: List[BaseAgent],
        execution_time: float
    ) -> Dict[str, Any]:
        """
        Combine results from multiple agents.
        
        Args:
            results: List of results from each agent
            agents: List of agents that produced the results
            execution_time: Total execution time
            
        Returns:
            Combined result
        """
        # This is a simplified combination strategy
        # In a real system, this would be more sophisticated
        
        # Select the result with the highest confidence
        best_result = None
        best_confidence = -1
        best_agent = None
        
        for i, result in enumerate(results):
            confidence = result.get("confidence", 0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_result = result
                best_agent = agents[i]
        
        if best_result:
            return self._prepare_result(best_result, best_agent, execution_time)
        else:
            # Fallback to first result if none have confidence scores
            return self._prepare_result(results[0], agents[0], execution_time)
    
    def _prepare_result(
        self, 
        result: Dict[str, Any], 
        agent: BaseAgent,
        execution_time: float
    ) -> Dict[str, Any]:
        """
        Prepare the final result by adding metadata.
        
        Args:
            result: Agent's result
            agent: Agent that produced the result
            execution_time: Execution time in seconds
            
        Returns:
            Enriched result with metadata
        """
        return {
            **result,
            "agent_name": agent.name,
            "agent_description": agent.description,
            "execution_time": execution_time
        }
    
    def _get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name.
        
        Args:
            name: Name of the agent to find
            
        Returns:
            Agent instance or None if not found
        """
        for agent in self.agents:
            if agent.name.lower() == name.lower():
                return agent
        return None
