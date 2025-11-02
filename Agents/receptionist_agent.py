# Agents/receptionist_agent.py
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import interrupt

import dotenv, os, getpass

from Prompts.receptionist_agent_prompt import (
    receptionist_prompt,
    followup_question_prompt,
)
from Data.database import get_patient_by_name

from graph_state import *

dotenv.load_dotenv(".env")
KEY = os.environ.get("GOOGLE_API_KEY")
if not KEY:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Your API Key here :")


def set_system_prompt_receptionist(state: CombinedAgentState) -> CombinedAgentState:
    """Node to set a default system prompt."""
    try:
        system_prompt = [SystemMessage(content=receptionist_prompt)]
        # The node sets the base receptionist messages. The client should show prompt when awaiting.
        return {"receptionist_messages": system_prompt}
    except Exception as e:
        print("Exception occured while setting prompt -", e)


def take_user_input(state: CombinedAgentState) -> CombinedAgentState:
    """Node to take user input from client."""
    if state.get("follow_up_messages"):
        user_input = interrupt(state.get("follow_up_messages"))
    else:
        user_input = interrupt(
            "Hi, how can i help you, please enter your name or quey to begin with"
        )
    print(f"User:  {user_input}") 
    return {
        "user_query": user_input,
        "receptionist_messages": HumanMessage(content=user_input),
    }


def route_database_call_or_take_user_input(state: CombinedAgentState):
    """Routing Node to check which tool to use"""
    if state.get("database_query") and state.get("user_name") != "":
        return "database_query"
    # elif state.get("clinical_query"):
    #     return "clinical_agent"
    else:
        return "take_user_input"


def process_reception_query(state: CombinedAgentState) -> CombinedAgentState:
    try:
        print("----- in process reception query")
        llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")

        llm = llm.with_structured_output(schema=ReceptionistAgentSchema)
        messages = list(state.get("receptionist_messages", []))
        messages.append(HumanMessage(content=state.get("user_query", "")))
        response = llm.invoke(messages)

        if response.get("user_name") and response.get("database_query"):
            return {"user_name": response.get("user_name"), "database_query": True}
        elif response.get("clinical_query"):
            return {"clinical_query": True}
        else:
            return {"user_query": state.get("user_query", "")}

    except Exception as e:
        print("error occured while extracting processing reception query.", e)


def databse_query(state: CombinedAgentState) -> CombinedAgentState:
    """Node to make database query"""
    try:
        print("------ in database query")
        if state.get("report"):
            return {"report": state["report"]}

        response = get_patient_by_name(state.get("user_name", ""))
        if response is None:
            return {"report": None}

        return {"report": response}

    except Exception as e:
        print("Error occured while making database query - > ", e)


def handle_follow_up_question(state: CombinedAgentState) -> CombinedAgentState:
    """Node to handle follow up questions from user"""
    try:
        print("------- in handle follow up question")
        llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")
        llm = llm.with_structured_output(schema=DatabaseQueryResponse)

        receptionist_message = list(state.get("receptionist_messages", []))
        # keep previous messages (skip the initial system message)
        receptionist_message = receptionist_message[1:]
        receptionist_message.append(
            HumanMessage(
                content=f"here is my report for {state.get('user_name','')}: "
                + str(state.get("report", {}))
            )
        )
        receptionist_message.insert(0, SystemMessage(content=followup_question_prompt))

        response = llm.invoke(receptionist_message)
        if response.get("clinical_agent"):
            return {
                "clinical_query": True,
                "clinical_messages": str(response.get("follow_up_messages", "")),
            }
        elif response.get("follow_up_question"):
            print("Receptionist - ", response.get("follow_up_question") + "\n\n")
            return {
                "follow_up_question": response.get("follow_up_question"),
                "receptionist_messages": AIMessage(
                    content=response.get("follow_up_question")
                ),
                "follow_up_messages": str(response.get("follow_up_question", "")),
            }
        else:
            return {"user_query": state.get("user_query", "")}

    except Exception as e:
        print("Error occured while taking follow up questions - > ", e)


def route_followups_or_take_input_or_clinical_agent(state: CombinedAgentState):
    """Routing Node to check which tool to use after database query"""
    if state.get("follow_up_question"):
        return "handle_follow_up_question"
    elif state.get("clinical_query"):
        return "set_system_prompt_clinic"
    else:
        return "take_user_input"