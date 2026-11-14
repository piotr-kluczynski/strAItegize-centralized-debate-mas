from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage

from states import CentralizedDebateState, RepresentativeState
from prompts import agent_brainstorming_prompt

from strAItegize_common.client.communication.communication_context import CommunicationContext

def phase_node(state: CentralizedDebateState) -> CentralizedDebateState:
    pass

def brainstorming_node(state: CentralizedDebateState) -> CentralizedDebateState:
    active = list(state.get("active_agents", []))
    finished = list(state.get("finished_agents", []))
    
    # If all agents finished brainstorming, pick first topic and vote on its debate
    if not active:
        new_debate_topic = state.get("next_debates_topics", []).pop(0)
        
        # If there are no topics, and no agents are active, finish the system processing
        if not new_debate_topic:
            return {
                "next_action": "end"
            }
        # Otherwise assign topic as new debate, and move to the debate node
        else:
            return {
                # TO DO
            }
        
    # Otherwise, activate next agent in the queue
    else:
        agent_id = active.pop(0)
        history = list(state.get("representative_agents_messages", {}).get(agent_id, []))
        
        # Add brainstorming prompt to the agent's messages
        brainstorming_prompt = [SystemMessage(content=agent_brainstorming_prompt(
            upkeep=state["upkeep_phase"],
            supply_surplus=state["supply_surplus"],
            current_debate=state["current_debate"],
            debate_limit=state["debate_limit"],
            prev_debate_topics=state["prev_debates_topics"],
            prev_debate_results=state["prev_debates_results"]
        ))]
        
        

def debating_node(state: CentralizedDebateState) -> CentralizedDebateState:
    pass

def voting_node(state: CentralizedDebateState) -> CentralizedDebateState:
    pass

def get_centralized_debate_mas(
    communication: CommunicationContext,
    representative_agent_model = init_chat_model("openai:gpt-4o"),
    agent_num=3
):
    # Assigning tools
    
    # Building regional agent subgraph
    
    
    # Building Decentralized Debate Multi-Agent System graph
    
    pass
