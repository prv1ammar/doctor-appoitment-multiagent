"""
Streamlit frontend for Hierarchical Multi-Agent Medical Appointment System
Uses the 6-level architecture API.
"""

import streamlit as st
import requests
import json

# Hierarchical API endpoint
HIERARCHICAL_API_URL = "http://127.0.0.1:8007/execute_hierarchical"
# Original API endpoint (for comparison)
ORIGINAL_API_URL = "http://127.0.0.1:8006/execute"

st.set_page_config(
    page_title="Hierarchical Medical Appointment System",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hierarchical Multi-Agent Medical Appointment System")
st.markdown("---")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "patient_id" not in st.session_state:
    st.session_state.patient_id = 2  # Default ID
if "use_hierarchical" not in st.session_state:
    st.session_state.use_hierarchical = True  # Use hierarchical by default

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    # API selection
    use_hierarchical = st.toggle(
        "Use Hierarchical System",
        value=st.session_state.use_hierarchical,
        help="Toggle between hierarchical (6-level) and original system"
    )
    st.session_state.use_hierarchical = use_hierarchical
    
    st.markdown("---")
    st.header("👤 Patient Information")
    
    # Patient ID input
    patient_id = st.number_input(
        "Patient ID",
        min_value=1,
        max_value=99999999,
        value=st.session_state.patient_id,
        help="Enter your patient ID (7-8 digits)"
    )
    st.session_state.patient_id = patient_id
    
    # Check patient info button
    if st.button("🔍 Check My Info", use_container_width=True):
        with st.spinner("Checking patient information..."):
            api_url = HIERARCHICAL_API_URL if use_hierarchical else ORIGINAL_API_URL
            try:
                response = requests.post(
                    api_url,
                    json={"messages": f"Get my patient information", "id_number": patient_id},
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                    if "messages" in result:
                        st.success(f"✅ Patient ID: {patient_id}")
                        # Display patient info
                        for msg in result["messages"]:
                            if isinstance(msg, dict) and msg.get("sender") in ["assistant", "patient_management_agent"]:
                                st.info(msg.get("content", "No information available"))
                                break
                    
                    # Show hierarchical info if available
                    if use_hierarchical and "agent_hierarchy" in result:
                        with st.expander("🔬 Agent Hierarchy Details"):
                            st.json(result["agent_hierarchy"])
                else:
                    st.error("❌ Failed to retrieve patient information")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    st.header("🎯 Available Actions")
    
    if use_hierarchical:
        st.markdown("""
        ### **6-Level Hierarchical System**
        
        **Level 0: Orchestrator** - Routes your request
        **Level 1: Supervisor** - Validates business rules
        **Level 2: Judge** - Resolves conflicts
        **Level 3: Patient Management** - Your data
        **Level 3bis: FAQ** - Information
        **Level 4: Availability** - Doctor schedules
        **Level 5: Appointment** - Booking execution
        
        **Try these:**
        - "Hello" → FAQ agent
        - "Get my patient information" → Patient agent
        - "Is Dr. Mohamed available tomorrow?" → Availability agent
        - "book appointment" → Multi-step booking
        - "What are your services?" → FAQ agent
        """)
    else:
        st.markdown("""
        ### **Original System**
        
        **Try these:**
        - "Book an appointment"
        - "Check doctor availability"
        - "Get my patient info"
        - "What are your services?"
        """)
    
    # System info
    with st.expander("📊 System Information"):
        if use_hierarchical:
            st.success("✅ Using 6-Level Hierarchical System")
            st.info(f"API: {HIERARCHICAL_API_URL}")
        else:
            st.warning("⚠️ Using Original System")
            st.info(f"API: {ORIGINAL_API_URL}")
        
        # Test connection
        if st.button("Test Connection", use_container_width=True):
            try:
                api_url = HIERARCHICAL_API_URL if use_hierarchical else ORIGINAL_API_URL
                response = requests.get(api_url.replace("/execute_hierarchical", "").replace("/execute", ""))
                if response.status_code == 200:
                    st.success("✅ API is reachable")
                else:
                    st.error(f"❌ API error: {response.status_code}")
            except:
                st.error("❌ Cannot connect to API")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    st.header("💬 Chat with Assistant")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for entry in st.session_state.chat_history:
            sender = entry["sender"]
            message = entry["message"]
            agent_info = entry.get("agent_info", {})
            
            if sender == "You":
                with st.chat_message("user"):
                    st.write(message)
            else:
                with st.chat_message("assistant"):
                    # Display message
                    st.write(message)
                    
                    # Show agent info for hierarchical system
                    if use_hierarchical and agent_info:
                        with st.expander(f"🔍 Agent: {agent_info.get('current_agent', 'Unknown')}"):
                            st.caption(f"**Level:** {agent_info.get('current_niveau', 'Unknown')}")
                            st.caption(f"**Topic:** {agent_info.get('conversation_topic', 'Unknown')}")
                            if agent_info.get('business_rules_applied'):
                                st.caption("**Business Rules Applied:**")
                                st.json(agent_info['business_rules_applied'])

with col2:
    st.header("📈 System Status")
    
    # Current system info
    if st.session_state.use_hierarchical:
        st.success("**6-Level Hierarchical System**")
        
        # Agent status indicators
        st.subheader("Agent Levels")
        
        agents = [
            {"level": 0, "name": "Orchestrator", "status": "✅ Active"},
            {"level": 1, "name": "Supervisor", "status": "✅ Active"},
            {"level": 2, "name": "Judge", "status": "✅ Standby"},
            {"level": 3, "name": "Patient", "status": "✅ Active"},
            {"level": "3bis", "name": "FAQ", "status": "✅ Active"},
            {"level": 4, "name": "Availability", "status": "✅ Active"},
            {"level": 5, "name": "Appointment", "status": "✅ Active"},
        ]
        
        for agent in agents:
            st.caption(f"**Level {agent['level']}:** {agent['name']} - {agent['status']}")
        
        st.markdown("---")
        st.caption(f"**Patient ID:** {st.session_state.patient_id}")
        st.caption(f"**Messages:** {len(st.session_state.chat_history)}")
    else:
        st.warning("**Original System**")
        st.caption("Using simple agent routing")

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)
    
    # Add to history
    st.session_state.chat_history.append({
        "sender": "You",
        "message": user_input,
        "agent_info": {}
    })
    
    # Get bot response
    with st.spinner("Thinking..."):
        api_url = HIERARCHICAL_API_URL if use_hierarchical else ORIGINAL_API_URL
        
        try:
            response = requests.post(
                api_url,
                json={"messages": user_input, "id_number": st.session_state.patient_id},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                bot_messages = result.get("messages", [])
                
                # Extract assistant messages
                for msg in bot_messages:
                    if isinstance(msg, dict) and msg.get("sender") not in ["user", "You"]:
                        bot_content = msg.get("content", "No response")
                        agent_info = {}
                        
                        # Get hierarchical info if available
                        if use_hierarchical and "agent_hierarchy" in result:
                            agent_info = result["agent_hierarchy"]
                        
                        # Add to history
                        st.session_state.chat_history.append({
                            "sender": "Assistant",
                            "message": bot_content,
                            "agent_info": agent_info
                        })
                        
                        # Display in chat
                        with chat_container:
                            with st.chat_message("assistant"):
                                st.write(bot_content)
                                
                                # Show agent info for hierarchical
                                if use_hierarchical and agent_info:
                                    with st.expander(f"🔍 Agent: {agent_info.get('current_agent', 'Unknown')}"):
                                        st.caption(f"**Level:** {agent_info.get('current_niveau', 'Unknown')}")
                                        st.caption(f"**Topic:** {agent_info.get('conversation_topic', 'Unknown')}")
                                        if agent_info.get('business_rules_applied'):
                                            st.caption("**Business Rules Applied:**")
                                            st.json(agent_info['business_rules_applied'])
                        break
            else:
                error_msg = f"API Error: {response.status_code}"
                st.session_state.chat_history.append({
                    "sender": "System",
                    "message": error_msg,
                    "agent_info": {}
                })
                with chat_container:
                    with st.chat_message("assistant"):
                        st.error(error_msg)
                        
        except requests.exceptions.Timeout:
            error_msg = "Request timed out. Please try again."
            st.session_state.chat_history.append({
                "sender": "System",
                "message": error_msg,
                "agent_info": {}
            })
            with chat_container:
                with st.chat_message("assistant"):
                    st.error(error_msg)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.session_state.chat_history.append({
                "sender": "System",
                "message": error_msg,
                "agent_info": {}
            })
            with chat_container:
                with st.chat_message("assistant"):
                    st.error(error_msg)

# Footer
st.markdown("---")
st.caption("🏥 Hierarchical Multi-Agent Medical Appointment System v2.0 | 6-Level Architecture")
