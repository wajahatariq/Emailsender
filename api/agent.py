import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class EmailState(TypedDict):
    lead_data: dict
    template: str
    drafted_email: str

def draft_email_node(state: EmailState):
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-8b-8192" 
    )
    
    prompt = PromptTemplate.from_template(
        "You are an expert sales representative for Flowmotive. "
        "Draft an email strictly using this template framework: \n\n{template}\n\n"
        "Here is the specific client data to fill into the template: {lead_data}\n\n"
        "Return ONLY the plain text email body. Do not include subject lines or extra greetings not present in the template."
    )
    
    chain = prompt | llm
    result = chain.invoke({
        "template": state["template"],
        "lead_data": str(state["lead_data"])
    })
    
    return {"drafted_email": result.content}

def create_agent():
    workflow = StateGraph(EmailState)
    workflow.add_node("draft", draft_email_node)
    workflow.set_entry_point("draft")
    workflow.add_edge("draft", END)
    return workflow.compile()

def process_lead_with_agent(lead_data, template):
    agent = create_agent()
    initial_state = {
        "lead_data": lead_data,
        "template": template,
        "drafted_email": ""
    }
    
    result = agent.invoke(initial_state)
    company_name = lead_data.get("name", "your business")
    subject = f"Quick question regarding {company_name}"
    
    return result["drafted_email"], subject