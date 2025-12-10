from typing import Literal, List, Any
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
#from langchain_core.messages import add_messages
from typing_extensions import TypedDict, Annotated

from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from groq import BadRequestError

from prompt_library.prompt import system_prompt
from utils.llms import LLMModel

# TOOLS NEW IMPORTS
from toolkit.toolkits import (
    check_availability_by_doctor,
    check_availability_by_specialization,
    set_appointment,
    cancel_appointment,
    reschedule_appointment,
    create_patient,
    get_patient,
    update_patient,
    check_patient_id,
    get_patient_appointments
)

# --------------------------------------------------------------
# UPDATED ROUTER ACCORDING TO NEW MEMBERS
# --------------------------------------------------------------
from pydantic import BaseModel

class Router(BaseModel):
    next: Literal[
        "appointment_management_sup_agent",
        "check_suggest_availability_sup_agent",
        "faq_sup_agent",
        "patient_management_sup_agent",
        "FINISH"
    ] = "FINISH"      # default (باش مايبقاش فارغ)

    reasoning: str = "No reasoning provided."   # default

# ----------------------------------------------------
# ADD_MESSAGES FALLBACK (because LangGraph version missing)
# ----------------------------------------------------
def add_messages(existing, new):
    """
    Simple replacement for langgraph add_messages.
    Combines existing and new messages safely.
    """
    if existing is None:
        existing = []
    if new is None:
        new = []

    # Convert LangChain messages or dicts to list
    if not isinstance(existing, list):
        existing = [existing]
    if not isinstance(new, list):
        new = [new]

    return existing + new


# --------------------------------------------------------------
# GLOBAL STATE WITH CONVERSATION CONTEXT
# --------------------------------------------------------------
class AgentState(TypedDict):
    messages: list[Any]
    id_number: int
    next: str
    query: str
    current_reasoning: str
    pending_action: str  # Track multi-step actions (e.g., "booking", "cancellation")
    pending_data: dict   # Store data collected during multi-step conversations


# --------------------------------------------------------------
# CORE AGENT
# --------------------------------------------------------------
class DoctorAppointmentAgent:

    def __init__(self):
        llm_model = LLMModel()
        self.llm_model = llm_model.get_model()

    # ----------------------------------------------------------
    # SUPERVISOR NODE WITH MULTI-STEP CONVERSATION SUPPORT
    # ----------------------------------------------------------
    def supervisor_node(self, state: AgentState):
        import sys
        
        # Get user message
        if len(state["messages"]) > 0:
            msg = state["messages"][-1]
            if hasattr(msg, 'content'):
                user_message = msg.content
            elif isinstance(msg, dict) and 'content' in msg:
                user_message = msg['content']
            else:
                user_message = str(msg)
        else:
            user_message = ""
        
        user_message_lower = user_message.lower().strip()
        
        # Check if this is a simple greeting that should go to FAQ agent
        simple_greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
                           'bonjour', 'salut', 'bonsoir', 'coucou']
        
        if user_message_lower in simple_greetings:
            # Route to FAQ agent for greetings
            print(f"DEBUG: Routing to FAQ agent for greeting: {user_message}", file=sys.stderr)
            return Command(
                goto="faq_sup_agent",
                update={
                    "next": "faq_sup_agent",
                    "current_reasoning": "User sent a simple greeting, routing to FAQ agent",
                    "query": user_message,
                    "pending_action": "",  # Clear any pending action
                    "pending_data": {}     # Clear pending data
                }
            )
        
        # Check if we have a pending action (multi-step conversation)
        pending_action = state.get("pending_action", "")
        pending_data = state.get("pending_data", {})
        
        # If we have a pending booking action, route back to appointment agent
        if pending_action == "booking":
            print(f"DEBUG: Continuing booking conversation with pending data: {pending_data}", file=sys.stderr)
            return Command(
                goto="appointment_management_sup_agent",
                update={
                    "next": "appointment_management_sup_agent",
                    "current_reasoning": "Continuing multi-step booking conversation",
                    "query": user_message,
                    "pending_action": "booking",  # Keep the action pending
                    "pending_data": pending_data  # Keep the data
                }
            )
        
        # Simple keyword-based routing for mock LLM or when structured output fails
        # Check if we're using a mock LLM (check if the model has _llm_type attribute)
        using_mock = False
        try:
            # Check if it's a mock LLM by looking for _llm_type attribute
            if hasattr(self.llm_model, '_llm_type') and self.llm_model._llm_type == 'mock':
                using_mock = True
        except:
            pass
        
        # If using mock LLM or we want simple routing, use keyword matching
        if using_mock:
            print(f"DEBUG: Using keyword-based routing for mock LLM", file=sys.stderr)
            
            # Check if this is a follow-up to an agent response
            # Look at the last few messages to determine context
            if len(state["messages"]) >= 2:
                # Get the last agent message (if any)
                agent_messages = [msg for msg in state["messages"] if hasattr(msg, 'name') and msg.name]
                if agent_messages:
                    last_agent_msg = agent_messages[-1]
                    
                    # Check if the last agent was appointment agent asking for information
                    if last_agent_msg.name == "appointment_management_sup_agent":
                        # Check if the agent was asking for booking details
                        agent_content = last_agent_msg.content.lower() if hasattr(last_agent_msg, 'content') else str(last_agent_msg).lower()
                        if any(word in agent_content for word in ['doctor', 'date', 'time', 'need', 'require']):
                            # User is likely responding to appointment agent's request
                            print(f"DEBUG: User responding to appointment agent request, continuing", file=sys.stderr)
                            return Command(
                                goto="appointment_management_sup_agent",
                                update={
                                    "next": "appointment_management_sup_agent",
                                    "current_reasoning": "User responding to appointment agent's request",
                                    "query": user_message,
                                    "pending_action": "booking",  # Set pending action
                                    "pending_data": {"step": 1}   # Start with step 1
                                }
                            )
            
            # Multilingual keyword-based routing for new user messages
            # English keywords
            english_keywords = {
                'appointment': ['appointment', 'book', 'reschedule', 'cancel', 'schedule', 'rdv'],
                'availability': ['available', 'availability', 'schedule', 'time', 'slot'],
                'patient': ['patient', 'create patient', 'my info', 'information', 'update', 'profile'],
                'faq': ['service', 'faq', 'question', 'help', 'what', 'how', 'when', 'where']
            }
            
            # French keywords
            french_keywords = {
                'appointment': ['rendez-vous', 'réserver', 'prendre rdv', 'annuler', 'reporter'],
                'availability': ['disponible', 'disponibilité', 'horaire', 'créneau'],
                'patient': ['patient', 'créer patient', 'mes informations', 'profil', 'mettre à jour'],
                'faq': ['service', 'question', 'aide', 'quoi', 'comment', 'quand', 'où', 'prix']
            }
            
            # Arabic keywords (transliterated)
            arabic_keywords = {
                'appointment': ['موعد', 'حجز', 'تأجيل', 'إلغاء'],
                'availability': ['متاح', 'توفر', 'جدول', 'وقت'],
                'patient': ['مريض', 'معلومات', 'تحديث', 'ملف'],
                'faq': ['خدمة', 'سؤال', 'مساعدة', 'ماذا', 'كيف', 'متى', 'أين', 'سعر']
            }
            
            # Check all language keywords
            goto = "faq_sup_agent"
            reasoning = "Default routing to FAQ agent"
            
            # Check appointment keywords
            appointment_keywords = (english_keywords['appointment'] + 
                                  french_keywords['appointment'] + 
                                  arabic_keywords['appointment'])
            if any(keyword in user_message_lower for keyword in appointment_keywords):
                goto = "appointment_management_sup_agent"
                reasoning = "User mentioned appointment-related terms"
            
            # Check availability keywords (only if not already set to appointment)
            elif any(keyword in user_message_lower for keyword in (english_keywords['availability'] + 
                                                                  french_keywords['availability'] + 
                                                                  arabic_keywords['availability'])):
                goto = "check_suggest_availability_sup_agent"
                reasoning = "User asked about availability"
            
            # Check patient keywords (only if not already set)
            elif any(keyword in user_message_lower for keyword in (english_keywords['patient'] + 
                                                                  french_keywords['patient'] + 
                                                                  arabic_keywords['patient'])):
                goto = "patient_management_sup_agent"
                reasoning = "User asked about patient information"
            
            # Check FAQ keywords (only if not already set)
            elif any(keyword in user_message_lower for keyword in (english_keywords['faq'] + 
                                                                  french_keywords['faq'] + 
                                                                  arabic_keywords['faq'])):
                goto = "faq_sup_agent"
                reasoning = "User asked a general question"
            
            return Command(
                goto=goto,
                update={
                    "next": goto,
                    "current_reasoning": reasoning,
                    "query": user_message,
                    "pending_action": "",  # Clear any pending action
                    "pending_data": {}     # Clear pending data
                }
            )
        
        # Otherwise, use the LLM with structured output
        try:
            # Convert state messages to the format expected by the LLM
            llm_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"user ID: {state['id_number']}"}
            ]
            
            # Add the actual user messages
            for msg in state["messages"]:
                if hasattr(msg, 'content'):
                    # Determine role based on message type
                    if hasattr(msg, 'type') and msg.type == 'human':
                        role = "user"
                    elif hasattr(msg, 'type') and msg.type == 'ai':
                        role = "assistant"
                    else:
                        # Default based on class name
                        if 'HumanMessage' in str(type(msg)):
                            role = "user"
                        elif 'AIMessage' in str(type(msg)):
                            role = "assistant"
                        else:
                            role = "user"
                    llm_messages.append({"role": role, "content": msg.content})
                elif isinstance(msg, dict) and 'content' in msg:
                    # Already in dict format
                    llm_messages.append(msg)

            response = self.llm_model.with_structured_output(Router).invoke(llm_messages)
            
            goto = response.next
            if goto == "FINISH":
                goto = END

            update_data = {
                "next": goto,
                "current_reasoning": response.reasoning
            }

            # Don't replace messages, keep them for the conversation history
            if user_message:
                update_data["query"] = user_message

            return Command(goto=goto, update=update_data)
            
        except Exception as e:
            # If LLM fails, use keyword-based routing as fallback
            print(f"DEBUG: LLM failed with error: {e}, using keyword routing", file=sys.stderr)
            
            # Keyword-based routing fallback
            if any(word in user_message_lower for word in ['appointment', 'book', 'reschedule', 'cancel', 'schedule']):
                goto = "appointment_management_sup_agent"
                reasoning = f"LLM failed, keyword routing to appointment agent"
            elif any(word in user_message_lower for word in ['available', 'availability', 'schedule', 'time', 'slot']):
                goto = "check_suggest_availability_sup_agent"
                reasoning = f"LLM failed, keyword routing to availability agent"
            elif any(word in user_message_lower for word in ['patient', 'create patient', 'my info', 'information', 'update']):
                goto = "patient_management_sup_agent"
                reasoning = f"LLM failed, keyword routing to patient agent"
            else:
                # Default to FAQ
                goto = "faq_sup_agent"
                reasoning = f"LLM failed, default routing to FAQ agent"
            
            return Command(
                goto=goto,
                update={
                    "next": goto,
                    "current_reasoning": reasoning,
                    "query": user_message
                }
            )

    # ----------------------------------------------------------
    # NODE 1 — CHECK + SUGGEST DOCTOR AVAILABILITY
    # ----------------------------------------------------------
    def check_suggest_availability_sup_agent(self, state: AgentState):
        import sys
        
        # Check if we're using mock LLM
        using_mock = False
        try:
            if hasattr(self.llm_model, '_llm_type') and self.llm_model._llm_type == 'mock':
                using_mock = True
        except:
            pass
        
        # For mock LLM, use tools directly
        if using_mock:
            print(f"DEBUG: Availability agent using mock LLM, using tools directly", file=sys.stderr)
            
            # Get the last user message
            if len(state["messages"]) > 0:
                last_msg = state["messages"][-1]
                if hasattr(last_msg, 'content'):
                    user_message = last_msg.content.lower()
                elif isinstance(last_msg, dict) and 'content' in last_msg:
                    user_message = last_msg['content'].lower()
                else:
                    user_message = str(last_msg).lower()
            else:
                user_message = ""
            
            # Try to extract doctor name and date from message
            doctor_name = None
            date = None
            
            # Simple extraction logic
            if 'mohamed' in user_message or 'tajmouati' in user_message:
                doctor_name = "Dr.Mohamed Tajmouati"
            elif 'adil' in user_message:
                doctor_name = "Dr.Adil Tajmouati"
            elif 'hanane' in user_message or 'louizi' in user_message:
                doctor_name = "Dr.Hanane Louizi"
            
            # Default date if not specified
            date = "04-12-2025"  # Default date for testing
            
            if doctor_name:
                try:
                    # Call the tool directly
                    result = check_availability_by_doctor.func(date, doctor_name)
                    content = result
                except Exception as e:
                    content = f"I checked availability for {doctor_name} on {date}. Error: {str(e)}"
            else:
                content = "I can check doctor availability. Please specify which doctor you're interested in (e.g., Dr. Mohamed Tajmouati)."
        
        else:
            # Use create_react_agent for real LLM
            sys_msg = """
            You are the specialized agent responsible for checking doctor availability 
            AND suggesting new availability based on user needs.
            You can use:
            - check_availability_by_doctor
            - check_availability_by_specialization
            """

            system_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", sys_msg),
                    ("placeholder", "{messages}")
                ]
            )

            try:
                agent = create_react_agent(
                    model=self.llm_model,
                    tools=[check_availability_by_doctor, check_availability_by_specialization],
                    prompt=system_prompt
                )

                result = agent.invoke(state)
                content = result["messages"][-1].content
                
                # If content is empty, provide a default response
                if not content or content.strip() == "":
                    content = "I can help you check doctor availability. Please tell me which doctor or specialization you're interested in."
                    
            except BadRequestError as e:
                content = f"Tool validation error: {e}. Please provide correct parameters."
            except Exception as e:
                # If LLM fails, provide a helpful default response
                print(f"DEBUG: Check availability agent failed with error: {e}", file=sys.stderr)
                content = "I can help you check doctor availability. Please tell me which doctor or specialization you're interested in."

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content,
                              name="check_suggest_availability_sup_agent")
                ]
            },
            goto="supervisor",
        )

    # ----------------------------------------------------------
    # NODE 2 — APPOINTMENT MANAGEMENT WITH MULTI-STEP SUPPORT
    # ----------------------------------------------------------
    def appointment_management_sup_agent(self, state: AgentState):
        import sys
        import re
        
        # Check if we're using mock LLM
        using_mock = False
        try:
            if hasattr(self.llm_model, '_llm_type') and self.llm_model._llm_type == 'mock':
                using_mock = True
        except:
            pass
        
        # For mock LLM, use tools directly with multi-step support
        if using_mock:
            print(f"DEBUG: Appointment management agent using mock LLM with multi-step support", file=sys.stderr)
            
            # Get the last user message
            if len(state["messages"]) > 0:
                last_msg = state["messages"][-1]
                if hasattr(last_msg, 'content'):
                    user_message = last_msg.content
                elif isinstance(last_msg, dict) and 'content' in last_msg:
                    user_message = last_msg['content']
                else:
                    user_message = str(last_msg)
            else:
                user_message = ""
            
            user_message_lower = user_message.lower()
            
            # Get patient ID from state
            patient_id = state.get("id_number", 0)
            
            # Get pending action and data
            pending_action = state.get("pending_action", "")
            pending_data = state.get("pending_data", {})
            
            # If we have pending booking data, continue the multi-step process
            if pending_action == "booking" and pending_data:
                step = pending_data.get("step", 1)
                
                if step == 1:
                    # Step 1: Expecting doctor name
                    doctor_name = self._extract_doctor_name(user_message)
                    if doctor_name:
                        pending_data["doctor"] = doctor_name
                        pending_data["step"] = 2
                        content = f"Doctor: {doctor_name}. Now, what date would you like? (format: DD-MM-YYYY)"
                    else:
                        content = "I didn't recognize the doctor name. Please specify the full name (e.g., Dr. Mohamed Tajmouati)."
                
                elif step == 2:
                    # Step 2: Expecting date
                    date = self._extract_date(user_message)
                    if date:
                        pending_data["date"] = date
                        pending_data["step"] = 3
                        content = f"Date: {date}. Now, what time would you like? (format: HH:MM)"
                    else:
                        content = "I didn't recognize the date. Please specify the date in DD-MM-YYYY format."
                
                elif step == 3:
                    # Step 3: Expecting time
                    time = self._extract_time(user_message)
                    if time:
                        pending_data["time"] = time
                        # Try to book appointment
                        try:
                            full_date = f"{pending_data['date']} {pending_data['time']}"
                            result = set_appointment.func(full_date, patient_id, pending_data['doctor'])
                            content = f"Appointment confirmed! {result}"
                            # Clear pending data after successful booking
                            pending_action = ""
                            pending_data = {}
                        except Exception as e:
                            content = f"Error booking appointment: {str(e)}"
                    else:
                        content = "I didn't recognize the time. Please specify the time in HH:MM format."
                
                else:
                    content = "I can help you book an appointment. I need: 1) Doctor name, 2) Preferred date (DD-MM-YYYY), 3) Preferred time (HH:MM)."
                
                # Update state with new pending data
                update_data = {
                    "messages": state["messages"] + [
                        AIMessage(content=content, name="appointment_management_sup_agent")
                    ],
                    "pending_action": pending_action,
                    "pending_data": pending_data
                }
                
                return Command(
                    update=update_data,
                    goto="supervisor",
                )
            
            # Handle different appointment requests (new conversation)
            if any(word in user_message_lower for word in ['book', 'schedule', 'appointment', 'rendez-vous', 'rdv']):
                # Start booking process
                content = "I can help you book an appointment. I need: 1) Doctor name, 2) Preferred date (DD-MM-YYYY), 3) Preferred time (HH:MM)."
                
                # Set pending action for multi-step booking
                pending_action = "booking"
                pending_data = {"step": 1}
            
            elif any(word in user_message_lower for word in ['cancel', 'annuler']):
                # For cancellation, we need appointment ID
                content = "I can help you cancel an appointment. I need your appointment ID or the details of the appointment you want to cancel."
            
            elif any(word in user_message_lower for word in ['reschedule', 'reporter', 'changer']):
                # For rescheduling
                content = "I can help you reschedule an appointment. I need: 1) Current appointment details, 2) New preferred date and time."
            
            else:
                content = f"I can help you with appointment management for patient ID {patient_id}. Would you like to: 1) Book an appointment, 2) Cancel an appointment, or 3) Reschedule an appointment?"
        
        else:
            # Use create_react_agent for real LLM
            sys_msg = """
            You manage all appointment operations:
            - Set appointment
            - Cancel appointment
            - Reschedule appointment
            Ask politely for missing information.
            """

            system_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", sys_msg),
                    ("placeholder", "{messages}")
                ]
            )

            try:
                agent = create_react_agent(
                    model=self.llm_model,
                    tools=[set_appointment, cancel_appointment, reschedule_appointment],
                    prompt=system_prompt
                )

                result = agent.invoke(state)
                content = result["messages"][-1].content
                
                # If content is empty, provide a default response
                if not content or content.strip() == "":
                    content = "I can help you with appointment management. Would you like to book, cancel, or reschedule an appointment?"
                    
            except BadRequestError as e:
                # Clean up the error message to be user-friendly
                error_str = str(e)
                if "expected integer, but got string" in error_str:
                    content = "I need your patient ID number (a numeric value) to help with your appointment. Could you please provide your ID number?"
                elif "did not match schema" in error_str:
                    content = "I need more information to help you. Could you please provide the necessary details like your ID number, appointment date, and doctor name?"
                else:
                    content = "I encountered an issue processing your request. Could you please provide the necessary information in the correct format?"
            except Exception as e:
                # If LLM fails, provide a helpful default response
                print(f"DEBUG: Appointment management agent failed with error: {e}", file=sys.stderr)
                content = "I can help you with appointment management. Would you like to book, cancel, or reschedule an appointment?"

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content,
                              name="appointment_management_sup_agent")
                ]
            },
            goto="supervisor",
        )
    
    # Helper methods for extracting information from user messages
    def _extract_doctor_name(self, message: str):
        """Extract doctor name from message"""
        message_lower = message.lower()
        if 'mohamed' in message_lower or 'tajmouati' in message_lower:
            return "Dr.Mohamed Tajmouati"
        elif 'adil' in message_lower:
            return "Dr.Adil Tajmouati"
        elif 'hanane' in message_lower or 'louizi' in message_lower:
            return "Dr.Hanane Louizi"
        return None
    
    def _extract_date(self, message: str):
        """Extract date from message"""
        import re
        import datetime
        
        # Simple date patterns
        date_pattern = r'\b(\d{2}-\d{2}-\d{4})\b'
        match = re.search(date_pattern, message)
        if match:
            return match.group(1)
        
        # Handle "tomorrow", "today"
        message_lower = message.lower()
        if 'demain' in message_lower or 'tomorrow' in message_lower:
            tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
            return tomorrow
        elif 'aujourd\'hui' in message_lower or 'today' in message_lower:
            today = datetime.datetime.now().strftime("%d-%m-%Y")
            return today
        
        return None
    
    def _extract_time(self, message: str):
        """Extract time from message"""
        import re
        time_pattern = r'\b(\d{1,2}:\d{2})\b'
        match = re.search(time_pattern, message)
        if match:
            return match.group(1)
        
        # Handle common time expressions
        message_lower = message.lower()
        if 'matin' in message_lower or 'morning' in message_lower:
            return "09:00"
        elif 'après-midi' in message_lower or 'afternoon' in message_lower:
            return "14:00"
        elif 'soir' in message_lower or 'evening' in message_lower:
            return "17:00"
        
        return None

    # ----------------------------------------------------------
    # NODE 3 — FAQ SUP AGENT
    # ----------------------------------------------------------
    def faq_sup_agent(self, state: AgentState):
        import sys
        
        # Check if we're using mock LLM
        using_mock = False
        try:
            if hasattr(self.llm_model, '_llm_type') and self.llm_model._llm_type == 'mock':
                using_mock = True
        except:
            pass
        
        # For mock LLM, use simple responses
        if using_mock:
            print(f"DEBUG: FAQ agent using mock LLM response", file=sys.stderr)
            
            # Get the last user message
            if len(state["messages"]) > 0:
                last_msg = state["messages"][-1]
                if hasattr(last_msg, 'content'):
                    user_message = last_msg.content.lower()
                elif isinstance(last_msg, dict) and 'content' in last_msg:
                    user_message = last_msg['content'].lower()
                else:
                    user_message = str(last_msg).lower()
            else:
                user_message = ""
            
            # Simple rule-based responses
            if any(word in user_message for word in ['hello', 'hi', 'hey', 'bonjour']):
                content = "Hello! I can help you with questions about doctors, services, or hospital procedures."
            elif any(word in user_message for word in ['service', 'what do you offer', 'treatment']):
                content = "We offer dental services including orthodontics, prosthetics and implants, periodontology and aesthetics."
            elif any(word in user_message for word in ['doctor', 'médecin', 'dentist']):
                content = "We have experienced dentists specializing in orthodontics, prosthetics, and periodontology."
            elif any(word in user_message for word in ['hour', 'time', 'open', 'close']):
                content = "Our clinic is open Monday to Friday from 8:00 to 18:00, and Saturday from 9:00 to 13:00."
            elif any(word in user_message for word in ['price', 'cost', 'fee', 'tarif']):
                content = "Prices vary depending on the treatment. Please contact us for a personalized quote."
            else:
                content = "I'm here to help with questions about our medical services, doctors, and hospital procedures. Please tell me what you'd like to know."
        
        else:
            # Use create_react_agent for real LLM
            sys_msg = """
            You answer any FAQ question about:
            - Doctors
            - Services
            - Hospital procedures
            You DO NOT manage appointments.
            """

            system_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", sys_msg),
                    ("placeholder", "{messages}")
                ]
            )

            try:
                agent = create_react_agent(
                    model=self.llm_model,
                    tools=[],   # no tools for FAQ
                    prompt=system_prompt
                )

                result = agent.invoke(state)
                content = result["messages"][-1].content
                
                # If content is empty, provide a default response
                if not content or content.strip() == "":
                    content = "I can help you with questions about doctors, services, or hospital procedures. Could you please rephrase your question?"
                    
            except Exception as e:
                # If LLM fails, provide a helpful default response
                print(f"DEBUG: FAQ agent failed with error: {e}", file=sys.stderr)
                content = "I'm here to help with questions about our medical services, doctors, and hospital procedures. Please tell me what you'd like to know."

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content,
                              name="faq_sup_agent")
                ]
            },
            goto="supervisor",
        )

    # ----------------------------------------------------------
    # NODE 4 — PATIENT MANAGEMENT
    # ----------------------------------------------------------
    def patient_management_sup_agent(self, state: AgentState):
        import sys
        
        # Check if we're using mock LLM
        using_mock = False
        try:
            if hasattr(self.llm_model, '_llm_type') and self.llm_model._llm_type == 'mock':
                using_mock = True
        except:
            pass
        
        # For mock LLM, use tools directly
        if using_mock:
            print(f"DEBUG: Patient management agent using mock LLM, using tools directly", file=sys.stderr)
            
            # Get the last user message
            if len(state["messages"]) > 0:
                last_msg = state["messages"][-1]
                if hasattr(last_msg, 'content'):
                    user_message = last_msg.content.lower()
                elif isinstance(last_msg, dict) and 'content' in last_msg:
                    user_message = last_msg['content'].lower()
                else:
                    user_message = str(last_msg).lower()
            else:
                user_message = ""
            
            # Get patient ID from state
            patient_id = state.get("id_number", 0)
            
            # Handle different patient management requests
            if 'get my' in user_message or 'my info' in user_message or 'patient information' in user_message:
                # Get patient information
                try:
                    result = get_patient.func(patient_id)
                    content = result
                except Exception as e:
                    content = f"Error retrieving patient information for ID {patient_id}: {str(e)}"
            
            elif 'appointment' in user_message and ('my' in user_message or 'get' in user_message):
                # Get patient appointments
                try:
                    result = get_patient_appointments.func(patient_id)
                    content = result
                except Exception as e:
                    content = f"Error retrieving appointments for ID {patient_id}: {str(e)}"
            
            elif 'check' in user_message and 'id' in user_message:
                # Check patient ID
                try:
                    # Extract ID from message or use state ID
                    result = check_patient_id.func(patient_id)
                    content = result
                except Exception as e:
                    content = f"Error checking patient ID {patient_id}: {str(e)}"
            
            elif 'create' in user_message:
                content = "To create a new patient, I need: name, email, phone, birth date, gender, and address."
            
            elif 'update' in user_message:
                content = "To update patient information, please specify what you want to update and provide the new information."
            
            else:
                content = f"I can help you with patient management for ID {patient_id}. Would you like to: 1) Get your information, 2) Get your appointments, 3) Check if your ID exists, 4) Create a new patient, or 5) Update your information?"
        
        else:
            # Use create_react_agent for real LLM
            sys_msg = """
            You manage patient info:
            - create patient
            - retrieve patient
            - update patient
            - check patient ID existence
            
            You can use the following tools:
            - create_patient: Create a new patient record
            - get_patient: Retrieve patient information by ID
            - update_patient: Update patient information
            - check_patient_id: Check if a patient ID exists
            """

            system_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", sys_msg),
                    ("placeholder", "{messages}")
                ]
            )

            try:
                agent = create_react_agent(
                    model=self.llm_model,
                    tools=[create_patient, get_patient, update_patient, check_patient_id],
                    prompt=system_prompt
                )

                result = agent.invoke(state)
                content = result["messages"][-1].content
                
                # If content is empty, provide a default response
                if not content or content.strip() == "":
                    content = "I can help you with patient management. Would you like to create, retrieve, update patient information, or check if a patient ID exists?"
                    
            except BadRequestError as e:
                # Clean up the error message to be user-friendly
                error_str = str(e)
                if "expected integer, but got string" in error_str:
                    content = "I need a valid patient ID number (a numeric value) to help with patient management. Could you please provide a valid ID?"
                elif "did not match schema" in error_str:
                    content = "I need more information to help you. Could you please provide the necessary details like patient name, email, phone number, etc.?"
                else:
                    content = "I encountered an issue processing your request. Could you please provide the necessary information in the correct format?"
            except Exception as e:
                # If LLM fails, provide a helpful default response
                print(f"DEBUG: Patient management agent failed with error: {e}", file=sys.stderr)
                content = "I can help you with patient management. Would you like to create, retrieve, update patient information, or check if a patient ID exists?"

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content,
                              name="patient_management_sup_agent")
                ]
            },
            goto="supervisor",
        )

    # ----------------------------------------------------------
    # BUILD WORKFLOW GRAPH
    # ----------------------------------------------------------
    def workflow(self):

        self.graph = StateGraph(AgentState)

        self.graph.add_node("supervisor", self.supervisor_node)

        self.graph.add_node("appointment_management_sup_agent",
                            self.appointment_management_sup_agent)
        self.graph.add_node("check_suggest_availability_sup_agent",
                            self.check_suggest_availability_sup_agent)
        self.graph.add_node("faq_sup_agent", self.faq_sup_agent)
        self.graph.add_node("patient_management_sup_agent",
                            self.patient_management_sup_agent)

        self.graph.add_edge(START, "supervisor")

        self.app = self.graph.compile()
        return self.app
