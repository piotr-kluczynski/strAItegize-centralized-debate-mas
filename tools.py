from typing import Annotated
from langchain_core.tools import tool
from langchain.tools import InjectedState

from strAItegize_common.others.order import describe_order

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