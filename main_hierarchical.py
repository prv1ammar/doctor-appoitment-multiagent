"""
Main FastAPI application for the Hierarchical Multi-Agent System
Based on the 6-level architecture specification.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from agents.hierarchical_agent import HierarchicalAgentSystem
from langchain_core.messages import HumanMessage
import os

# Fix SSL Windows noise
os.environ.pop("SSL_CERT_FILE", None)

app = FastAPI(title="Hierarchical Multi-Agent Medical Appointment System")


# -------------------------------
# USER REQUEST BODY
# -------------------------------
class UserQuery(BaseModel):
    id_number: int
    messages: str


# -------------------------------
# INIT HIERARCHICAL AGENT SYSTEM
# -------------------------------
hierarchical_agent = HierarchicalAgentSystem()
hierarchical_app = hierarchical_agent.workflow()  # Build workflow once


# -------------------------------
# MAIN ENDPOINT
# -------------------------------
@app.post("/execute_hierarchical")
def execute_hierarchical_agent(user_input: UserQuery):
    """
    Execute the hierarchical multi-agent system with 6-level architecture.
    """
    # Prepare user message
    input_message = [HumanMessage(content=user_input.messages)]

    # Run hierarchical agent system
    response = hierarchical_agent.invoke(
        messages=input_message,
        patient_id=user_input.id_number
    )

    # Extract and format response
    output_messages = []
    
    # Add user message
    output_messages.append({
        "sender": "user",
        "content": user_input.messages
    })
    
    # Find the last assistant/agent message
    assistant_messages = []
    for msg in response["messages"]:
        if hasattr(msg, "content"):
            # Skip user messages
            if hasattr(msg, 'type') and msg.type == 'human':
                continue
            if isinstance(msg, HumanMessage):
                continue
                
            # Get sender name (agent name)
            sender = getattr(msg, "name", "assistant")
            content = msg.content
            
            # Clean up error messages
            if "Tool validation error" in content or "Error code: 400" in content:
                if "expected integer, but got string" in content:
                    content = "I need your patient ID number (a numeric value). Please provide your ID number."
                elif "did not match schema" in content:
                    content = "I need more information. Please provide necessary details like ID number, appointment date, and doctor name."
                else:
                    content = "I encountered an issue. Please provide information in the correct format."
            
            assistant_messages.append((sender, content))
    
    # Get the last assistant message
    if assistant_messages:
        last_sender, last_content = assistant_messages[-1]
        output_messages.append({
            "sender": last_sender,
            "content": last_content
        })
    else:
        output_messages.append({
            "sender": "assistant",
            "content": "How can I help you today?"
        })
    
    # Include logs in response for debugging (optional)
    logs = response.get("logs", [])
    
    return {
        "messages": output_messages,
        "agent_hierarchy": {
            "current_niveau": response.get("current_niveau", ""),
            "current_agent": response.get("current_agent", ""),
            "conversation_topic": response.get("conversation_topic", ""),
            "business_rules_applied": response.get("business_rules", {})
        },
        "logs_count": len(logs)
    }


# -------------------------------
# HEALTH CHECK ENDPOINT
# -------------------------------
@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "system": "Hierarchical Multi-Agent Medical Appointment System",
        "architecture": "6-level hierarchy (Orchestrator, Supervisor, Judge, Patient, FAQ, Availability, Appointment)",
        "endpoints": {
            "execute_hierarchical": "POST /execute_hierarchical",
            "health": "GET /"
        }
    }


# -------------------------------
# AGENT INFO ENDPOINT
# -------------------------------
@app.get("/agents")
def list_agents():
    return {
        "agents": [
            {
                "level": 0,
                "name": "Orchestrator",
                "role": "Brain of the system - analyzes intent, coordinates agents",
                "restrictions": "No appointments, no database access, no direct patient contact"
            },
            {
                "level": 1,
                "name": "Supervisor",
                "role": "Department head - validates requests, handles priorities",
                "restrictions": "No booking, no direct patient contact"
            },
            {
                "level": 2,
                "name": "Judge",
                "role": "Conflict resolution and error analysis",
                "restrictions": "No patient contact, no direct action"
            },
            {
                "level": 3,
                "name": "Patient Management",
                "role": "Patient data handling - CIN, insurance, medical history, consent",
                "restrictions": "No schedule access, no appointment management"
            },
            {
                "level": "3bis",
                "name": "FAQ/Support",
                "role": "Information only - answers questions",
                "restrictions": "No appointments, no patient data, no medical advice"
            },
            {
                "level": 4,
                "name": "Availability Checker",
                "role": "Schedule management only",
                "restrictions": "No patient contact, no booking"
            },
            {
                "level": 5,
                "name": "Appointment Operations",
                "role": "Booking execution",
                "restrictions": "No direct schedule reading, no patient profile management"
            }
        ]
    }


# -------------------------------
# RUN APPLICATION
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8007)
