from langgraph.graph.message import add_messages

from typing import Annotated
from typing_extensions import TypedDict

class CombinedAgentState(TypedDict):
    user_query: str
    user_name: str
    database_query: bool = False
    clinical_query: bool = False
    report: dict
    folllow_up_question: str
    nephrology_rag_query: bool
    web_search_query: bool = False
    irrelevant_query: bool = False
    receptionist_messages: Annotated[list, add_messages]
    clinical_messages: Annotated[list, add_messages]
    follow_up_messages: str


class ClinicalAgentSchema(TypedDict):
    nephrology_rag_query: bool = False
    web_search_query: bool = False
    irrelevant_query: bool = False


class ReceptionistAgentSchema(TypedDict):
    user_name: str
    database_query: bool = False
    clinical_query: bool = False


class DatabaseQueryResponse(TypedDict):
    follow_up_question: str
    clinical_agent: bool


class RagToolResponseSchema(TypedDict):
    insufficient_data: bool = False
    answer: str = ""
