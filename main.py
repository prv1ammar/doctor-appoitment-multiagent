from fastapi import FastAPI
from pydantic import BaseModel
from agents.agent import DoctorAppointmentAgent
from langchain_core.messages import HumanMessage
import os

# Fix SSL Windows noise - commented out as it may cause connection issues
# os.environ.pop("SSL_CERT_FILE", None)

app = FastAPI()


# -------------------------------
# USER REQUEST BODY
# -------------------------------
class UserQuery(BaseModel):
    id_number: int
    messages: str


# -------------------------------
# INIT AGENT + GRAPH ONLY ONCE
# -------------------------------
agent = DoctorAppointmentAgent()
app_graph = agent.workflow()         # build workflow ONCE (important!)


# -------------------------------
# MAIN ENDPOINT
# -------------------------------
@app.post("/execute")
def execute_agent(user_input: UserQuery):

    # Prepare user message as LangChain HumanMessage
    input_message = [HumanMessage(content=user_input.messages)]

    # StateGraph state format
    query_state = {
        "messages": input_message,
        "id_number": user_input.id_number,
        "next": "",
        "query": "",
        "current_reasoning": "",
    }

    # Run agent workflow
    response = app_graph.invoke(
        query_state,
        config={
            "recursion_limit": 40,
            "configurable": {"thread_id": "session_1"}
        }
    )

    # Extract only the user message and the FINAL assistant response
    # We want: user message + last assistant message (not all intermediate agent messages)
    output_messages = []
    
    # First, add the user message
    output_messages.append({
        "sender": "user",
        "content": user_input.messages
    })
    
    # Find the last assistant/agent message in the response
    assistant_messages = []
    for msg in response["messages"]:
        if hasattr(msg, "content"):
            # Skip the user message (we already added it)
            if hasattr(msg, 'type') and msg.type == 'human':
                continue
            if isinstance(msg, HumanMessage):
                continue
                
            # Get sender name
            sender = getattr(msg, "name", "assistant")
            content = msg.content
            
            # Clean up error messages to be user-friendly
            if "Tool validation error" in content or "Error code: 400" in content:
                # Extract just the error message, not the full JSON
                if "expected integer, but got string" in content:
                    content = "I need your patient ID number (a numeric value) to help with your appointment. Could you please provide your ID number?"
                elif "did not match schema" in content:
                    content = "I need more information to help you. Could you please provide the necessary details like your ID number, appointment date, and doctor name?"
                else:
                    # Generic error message
                    content = "I encountered an issue processing your request. Could you please provide the necessary information in the correct format?"
            
            assistant_messages.append((sender, content))
    
    # Get the last assistant message (most recent)
    if assistant_messages:
        last_sender, last_content = assistant_messages[-1]
        output_messages.append({
            "sender": last_sender,
            "content": last_content
        })
    else:
        # If no assistant message, add a default
        output_messages.append({
            "sender": "assistant",
            "content": "How can I help you today?"
        })

    return {"messages": output_messages}
