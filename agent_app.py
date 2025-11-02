from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

import dotenv, os, getpass

from graph_state import *
from Agents.receptionist_agent import (
    set_system_prompt_receptionist,
    take_user_input,
    process_reception_query,
    route_database_call_or_take_user_input,
    databse_query,
    handle_follow_up_question,
    route_followups_or_take_input_or_clinical_agent,
)

from Agents.clinical_agent import (
    set_system_prompt_clinic,
    take_user_input_clinic,
    process_clinic_query,
    end_chat_or_continue,
)

dotenv.load_dotenv(".env")
KEY = os.environ.get("GOOGLE_API_KEY")
if not KEY:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Your API Key here :")


combined_graph_compiler = StateGraph(CombinedAgentState)

combined_graph_compiler.add_node(
    "set_system_prompt_receptionist", set_system_prompt_receptionist
)
combined_graph_compiler.add_node("take_user_input", take_user_input)
combined_graph_compiler.add_node("process_reception_query", process_reception_query)
combined_graph_compiler.add_node("database_query", databse_query)
combined_graph_compiler.add_node("handle_follow_up_question", handle_follow_up_question)


combined_graph_compiler.add_node("set_system_prompt_clinic", set_system_prompt_clinic)

combined_graph_compiler.add_node("take_user_input_clinic", take_user_input_clinic)
combined_graph_compiler.add_node("process_clinic_query", process_clinic_query)


combined_graph_compiler.add_edge(START, "set_system_prompt_receptionist")
combined_graph_compiler.add_edge("set_system_prompt_receptionist", "take_user_input")
combined_graph_compiler.add_edge("take_user_input", "process_reception_query")

combined_graph_compiler.add_conditional_edges(
    "process_reception_query",
    route_database_call_or_take_user_input,
    {
        "database_query": "database_query",
        # "set_system_prompt_clinic": "set_system_prompt_clinic",
        "take_user_input": "take_user_input",
    },
)

combined_graph_compiler.add_edge("database_query", "handle_follow_up_question")

combined_graph_compiler.add_conditional_edges(
    "handle_follow_up_question",
    route_followups_or_take_input_or_clinical_agent,
    {
        "handle_follow_up_question": "handle_follow_up_question",
        "set_system_prompt_clinic": "set_system_prompt_clinic",
        "take_user_input": "take_user_input",
    },
)

combined_graph_compiler.add_edge("set_system_prompt_clinic", "take_user_input_clinic")
combined_graph_compiler.add_edge("take_user_input_clinic", "process_clinic_query")

combined_graph_compiler.add_conditional_edges(
    "process_clinic_query",
    end_chat_or_continue,
    {"process_clinic_query": "process_clinic_query"},
)

checkpointer = InMemorySaver()
combined_agent = combined_graph_compiler.compile(checkpointer=checkpointer)


try:
    png_bytes = combined_agent.get_graph().draw_mermaid_png()

    with open("combined_agent.png", "wb") as f:
        f.write(png_bytes)
except Exception:
    # This requires some extra dependencies and is optional
    pass
