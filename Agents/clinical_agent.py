# Agents/clinical_agent.py
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.types import interrupt

import dotenv, os, getpass, json

from langchain_tavily import TavilySearch
from Prompts.clinical_agent_prompt import (
    clinic_agent_prompt,
    nephrology_rag_tool_prompt,
)
from RAG.vector_store import search_vector_store

dotenv.load_dotenv(".env")
KEY = os.environ.get("GOOGLE_API_KEY")
if not KEY:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Your API Key here :")

from graph_state import *


def set_system_prompt_clinic(state: CombinedAgentState) -> CombinedAgentState:
    """Node to set a default system prompt."""
    try:
        print("\nReceptionist: Transferring the chat to Clinical Agent...")
        system_prompt = [SystemMessage(content=clinic_agent_prompt)]
        return {"clinical_messages": system_prompt}
    except Exception as e:
        print("Exception occured while setting prompt -", e)

def take_user_input_clinic(state: CombinedAgentState) -> CombinedAgentState:
    if state.get("follow_up_messages"):
        message = f"Hi, {state["user_name"]} I am Clinical Agent. How can I help you today?\n\nYou have been transferred to me with your last query as: {state.get('user_query','')}\n\nFor such case please type yes or ask another query."
        user_input = interrupt(message)
        if "yes" in user_input.lower():
            return {
                "user_query": state["user_query"],
                "clinical_messages": HumanMessage(content=state["user_query"]),
            }
    else:
        user_input = interrupt(f"Hi, {state["user_name"]} I am a Clinical Agent. How can I help you today?")
    return {
        "user_query": user_input,
        "clinical_messages": HumanMessage(content=user_input),
    }

def web_search_tool(user_query: str):
    """Tool to perform web search using tavily tool, takes user query as input"""
    try:
        print("----- in web search tool")
        tavily_tool = TavilySearch(
            api_key=os.environ.get("TAVILY_API_KEY"), max_results=1
        )
        ans = tavily_tool.invoke({"query": user_query})["results"][0]["content"]
        
        return ans
        
    except Exception as e:
        print("Error occured while performing web search - > ", e)


def nephrology_rag_tool(user_query: str) -> str:
    """Tool to perform RAG over nephrology reference book, takes user query as input"""
    try:
        print("----- in nephrology RAG tool")
        rag_answer = search_vector_store(user_query)

        llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")
        llm = llm.with_structured_output(schema=RagToolResponseSchema)
        rag_answer = llm.invoke(
            [
                SystemMessage(content=nephrology_rag_tool_prompt + str(rag_answer)),
                HumanMessage(content=user_query),
            ]
        )

        return rag_answer 
    except Exception as e:
        print("Error occured while performing nephrology RAG tool - > ", e)


def process_clinic_query(state: CombinedAgentState) -> CombinedAgentState:

    print("----- in process clinic query")
    tool_list = [web_search_tool, nephrology_rag_tool]
    llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")
    llm_with_tools = llm.bind_tools(tool_list)
    clinical_messages = list(state.get("clinical_messages", []))
    clinical_messages.append(
        HumanMessage(
            content=f"here is my report for {state.get('user_name','')}: "
            + str(state.get("report", {}))
        )
    )
    clinical_messages.append(HumanMessage(content=state.get("user_query", "")))

    response = llm_with_tools.invoke(clinical_messages)

    function_call = response.additional_kwargs.get("function_call")

    if function_call:
        tool_name = function_call.get("name")
        raw_args = function_call.get("arguments", "{}")
        tool_args = json.loads(raw_args)

        print(f"🧠 Model requested tool: {tool_name}")
        print(f"🧩 Arguments: {tool_args}")

        tool = None
        for tool in tool_list:
            if tool.__name__ == tool_name:
                tool = tool
                break
        user_response: str = ""
        append_str = "\n\nPlease reply with Yes to end the conversation or ask other questions if required. \n\nThank You."

        ans = tool(tool_args.get("user_query"))
        if tool.__name__ == "web_search_tool":
            user_response = interrupt(f"""{ans}""" + append_str)
        elif ans.get("insufficient_data") == True:
            web_ans = web_search_tool(tool_args.get("user_query"))
            user_response = interrupt(f"""{str(web_ans)}""" + append_str)
        elif ans.get("insufficient_data") == False:
            user_response = interrupt(f"""{str(ans.get("answer")) + append_str}""")

        if user_response.lower == "yes":
            return {"end_chat": True}
        else:
            return {"end_chat": False}


def end_chat_or_continue(state: CombinedAgentState):
    if not state.get("end_chat") :
        return "process_clinic_query"