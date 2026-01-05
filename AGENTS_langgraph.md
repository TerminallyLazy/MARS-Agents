# AGENTS.md

## Overview

This document provides an overview of the multi-agent research system designed for recursive self-improvement. The system consists of a network of specialized agents, each equipped with distinct capabilities and responsibilities. These agents collaborate to enhance their collective performance through a cycle of ongoing learning and adaptation.

## Agents Architecture

The system is structured around a dynamic network of agents, each playing a critical role in the overall functionality and improvement process. The agents operate semi-autonomously and interact through well-defined protocols to achieve common objectives.

### Core Agents

1. **Analyzer Agent**
    - **Purpose**: Gathers, processes, and analyzes data inputs to extract relevant insights.
    - **Capabilities**: Data mining, pattern recognition, statistical analysis.
    - **Interactions**: Provides insights to the Optimizer and Learner agents for further use.

2. **Optimizer Agent**
    - **Purpose**: Enhances system efficiency and performance by refining internal algorithms and processes.
    - **Capabilities**: Algorithmic optimization, resource allocation, performance tuning.
    - **Interactions**: Collaborates with the Analyzer agent for insights and executes improvements suggested by the Learner agent.

3. **Learner Agent**
    - **Purpose**: Facilitates the system's ability to self-improve through recursive learning.
    - **Capabilities**: Machine learning, neural network training, reinforcement learning.
    - **Interactions**: Integrates data and insights from the Analyzer agent and provides optimized models to the Optimizer agent.

4. **Coordinator Agent**
    - **Purpose**: Oversees agent interactions and ensures cohesive operation and communication among the agents.
    - **Capabilities**: Task delegation, synchronization, conflict resolution.
    - **Interactions**: Maintains a continuous communication loop with all agents to monitor and manage activities.

5. **Evaluator Agent**
    - **Purpose**: Assesses the effectiveness of improvements and alterations made by other agents.
    - **Capabilities**: Metrics evaluation, scenario testing, validation.
    - **Interactions**: Provides feedback to all agents to inform future actions and developments.

## Recursive Self-Improvement Cycle

1. **Data Collection and Analysis**: The Analyzer agent collects data and extracts insights.
2. **Optimization**: The Optimizer agent leverages these insights to enhance system efficiency.
3. **Learning and Adaptation**: The Learner agent implements recursive learning mechanisms to improve models and algorithms.
4. **Evaluation**: The Evaluator agent assesses the success of optimizations and learning processes, feeding results back into the cycle.
5. **Coordination**: Throughout this cycle, the Coordinator agent ensures smooth interaction and progress among all agents.

## Development Plan

- **Short-term Goals**: Implement basic functionalities of each agent; establish communication protocols.
- **Mid-term Goals**: Enhance learning capabilities; improve the efficiency of the optimization process.
- **Long-term Goals**: Achieve autonomous, continuous self-improvement without external intervention.

## Memory Subsystem (MemEvolve + HGM Integration)

The system implements a hierarchical memory architecture combining research patterns from MemEvolve and HGM.

### MemEvolve Patterns

- **Dual-Loop Evolution**:
  - Inner Loop: Content evolution (what the system remembers)
  - Outer Loop: Architecture evolution (how memory is structured)
- **BaseMemoryProvider Protocol**: Standard interface for memory systems
- **Dual-Buffer Memory**: Short-term (task-specific) + Long-term (strategic/operational)

### HGM Patterns

- **Memory Tree**: Hierarchical versioning of memory states
- **Thompson Sampling**: Exploration-exploitation balance for improvement selection
- **Utility Tracking**: Performance-based node scoring

### Memory Flow

```
Task Input → Memory Request → Phase Detection
                              ├── BEGIN → Strategic Guidance
                              ├── IN → Operational Guidance
                              └── END → Consolidation

Execution → Trajectory → Memory Update
                         ├── Score ≥ 7.0 → Strategic Memory
                         └── Score < 7.0 → Operational Memory
```

## Optimization Subsystem (GEPA Integration)

### Pareto Optimization

- **Multi-Objective Tracking**: accuracy, completeness, clarity
- **Pareto Front**: Non-dominated solutions maintained
- **Epsilon-Greedy Selection**: Occasional exploration of dominated candidates

### Reflective Mutation

- **Failure Analysis**: LLM-driven root cause analysis
- **Targeted Mutation**: Improvements address specific weaknesses
- **Candidate Merging**: Combine strengths from Pareto front

### Optimization Flow

```
Judge Score → Add Candidate → Update Pareto Front
                              ├── Score < Target → Select for Mutation
                              │                   → Reflective Analysis
                              │                   → Generate Mutation
                              │                   → Evaluate
                              └── Score ≥ Target → Complete
```

## Workflow Integration

The graph workflow integrates memory and optimization at key nodes:

1. **Entry Node**: Initializes memory provider and Pareto tracker
2. **Specialist Nodes**: Request memory guidance at BEGIN/IN phases
3. **Reflection Node**: Stores execution trajectories in memory
4. **Judge Node**: Tracks candidates in Pareto optimizer
5. **Memory Evolution Node**: Triggers outer-loop evolution on score plateau

## Conclusion

The multi-agent research system is designed to fundamentally enhance its performance over time through recursive self-improvement. By leveraging the specialized capabilities of each agent within a collaborative network, the system aims to achieve a continuously evolving state of optimization and learning. The interconnected operations of these agents are the driving force behind the evolutionary potential of the system.