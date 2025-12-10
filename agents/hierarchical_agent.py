"""
Hierarchical Multi-Agent System for Medical Appointments
Based on the 6-level architecture specification:

Level 0: Orchestrator - Brain of the system
Level 1: Supervisor - Department head
Level 2: Judge - Conflict resolution
Level 3: Patient Management - Patient data handling
Level 3bis: FAQ/Support - Information only
Level 4: Availability Checker - Schedule management
Level 5: Appointment Operations - Booking execution
"""

from typing import Literal, List, Any, Dict, Optional
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from groq import BadRequestError
from pydantic import BaseModel
import sys
import datetime
import json

from utils.llms import LLMModel
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
# ENHANCED DATA MODELS (to be implemented fully later)
# --------------------------------------------------------------
class EnhancedPatientModel(BaseModel):
    """Enhanced patient model with CIN, insurance, medical history, etc."""
    ID: int
    nom: str
    CIN: str  # National ID
    telephone: str
    email: str
    date_naissance: str
    sexe: str
    addresse: str
    assurance: Optional[str] = None  # Insurance
    maladies: Optional[str] = None  # Medical conditions
    allergies: Optional[str] = None  # Allergies
    consentement_chatbot: bool = False  # Chatbot consent
    date_consentement: Optional[str] = None

class EnhancedAppointmentModel(BaseModel):
    """Enhanced appointment model with pricing, status, urgency, etc."""
    patient_id: int
    medecin_id: int
    date_rendez_vous: str
    heure_rendez_vous: str
    service: str
    duree: int = 30  # Duration in minutes
    prix: Optional[float] = None
    statut: str = "confirmé"  # confirmé, annulé, reporté, absent
    urgence: bool = False
    source: str = "chatbot"  # chatbot, téléphone, site_web
    rappel_24h: bool = False
    rappel_2h: bool = False

class ConversationLog(BaseModel):
    """Comprehensive conversation logging"""
    timestamp: str
    patient_id: int
    agent_niveau: str
    agent_nom: str
    message: str
    sentiment: Optional[str] = None  # positif, neutre, négatif
    action_declenchee: Optional[str] = None
    erreur: Optional[str] = None

# --------------------------------------------------------------
# GLOBAL STATE WITH ENHANCED FIELDS
# --------------------------------------------------------------
class HierarchicalAgentState(TypedDict):
    messages: Annotated[list[Any], "add_messages"]  # Use add_messages for message updates
    patient_id: int
    current_niveau: str  # Current agent level
    current_agent: str   # Current agent name
    conversation_topic: str
    pending_action: Optional[str]  # For multi-step operations
    pending_data: Dict[str, Any]   # Data collected during multi-step
    logs: Annotated[List[Dict[str, Any]], "append"]  # Use append for logs
    business_rules: Dict[str, Any] # Applied business rules
    errors: Annotated[List[str], "append"]  # Use append for errors

# --------------------------------------------------------------
# LEVEL 0: ORCHESTRATOR AGENT
# --------------------------------------------------------------
class OrchestratorAgent:
    """Level 0: Brain of the system - analyzes intent, coordinates agents"""
    
    def __init__(self, llm_model):
        self.llm_model = llm_model
        
    def analyze_intent(self, state: HierarchicalAgentState) -> Dict[str, Any]:
        """Analyze user intent and determine which agent should handle it"""
        if len(state["messages"]) == 0:
            return {"niveau": "faq", "agent": "faq_support", "reasoning": "No messages"}
        
        last_msg = state["messages"][-1]
        user_message = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        user_message_lower = user_message.lower()
        
        # Simple intent analysis (would be enhanced with LLM)
        if any(word in user_message_lower for word in ['hello', 'hi', 'bonjour', 'salut']):
            return {"niveau": "faq", "agent": "faq_support", "reasoning": "Greeting"}
        elif any(word in user_message_lower for word in ['patient', 'mon info', 'créer', 'mettre à jour']):
            return {"niveau": "patient", "agent": "patient_management", "reasoning": "Patient data request"}
        elif any(word in user_message_lower for word in ['disponible', 'disponibilité', 'horaire', 'créneau']):
            return {"niveau": "availability", "agent": "availability_checker", "reasoning": "Availability check"}
        elif any(word in user_message_lower for word in ['rendez-vous', 'rdv', 'book', 'réserver', 'annuler', 'reporter']):
            return {"niveau": "appointment", "agent": "appointment_operations", "reasoning": "Appointment operation"}
        elif any(word in user_message_lower for word in ['service', 'question', 'quoi', 'comment', 'prix']):
            return {"niveau": "faq", "agent": "faq_support", "reasoning": "FAQ question"}
        else:
            return {"niveau": "faq", "agent": "faq_support", "reasoning": "Default to FAQ"}
    
    def route(self, state: HierarchicalAgentState) -> Command:
        """Route to appropriate agent based on intent analysis"""
        intent = self.analyze_intent(state)
        
        # Log the routing decision
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": state.get("patient_id", 0),
            "agent_niveau": "orchestrator",
            "agent_nom": "orchestrator",
            "message": f"Routing to {intent['niveau']} level, agent: {intent['agent']}",
            "sentiment": "neutre",
            "action_declenchee": f"route_to_{intent['agent']}",
            "reasoning": intent["reasoning"]
        }
        
        # Update state with log
        updated_logs = state.get("logs", []) + [log_entry]
        
        # Determine target node
        if intent["niveau"] == "patient":
            goto = "patient_management_agent"
        elif intent["niveau"] == "availability":
            goto = "availability_checker_agent"
        elif intent["niveau"] == "appointment":
            goto = "appointment_operations_agent"
        else:
            goto = "faq_support_agent"
        
        return Command(
            goto=goto,
            update={
                "current_niveau": intent["niveau"],
                "current_agent": intent["agent"],
                "logs": updated_logs,
                "conversation_topic": intent["reasoning"]
            }
        )

# --------------------------------------------------------------
# LEVEL 1: SUPERVISOR AGENT
# --------------------------------------------------------------
class SupervisorAgent:
    """Level 1: Department head - validates management, handles priorities"""
    
    def validate_request(self, state: HierarchicalAgentState, target_agent: str) -> Dict[str, Any]:
        """Validate if request can proceed based on business rules"""
        patient_id = state.get("patient_id", 0)
        
        # Check business rules
        rules = {
            "consent_required": True,
            "emergency_priority": False,
            "working_hours": self._check_working_hours(),
            "patient_exists": patient_id > 0
        }
        
        # Apply priority rules for emergencies
        last_msg = state["messages"][-1] if state["messages"] else None
        if last_msg:
            msg_content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            if any(word in msg_content.lower() for word in ['urgence', 'urgent', 'immédiat', 'grave']):
                rules["emergency_priority"] = True
                rules["consent_required"] = False  # Bypass consent for emergencies
        
        return {
            "valid": all(rules.values()),
            "rules": rules,
            "message": "Validation completed" if all(rules.values()) else "Validation failed"
        }
    
    def _check_working_hours(self) -> bool:
        """Check if within working hours (8:00-18:00 weekdays, 9:00-13:00 Saturday)"""
        now = datetime.datetime.now()
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        hour = now.hour
        
        if weekday < 5:  # Monday-Friday
            return 8 <= hour < 18
        elif weekday == 5:  # Saturday
            return 9 <= hour < 13
        else:  # Sunday
            return False
    
    def process(self, state: HierarchicalAgentState) -> Command:
        """Supervisor processing - validate and authorize"""
        validation = self.validate_request(state, state.get("current_agent", ""))
        
        # Log supervisor action
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": state.get("patient_id", 0),
            "agent_niveau": "supervisor",
            "agent_nom": "supervisor",
            "message": f"Validation result: {validation['message']}",
            "sentiment": "positif" if validation["valid"] else "négatif",
            "action_declenchee": "request_validation",
            "validation_result": validation
        }
        
        updated_logs = state.get("logs", []) + [log_entry]
        
        if not validation["valid"]:
            # Route to Judge agent for resolution
            return Command(
                goto="judge_agent",
                update={
                    "logs": updated_logs,
                    "errors": [f"Supervisor validation failed: {validation['message']}"]
                }
            )
        
        # Continue to target agent
        target_agent = state.get("current_agent", "")
        if target_agent == "patient_management":
            goto = "patient_management_agent"
        elif target_agent == "availability_checker":
            goto = "availability_checker_agent"
        elif target_agent == "appointment_operations":
            goto = "appointment_operations_agent"
        else:
            goto = "faq_support_agent"
        
        return Command(
            goto=goto,
            update={
                "logs": updated_logs,
                "business_rules": validation["rules"]
            }
        )

# --------------------------------------------------------------
# LEVEL 2: JUDGE AGENT
# --------------------------------------------------------------
class JudgeAgent:
    """Level 2: Conflict resolution and error analysis"""
    
    def resolve_conflict(self, state: HierarchicalAgentState) -> Dict[str, Any]:
        """Analyze errors and provide resolution"""
        errors = state.get("errors", [])
        patient_id = state.get("patient_id", 0)
        
        if not errors:
            return {
                "resolved": True,
                "action": "continue",
                "recommendation": "No errors to resolve"
            }
        
        # Analyze errors and provide recommendations
        recommendations = []
        for error in errors:
            if "consent" in error.lower():
                recommendations.append("Require patient consent before proceeding")
            elif "emergency" in error.lower():
                recommendations.append("Bypass normal procedures for emergency")
            elif "hours" in error.lower():
                recommendations.append("Schedule for next available working hours")
            elif "patient" in error.lower():
                recommendations.append("Verify patient identity and create profile if needed")
            else:
                recommendations.append("Escalate to human operator")
        
        return {
            "resolved": len(recommendations) == 1 and "continue" in recommendations[0],
            "action": "human_intervention" if "human" in str(recommendations).lower() else "retry",
            "recommendation": "; ".join(recommendations),
            "errors_analyzed": errors
        }
    
    def process(self, state: HierarchicalAgentState) -> Command:
        """Judge processing - resolve conflicts"""
        resolution = self.resolve_conflict(state)
        
        # Log judge action
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": state.get("patient_id", 0),
            "agent_niveau": "judge",
            "agent_nom": "judge",
            "message": f"Conflict resolution: {resolution['recommendation']}",
            "sentiment": "positif" if resolution["resolved"] else "négatif",
            "action_declenchee": "conflict_resolution",
            "resolution": resolution
        }
        
        updated_logs = state.get("logs", []) + [log_entry]
        
        if resolution["action"] == "human_intervention":
            # End conversation for human intervention
            return Command(
                goto=END,
                update={
                    "logs": updated_logs,
                    "messages": state["messages"] + [
                        AIMessage(content="I need to transfer you to a human operator for assistance. Please wait...",
                                 name="judge_agent")
                    ]
                }
            )
        elif resolution["action"] == "retry":
            # Retry with corrected parameters
            return Command(
                goto="orchestrator_agent",
                update={
                    "logs": updated_logs,
                    "errors": []  # Clear errors after resolution
                }
            )
        else:
            # Continue normally
            target_agent = state.get("current_agent", "")
            if target_agent == "patient_management":
                goto = "patient_management_agent"
            elif target_agent == "availability_checker":
                goto = "availability_checker_agent"
            elif target_agent == "appointment_operations":
                goto = "appointment_operations_agent"
            else:
                goto = "faq_support_agent"
            
            return Command(
                goto=goto,
                update={
                    "logs": updated_logs,
                    "errors": []
                }
            )

# --------------------------------------------------------------
# LEVEL 3: PATIENT MANAGEMENT AGENT
# --------------------------------------------------------------
class PatientManagementAgent:
    """Level 3: Patient data handling - no access to schedules or appointments"""
    
    def process(self, state: HierarchicalAgentState) -> Command:
        """Process patient management requests"""
        if len(state["messages"]) == 0:
            return self._default_response(state)
        
        last_msg = state["messages"][-1]
        user_message = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        user_message_lower = user_message.lower()
        patient_id = state.get("patient_id", 0)
        
        # Handle different patient management requests
        if any(word in user_message_lower for word in ['mon info', 'mes informations', 'profil']):
            content = self._get_patient_info(patient_id)
        elif any(word in user_message_lower for word in ['créer', 'nouveau', 'inscrire']):
            content = "Pour créer un nouveau patient, j'ai besoin: nom, CIN, téléphone, email, date de naissance, sexe, adresse."
        elif any(word in user_message_lower for word in ['mettre à jour', 'changer', 'modifier']):
            content = "Pour mettre à jour vos informations, veuillez spécifier ce que vous voulez modifier."
        elif any(word in user_message_lower for word in ['consentement', 'autorisation']):
            content = self._handle_consent(patient_id, user_message_lower)
        else:
            content = f"Je peux vous aider avec la gestion de votre dossier patient (ID: {patient_id}). Souhaitez-vous: 1) Voir vos informations, 2) Mettre à jour vos informations, 3) Gérer votre consentement chatbot?"
        
        # Log patient management action
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": patient_id,
            "agent_niveau": "patient",
            "agent_nom": "patient_management",
            "message": f"Patient management request: {user_message[:50]}...",
            "sentiment": "neutre",
            "action_declenchee": "patient_data_access"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="patient_management_agent")
                ],
                "logs": state.get("logs", []) + [log_entry]
            },
            goto="orchestrator_agent"
        )
    
    def _get_patient_info(self, patient_id: int) -> str:
        """Get patient information using existing tool"""
        try:
            return get_patient.func(patient_id)
        except Exception as e:
            return f"Erreur lors de la récupération des informations du patient ID {patient_id}: {str(e)}"
    
    def _handle_consent(self, patient_id: int, user_message: str) -> str:
        """Handle chatbot consent management"""
        if 'oui' in user_message or 'yes' in user_message or 'accepter' in user_message:
            return "Consentement chatbot accepté. Merci! Vous pouvez maintenant utiliser tous les services."
        elif 'non' in user_message or 'no' in user_message or 'refuser' in user_message:
            return "Consentement chatbot refusé. Certains services peuvent être limités."
        else:
            return "Pour utiliser nos services chatbot, avez-vous besoin de consentir à l'utilisation de vos données? Répondez par 'oui' ou 'non'."
    
    def _default_response(self, state: HierarchicalAgentState) -> Command:
        """Default response when no messages"""
        content = "Je suis l'agent de gestion des patients. Je peux vous aider avec votre dossier patient."
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": state.get("patient_id", 0),
            "agent_niveau": "patient",
            "agent_nom": "patient_management",
            "message": "Default response - no user message",
            "sentiment": "neutre",
            "action_declenchee": "default_response"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="patient_management_agent")
                ],
                "logs": state.get("logs", []) + [log_entry]
            },
            goto="orchestrator_agent"
        )

# --------------------------------------------------------------
# LEVEL 3bis: FAQ/SUPPORT AGENT
# --------------------------------------------------------------
class FAQSupportAgent:
    """Level 3bis: Information only - no appointments, no patient data, no medical advice"""
    
    def process(self, state: HierarchicalAgentState) -> Command:
        """Process FAQ requests"""
        if len(state["messages"]) == 0:
            return self._default_response(state)
        
        last_msg = state["messages"][-1]
        user_message = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        user_message_lower = user_message.lower()
        patient_id = state.get("patient_id", 0)
        
        # FAQ responses
        if any(word in user_message_lower for word in ['hello', 'hi', 'bonjour', 'salut']):
            content = "Bonjour! Je peux vous aider avec des questions sur nos services, médecins, ou procédures hospitalières."
        elif any(word in user_message_lower for word in ['service', 'offre', 'traitement']):
            content = "Nous offrons des services dentaires incluant orthodontie, prothèses et implants, parodontologie et esthétique."
        elif any(word in user_message_lower for word in ['médecin', 'dentiste', 'docteur']):
            content = "Nous avons des dentistes expérimentés spécialisés en orthodontie, prothèses, et parodontologie."
        elif any(word in user_message_lower for word in ['horaire', 'ouvert', 'fermé', 'heure']):
            content = "Notre clinique est ouverte du lundi au vendredi de 8:00 à 18:00, et le samedi de 9:00 à 13:00."
        elif any(word in user_message_lower for word in ['prix', 'coût', 'tarif', 'frais']):
            content = "Les prix varient selon le traitement. Veuillez nous contacter pour un devis personnalisé."
        elif any(word in user_message_lower for word in ['urgence', 'urgent']):
            content = "Pour les urgences dentaires, appelez-nous immédiatement au 05 XX XX XX XX."
        else:
            content = "Je suis ici pour répondre à vos questions sur nos services médicaux, médecins et procédures hospitalières. Que souhaitez-vous savoir?"
        
        # Log FAQ action
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": patient_id,
            "agent_niveau": "faq",
            "agent_nom": "faq_support",
            "message": f"FAQ request: {user_message[:50]}...",
            "sentiment": "neutre",
            "action_declenchee": "faq_response"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="faq_support_agent")
                ],
                "logs": state.get("logs", []) + [log_entry]
            },
            goto="orchestrator_agent"
        )
    
    def _default_response(self, state: HierarchicalAgentState) -> Command:
        """Default FAQ response"""
        content = "Bonjour! Je peux répondre à vos questions sur nos services, médecins, et procédures."
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": state.get("patient_id", 0),
            "agent_niveau": "faq",
            "agent_nom": "faq_support",
            "message": "Default FAQ response",
            "sentiment": "neutre",
            "action_declenchee": "default_faq_response"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="faq_support_agent")
                ],
                "logs": state.get("logs", []) + [log_entry]
            },
            goto="orchestrator_agent"
        )

# --------------------------------------------------------------
# LEVEL 4: AVAILABILITY CHECKER AGENT
# --------------------------------------------------------------
class AvailabilityCheckerAgent:
    """Level 4: Schedule management only - no patient contact, no booking"""
    
    def process(self, state: HierarchicalAgentState) -> Command:
        """Check doctor availability"""
        if len(state["messages"]) == 0:
            return self._default_response(state)
        
        last_msg = state["messages"][-1]
        user_message = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        user_message_lower = user_message.lower()
        patient_id = state.get("patient_id", 0)
        
        # Extract doctor name and date from message
        doctor_name = None
        date = None
        
        # Simple extraction
        if 'mohamed' in user_message_lower or 'tajmouati' in user_message_lower:
            doctor_name = "Dr.Mohamed Tajmouati"
        elif 'adil' in user_message_lower:
            doctor_name = "Dr.Adil Tajmouati"
        elif 'hanane' in user_message_lower or 'louizi' in user_message_lower:
            doctor_name = "Dr.Hanane Louizi"
        
        # Date extraction (simplified)
        if 'demain' in user_message_lower:
            tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
            date = tomorrow
        elif 'aujourd\'hui' in user_message_lower or 'today' in user_message_lower:
            today = datetime.datetime.now().strftime("%d-%m-%Y")
            date = today
        else:
            # Default to tomorrow for testing
            tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
            date = tomorrow
        
        if doctor_name:
            try:
                result = check_availability_by_doctor.func(date, doctor_name)
                content = result
            except Exception as e:
                content = f"Erreur lors de la vérification de disponibilité pour {doctor_name}: {str(e)}"
        else:
            content = "Je peux vérifier la disponibilité des médecins. Veuillez spécifier le nom du médecin (ex: Dr. Mohamed Tajmouati)."
        
        # Log availability check
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": patient_id,
            "agent_niveau": "availability",
            "agent_nom": "availability_checker",
            "message": f"Availability check: {user_message[:50]}...",
            "sentiment": "neutre",
            "action_declenchee": "availability_check"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="availability_checker_agent")
                ],
                "logs": state.get("logs", []) + [log_entry]
            },
            goto="orchestrator_agent"
        )
    
    def _default_response(self, state: HierarchicalAgentState) -> Command:
        """Default availability response"""
        content = "Je suis l'agent de vérification de disponibilité. Je peux vérifier les créneaux disponibles des médecins."
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": state.get("patient_id", 0),
            "agent_niveau": "availability",
            "agent_nom": "availability_checker",
            "message": "Default availability response",
            "sentiment": "neutre",
            "action_declenchee": "default_availability_response"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="availability_checker_agent")
                ],
                "logs": state.get("logs", []) + [log_entry]
            },
            goto="orchestrator_agent"
        )

# --------------------------------------------------------------
# LEVEL 5: APPOINTMENT OPERATIONS AGENT
# --------------------------------------------------------------
class AppointmentOperationsAgent:
    """Level 5: Booking execution - no direct schedule reading, no patient profile management"""
    
    def process(self, state: HierarchicalAgentState) -> Command:
        """Handle appointment operations (booking, cancellation, rescheduling)"""
        if len(state["messages"]) == 0:
            return self._default_response(state)
        
        last_msg = state["messages"][-1]
        user_message = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        user_message_lower = user_message.lower()
        patient_id = state.get("patient_id", 0)
        
        # Check if we have pending data for multi-step booking
        pending_action = state.get("pending_action")
        pending_data = state.get("pending_data", {})
        
        if pending_action == "booking" and pending_data:
            # Continue multi-step booking
            return self._continue_booking(state, user_message, patient_id, pending_data)
        
        # Handle different appointment requests
        if any(word in user_message_lower for word in ['réserver', 'book', 'prendre rdv', 'rendez-vous']):
            return self._start_booking(state, user_message, patient_id)
        elif any(word in user_message_lower for word in ['annuler', 'cancel']):
            content = "Je peux vous aider à annuler un rendez-vous. J'ai besoin de l'ID du rendez-vous ou des détails du rendez-vous."
        elif any(word in user_message_lower for word in ['reporter', 'reschedule', 'changer date']):
            content = "Je peux vous aider à reporter un rendez-vous. J'ai besoin des détails du rendez-vous actuel et de la nouvelle date souhaitée."
        elif any(word in user_message_lower for word in ['mes rdv', 'mes rendez-vous', 'liste rdv']):
            try:
                result = get_patient_appointments.func(patient_id)
                content = result
            except Exception as e:
                content = f"Erreur lors de la récupération de vos rendez-vous: {str(e)}"
        else:
            content = f"Je peux vous aider avec la gestion des rendez-vous (ID patient: {patient_id}). Souhaitez-vous: 1) Prendre un rendez-vous, 2) Annuler un rendez-vous, 3) Reporter un rendez-vous, 4) Voir vos rendez-vous?"
        
        # Log appointment operation
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": patient_id,
            "agent_niveau": "appointment",
            "agent_nom": "appointment_operations",
            "message": f"Appointment request: {user_message[:50]}...",
            "sentiment": "neutre",
            "action_declenchee": "appointment_operation"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="appointment_operations_agent")
                ],
                "logs": state.get("logs", []) + [log_entry]
            },
            goto="orchestrator_agent"
        )
    
    def _start_booking(self, state: HierarchicalAgentState, user_message: str, patient_id: int) -> Command:
        """Start multi-step booking process"""
        content = "Je peux vous aider à prendre un rendez-vous. J'ai besoin: 1) Nom du médecin, 2) Date souhaitée (JJ-MM-AAAA), 3) Heure souhaitée (HH:MM)."
        
        # Set pending action for next step
        pending_data = {
            "step": 1,
            "doctor": None,
            "date": None,
            "time": None
        }
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": patient_id,
            "agent_niveau": "appointment",
            "agent_nom": "appointment_operations",
            "message": "Starting booking process",
            "sentiment": "positif",
            "action_declenchee": "start_booking"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="appointment_operations_agent")
                ],
                "logs": state.get("logs", []) + [log_entry],
                "pending_action": "booking",
                "pending_data": pending_data
            },
            goto="orchestrator_agent"
        )
    
    def _continue_booking(self, state: HierarchicalAgentState, user_message: str, patient_id: int, pending_data: Dict) -> Command:
        """Continue multi-step booking with collected data"""
        step = pending_data.get("step", 1)
        
        if step == 1:
            # Expecting doctor name
            doctor_name = self._extract_doctor_name(user_message)
            if doctor_name:
                pending_data["doctor"] = doctor_name
                pending_data["step"] = 2
                content = f"Médecin: {doctor_name}. Maintenant, quelle date souhaitez-vous? (format: JJ-MM-AAAA)"
            else:
                content = "Je n'ai pas reconnu le nom du médecin. Veuillez spécifier le nom complet (ex: Dr. Mohamed Tajmouati)."
        
        elif step == 2:
            # Expecting date
            date = self._extract_date(user_message)
            if date:
                pending_data["date"] = date
                pending_data["step"] = 3
                content = f"Date: {date}. Maintenant, quelle heure souhaitez-vous? (format: HH:MM)"
            else:
                content = "Je n'ai pas reconnu la date. Veuillez spécifier la date au format JJ-MM-AAAA."
        
        elif step == 3:
            # Expecting time
            time = self._extract_time(user_message)
            if time:
                pending_data["time"] = time
                # Try to book appointment
                try:
                    full_date = f"{pending_data['date']} {pending_data['time']}"
                    result = set_appointment.func(full_date, patient_id, pending_data['doctor'])
                    content = f"Rendez-vous confirmé! {result}"
                    # Clear pending data
                    pending_data = {}
                except Exception as e:
                    content = f"Erreur lors de la prise de rendez-vous: {str(e)}"
            else:
                content = "Je n'ai pas reconnu l'heure. Veuillez spécifier l'heure au format HH:MM."
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": patient_id,
            "agent_niveau": "appointment",
            "agent_nom": "appointment_operations",
            "message": f"Booking step {step}: {user_message[:50]}...",
            "sentiment": "positif",
            "action_declenchee": f"booking_step_{step}"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="appointment_operations_agent")
                ],
                "logs": state.get("logs", []) + [log_entry],
                "pending_action": "booking" if pending_data else None,
                "pending_data": pending_data if pending_data else {}
            },
            goto="orchestrator_agent"
        )
    
    def _extract_doctor_name(self, message: str) -> Optional[str]:
        """Extract doctor name from message"""
        message_lower = message.lower()
        if 'mohamed' in message_lower or 'tajmouati' in message_lower:
            return "Dr.Mohamed Tajmouati"
        elif 'adil' in message_lower:
            return "Dr.Adil Tajmouati"
        elif 'hanane' in message_lower or 'louizi' in message_lower:
            return "Dr.Hanane Louizi"
        return None
    
    def _extract_date(self, message: str) -> Optional[str]:
        """Extract date from message (simplified)"""
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
    
    def _extract_time(self, message: str) -> Optional[str]:
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
    
    def _default_response(self, state: HierarchicalAgentState) -> Command:
        """Default appointment operations response"""
        content = "Je suis l'agent des opérations de rendez-vous. Je peux vous aider à prendre, annuler, ou reporter des rendez-vous."
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "patient_id": state.get("patient_id", 0),
            "agent_niveau": "appointment",
            "agent_nom": "appointment_operations",
            "message": "Default appointment response",
            "sentiment": "neutre",
            "action_declenchee": "default_appointment_response"
        }
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=content, name="appointment_operations_agent")
                ],
                "logs": state.get("logs", []) + [log_entry]
            },
            goto="orchestrator_agent"
        )

# --------------------------------------------------------------
# MAIN HIERARCHICAL AGENT SYSTEM
# --------------------------------------------------------------
class HierarchicalAgentSystem:
    """Main system that integrates all 6 levels of agents"""
    
    def __init__(self):
        llm_model = LLMModel()
        self.llm_model = llm_model.get_model()
        self.orchestrator = OrchestratorAgent(self.llm_model)
        self.supervisor = SupervisorAgent()
        self.judge = JudgeAgent()
        self.patient_agent = PatientManagementAgent()
        self.faq_agent = FAQSupportAgent()
        self.availability_agent = AvailabilityCheckerAgent()
        self.appointment_agent = AppointmentOperationsAgent()
    
    def orchestrator_agent(self, state: HierarchicalAgentState) -> Command:
        """Level 0: Orchestrator node"""
        return self.orchestrator.route(state)
    
    def supervisor_agent(self, state: HierarchicalAgentState) -> Command:
        """Level 1: Supervisor node"""
        return self.supervisor.process(state)
    
    def judge_agent(self, state: HierarchicalAgentState) -> Command:
        """Level 2: Judge node"""
        return self.judge.process(state)
    
    def patient_management_agent(self, state: HierarchicalAgentState) -> Command:
        """Level 3: Patient Management node"""
        return self.patient_agent.process(state)
    
    def faq_support_agent(self, state: HierarchicalAgentState) -> Command:
        """Level 3bis: FAQ Support node"""
        return self.faq_agent.process(state)
    
    def availability_checker_agent(self, state: HierarchicalAgentState) -> Command:
        """Level 4: Availability Checker node"""
        return self.availability_agent.process(state)
    
    def appointment_operations_agent(self, state: HierarchicalAgentState) -> Command:
        """Level 5: Appointment Operations node"""
        return self.appointment_agent.process(state)
    
    def workflow(self):
        """Build the complete hierarchical workflow"""
        graph = StateGraph(HierarchicalAgentState)
        
        # Add all agent nodes
        graph.add_node("orchestrator_agent", self.orchestrator_agent)
        graph.add_node("supervisor_agent", self.supervisor_agent)
        graph.add_node("judge_agent", self.judge_agent)
        graph.add_node("patient_management_agent", self.patient_management_agent)
        graph.add_node("faq_support_agent", self.faq_support_agent)
        graph.add_node("availability_checker_agent", self.availability_checker_agent)
        graph.add_node("appointment_operations_agent", self.appointment_operations_agent)
        
        # Set entry point
        graph.add_edge(START, "orchestrator_agent")
        
        # Define routing logic
        graph.add_conditional_edges(
            "orchestrator_agent",
            lambda state: state.get("current_agent", ""),
            {
                "patient_management": "supervisor_agent",
                "availability_checker": "supervisor_agent",
                "appointment_operations": "supervisor_agent",
                "faq_support": "faq_support_agent"
            }
        )
        
        # Supervisor routes to specialized agents or judge
        graph.add_conditional_edges(
            "supervisor_agent",
            lambda state: "judge_agent" if state.get("errors") else state.get("current_agent", ""),
            {
                "patient_management": "patient_management_agent",
                "availability_checker": "availability_checker_agent",
                "appointment_operations": "appointment_operations_agent",
                "judge_agent": "judge_agent"
            }
        )
        
        # Judge routes back to orchestrator or ends conversation
        graph.add_conditional_edges(
            "judge_agent",
            lambda state: END if "human_intervention" in str(state.get("logs", [])[-1:]) else "orchestrator_agent"
        )
        
        # All specialized agents should END conversation after responding
        # They should NOT route back to orchestrator (that causes infinite loop)
        graph.add_edge("patient_management_agent", END)
        graph.add_edge("faq_support_agent", END)
        graph.add_edge("availability_checker_agent", END)
        graph.add_edge("appointment_operations_agent", END)
        
        # Compile the graph
        self.app = graph.compile()
        return self.app
    
    def invoke(self, messages: List, patient_id: int = 2):
        """Invoke the hierarchical agent system"""
        initial_state = {
            "messages": messages,
            "patient_id": patient_id,
            "current_niveau": "",
            "current_agent": "",
            "conversation_topic": "",
            "pending_action": None,
            "pending_data": {},
            "logs": [],
            "business_rules": {},
            "errors": []
        }
        
        if not hasattr(self, 'app'):
            self.workflow()
        
        return self.app.invoke(initial_state)
