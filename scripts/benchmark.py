#!/usr/bin/env python
"""Benchmark script for testing agent performance."""

import asyncio
import time
import json
import sys
import argparse
import statistics
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.coordinator import AgentCoordinator
from src.utils.logging import setup_global_logging, get_logger

logger = get_logger(__name__)

# Configure argument parser
parser = argparse.ArgumentParser(description='Benchmark agent performance')
parser.add_argument('--queries', type=str, default='scripts/benchmark_queries.json',
                    help='Path to JSON file with benchmark queries')
parser.add_argument('--output', type=str, default='logs/benchmark_results.json',
                    help='Path to output results')
parser.add_argument('--iterations', type=int, default=3,
                    help='Number of iterations for each query')
parser.add_argument('--agent', type=str, default=None,
                    help='Specific agent to benchmark (default: all agents)')
parser.add_argument('--plot', action='store_true',
                    help='Generate performance plots')
parser.add_argument('--verbose', action='store_true',
                    help='Show detailed output')

async def run_benchmark(args):
    # Initialize logging
    setup_global_logging()
    
    # Load benchmark queries
    with open(args.queries, 'r', encoding='utf-8') as f:
        benchmark_queries = json.load(f)
    
    # Initialize the agent coordinator
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    results = []
    
    # Run benchmarks
    for query_item in benchmark_queries:
        query = query_item["query"]
        expected_agent = query_item.get("expected_agent")
        category = query_item.get("category", "general")
        
        logger.info(f"Testing query: {query}")
        print(f"\nBenchmarking: {query}")
        
        iteration_times = []
        iteration_agents = []
        iteration_successes = []
        
        for i in range(args.iterations):
            start_time = time.time()
            
            # Process the query
            if args.agent:
                response = await coordinator.process_with_agent(args.agent, {"query": query})
            else:
                response = await coordinator.process({"query": query})
            
            execution_time = time.time() - start_time
            iteration_times.append(execution_time)
            
            agent_used = response.get("agent_name")
            iteration_agents.append(agent_used)
            
            success = response.get("success", False)
            iteration_successes.append(success)
            
            # Record results
            result = {
                "query": query,
                "category": category,
                "agent_used": agent_used,
                "expected_agent": expected_agent,
                "execution_time": execution_time,
                "success": success,
                "iteration": i + 1,
                "tokens_used": response.get("metadata", {}).get("tokens_used"),
                "confidence": response.get("metadata", {}).get("confidence")
            }
            
            results.append(result)
            
            if args.verbose:
                print(f"  Iteration {i+1}: Agent={agent_used}, Time={execution_time:.2f}s, Success={success}")
            else:
                print(f"  Iteration {i+1}: {execution_time:.2f}s {'✓' if success else '✗'}")
    
    # Save results to JSON
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    generate_report(results, args.output, args.plot)

def generate_report(results, output_path, generate_plots=False):
    # Convert to DataFrame for analysis
    df = pd.DataFrame(results)
    
    # Print summary statistics
    print("\n=== Benchmark Summary ===")
    
    # Overall statistics
    total_queries = len(df['query'].unique())
    total_iterations = len(df)
    avg_time = df['execution_time'].mean()
    success_rate = df['success'].mean() * 100
    
    print(f"Total unique queries: {total_queries}")
    print(f"Total iterations: {total_iterations}")
    print(f"Average execution time: {avg_time:.2f}s")
    print(f"Overall success rate: {success_rate:.1f}%")
    
    # Per-agent statistics
    print("\n=== Agent Performance ===")
    agent_stats = df.groupby('agent_used').agg({
        'execution_time': ['mean', 'min', 'max', 'count'],
        'success': 'mean'
    })
    
    agent_stats.columns = ['avg_time', 'min_time', 'max_time', 'queries', 'success_rate']
    agent_stats['success_rate'] *= 100  # Convert to percentage
    
    # Format for display
    table_data = []
    for agent, stats in agent_stats.iterrows():
        table_data.append([
            agent,
            f"{stats['queries']:.0f}",
            f"{stats['avg_time']:.2f}s",
            f"{stats['min_time']:.2f}s",
            f"{stats['max_time']:.2f}s",
            f"{stats['success_rate']:.1f}%"
        ])
    
    print(tabulate(
        table_data,
        headers=['Agent', 'Queries', 'Avg Time', 'Min Time', 'Max Time', 'Success Rate'],
        tablefmt='grid'
    ))
    
    # Check expected vs. actual agent
    correct_agent = df['agent_used'] == df['expected_agent']
    agent_accuracy = correct_agent.mean() * 100
    print(f"\nAgent selection accuracy: {agent_accuracy:.1f}%")
    
    # Save report to text file
    report_path = output_path.replace('.json', '_report.txt')
    with open(report_path, 'w') as f:
        f.write("=== Benchmark Summary ===\n")
        f.write(f"Total unique queries: {total_queries}\n")
        f.write(f"Total iterations: {total_iterations}\n")
        f.write(f"Average execution time: {avg_time:.2f}s\n")
        f.write(f"Overall success rate: {success_rate:.1f}%\n\n")
        
        f.write("=== Agent Performance ===\n")
        f.write(tabulate(
            table_data,
            headers=['Agent', 'Queries', 'Avg Time', 'Min Time', 'Max Time', 'Success Rate'],
            tablefmt='grid'
        ))
        f.write(f"\n\nAgent selection accuracy: {agent_accuracy:.1f}%\n")
    
    # Generate plots if requested
    if generate_plots:
        # Time distribution by agent
        plt.figure(figsize=(10, 6))
        df.boxplot(column='execution_time', by='agent_used')
        plt.title('Execution Time by Agent')
        plt.suptitle('')
        plt.ylabel('Time (seconds)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path.replace('.json', '_time_by_agent.png'))
        
        # Success rate by agent
        plt.figure(figsize=(10, 6))
        success_by_agent = df.groupby('agent_used')['success'].mean() * 100
        success_by_agent.plot(kind='bar')
        plt.title('Success Rate by Agent')
        plt.ylabel('Success Rate (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path.replace('.json', '_success_by_agent.png'))
        
        # Success rate by category
        plt.figure(figsize=(10, 6))
        success_by_category = df.groupby('category')['success'].mean() * 100
        success_by_category.plot(kind='bar')
        plt.title('Success Rate by Query Category')
        plt.ylabel('Success Rate (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path.replace('.json', '_success_by_category.png'))
        
        print(f"\nPlots saved to {output_path.replace('.json', '_*.png')}")
    
    print(f"\nDetailed report saved to {report_path}")
    print(f"Raw results saved to {output_path}")

if __name__ == "__main__":
    args = parser.parse_args()
    asyncio.run(run_benchmark(args)) 