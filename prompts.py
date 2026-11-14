from strAItegize_common.others.order import Order, describe_order
from strAItegize_common.others.recruitment_choice import RecruitmentChoice

def agent_brainstorming_prompt(
    upkeep: bool,
    supply_surplus: int,
    current_debate: int,
    debate_limit: int,
    prev_debate_topic: list[str],
    prev_debate_results: dict[str, list[Order | RecruitmentChoice]]
) -> str:
    pass