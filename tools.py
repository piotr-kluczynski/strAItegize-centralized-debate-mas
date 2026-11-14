from typing import Annotated, Literal, Optional
from langgraph.types import Command
from langchain.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langchain.tools import InjectedState

from strAItegize_common.others.recruitment_choice import RecruitmentChoice
from strAItegize_common.others.order import Order, describe_order

def DebateMessage(TypedDict):
    pass

@tool
def set_vote(
    decision: bool,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Signal whether you agree with the proposed idea or not."""

    return Command(
        update={
            "vote": decision,
            "representative_messages": [
                ToolMessage(
                    content=f"Your vote: {decision}, has been submitted properly.",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )

@tool
def set_order(
    unit_id: str,
    order_type: Literal["move", "hold", "attack", "support"],
    target_id: Optional[str],
    move_q: Optional[int],
    move_r: Optional[int],
    move_s: Optional[int],
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Adds an order proposition to the specified unit."""
    # Verifying the unit ownership
    if unit_id not in state["units"]:
        return f"Error: You can only assign orders to one of the owned units."
    
    # Verifying the movement order
    if order_type == "move":
        # Checking if movement coordinates are properly assigned
        if move_q is None or move_r is None or move_s is None:
            return f"Error: Movement orders require q, r and s coordinates to be provided."
        
        # Checking the q + r + s = 0
        if move_q + move_r + move_s != 0:
            return f"Error: Movement coordinates need to sum up to 0."
    
    # Verifying the attack/support orders
    elif order_type == "attack" or order_type == "support":
        # Checking if target id is properly assigned
        if not target_id:
            return f"Error: Target id needs to be provided in case of attack/support orders"

    order = Order(
        order_type=order_type,
        unit_id=unit_id,
        target_id=target_id,
        move_q=move_q,
        move_r=move_r,
        move_s=move_s
    )
    
    proposed_decisions = state["proposed_decisions"]
    proposed_decisions[unit_id] = order

    return Command(
        update={
            "proposed_decisions": proposed_decisions,
            "representative_messages": [
                ToolMessage(
                    content=f"The order proposition of type {order_type} for the unit {unit_id} was properly added to your solution proposition.",
                    tool_call_id=tool_call_id
                )
            ]
        },
    )

@tool 
def set_recruitment(
    unit_type: Literal["light_infantry", "heavy_infantry", "cavalry", "none"],
    region: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Adds a recruitment choice to your proposed solution."""
    proposed_decisions = state["proposed_decisions"]
    
    # Verifying the ownership over the region
    if region not in state["regions"]:
        return f"Error: The country does not control the {region} region. List of controlled regions: {state["regions"]}."

    # Serving removal recrutment orders
    if unit_type == "none":
        proposed_decisions[region] = None
        
        return Command(
            update={
                "proposed_decisions": proposed_decisions,
                "representative_messages": [
                    ToolMessage(
                        content=f"Properly removed the recruitment choice for {region} region from the proposed solution.",
                        tool_call_id=tool_call_id
                    )
                ]
            }
        )

    # Verifying that current recruitments does not exceed the supply surplus
    # Need to remove the hard-coded part
    spent_supplies = 0
    for decision in proposed_decisions.values():
        if not decision or type(decision) == Order:
            continue
        
        spent_supplies += {"light_infantry": 1, "heavy_infantry": 2, "cavalry": 3}.get(unit_type, 0)
            
    new_cost = {"light_infantry": 1, "heavy_infantry": 2, "cavalry": 3}.get(unit_type, 0)    
    if state["supply_surplus"] + new_cost < spent_supplies:
        return f"Error: Cannot register new recruitment order, as it would exceed the total supply surplus: {state["supply_surplus"]}. Remaining supplies to spent: {state['supply_surplus'] - spent_supplies}."

    # Registering the recruitment
    recruitment_choice = RecruitmentChoice(
        unit_type=unit_type,
        region=region
    )

    proposed_decisions[region] = recruitment_choice
    
    return Command(
        update={
            "proposed_decisions": proposed_decisions,
            "representative_messages": [
                ToolMessage(
                    content=f"The recruitment choice to recruit {unit_type} in region {region}, was properly assigned to the proposed solution.",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )

@tool
def raise_debate_topic(
    debate_topic: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId]    
) -> Command:
    prev_debates_topics = state["prev_debates_topics"]
    next_debates_authors = state["next_debates_authors"]
    next_debates_solutions = state["next_debates_solutions"]
    
    if debate_topic in prev_debates_topics:
        prev_debates_str = ""
        for prev_topic in prev_debates_topics:
            prev_debates_str += f"{prev_topic}, "
        
        return f'The debate with topic "{debate_topic}" has already been raised during previous debate - choose a different topic to address.\r\nList of previously debated topics: {prev_debates_str}'
    
    if len(state["proposed_decisions"]) == 0:
        return f"Add orders/recruitment to your proposed solutions before raising the debate."
    
    next_debates_authors[debate_topic] = state["current_agent_id"]
    next_debates_solutions[debate_topic] = state["proposed_decisions"]
    
    return Command(
        update={
            "next_debates_topics": debate_topic,
            "next_debates_authors": next_debates_authors,
            "next_debates_solutions": next_debates_solutions,
            "representative_messages": [
                ToolMessage(
                    content=f"Your debate topic was correctly added to the debate queue. Await its resolution after the brainstorming phase ends.",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )

@tool
def get_order_list(state: Annotated[dict, InjectedState]) -> str:
    """Read the currently assigned orders of your units.

    Returns:
        The list of orders assigned to your units.
    """
    controlled_units = state.get("controlled_units") or {}

    # Formatting the tool output to be more readable for the LLM
    if len(controlled_units) > 0:
        observation = f"Currently assigned orders:\r\n"
        for order in controlled_units.values():
            observation += f"- {describe_order(order)};"
        observation += "."
    else:
        observation = "There are no orders assigned to your units."

    return observation

@tool
def get_recent_events(state: Annotated[dict, InjectedState]) -> str:
    """Read the list of all events that took place this round.

    Returns:
        The list of events from this round.    
    """
    events = state["recent_events"]

    # Formatting the tool output to be more readable for the LLM
    if len(events) > 0:
        observation = "Events that had occurred on this round:\r\n"
        for event in events:
            observation += f"- {event},"
        observation += "."
    else:
        observation = "There've been no events since the last round."

    return observation