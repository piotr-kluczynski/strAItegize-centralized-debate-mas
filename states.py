from typing import TypedDict, Optional, Annotated, Sequence, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

from tools import DebateMessage

from strAItegize_common.others.order import Order
from strAItegize_common.others.recruitment_choice import RecruitmentChoice

class CentralizedDebateState(TypedDict):
    # Simulation data
    player_id: str
    units: list[str]
    regions: list[str]
    upkeep_phase: bool
    supply_surplus: int
    recent_events: list[str]
    init_msg: str
    input_prompt: Optional[BaseMessage]
    
    # Unit & region assignment
    units_orders: dict[str, Order]
    region_recruitment: dict[str, RecruitmentChoice]
        
    # Message logs & blocked tools
    representative_agents_messages: dict[str, list[BaseMessage]]
    blocked_tools: list[str]
        
    # Debate & brainstorming
    debate_limit: int
    next_debates_topics: list[str]
    next_debates_authors: dict[str, str] # Debate Topic: Agent Id
    next_debates_solutions: dict[str, list[Order | RecruitmentChoice]] # Debate Topic: Proposed solution
    prev_debates_topics: list[str]
    prev_debates_results: dict[str, list[Order | RecruitmentChoice]] # Debate Topic: Proposed solution
    
    current_debate: int
    current_debate_topic: str
    current_debate_decisions: dict[str, list[Order | RecruitmentChoice]] # Agent Id: Proposed solution
    current_debate_messages: list[DebateMessage]
        
    # Voting
    agents_votes: dict[str, bool]
        
    # Turn queue & quiescence
    next_action: Literal["brainstorming", "debating", "voting", "representative_agent", "end"]
    active_agents: list[str]
    finished_agents: list[str]
        
    # Subgraph channel for active regional agent
    current_agent_id: Optional[str]
    vote: bool
    representative_messages: Optional[Annotated[Sequence[BaseMessage], add_messages]]
    
    pass

class RepresentativeState(TypedDict):  
    current_agent_id: str
    vote: bool
    proposed_decisions: dict[str, Order | RecruitmentChoice]
    representative_messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Channel for additional information
    next_debates_topics: list[str]
    next_debates_authors: dict[str, str] # Debate Topic: Agent Id
    next_debates_solutions: dict[str, list[Order | RecruitmentChoice]] # Debate Topic: Proposed solution
    prev_debates_topics: list[str]
