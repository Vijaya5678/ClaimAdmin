import os
import sys
import streamlit as st
import google.generativeai as genai
import requests
import subprocess
import time

# === Path Setup ===
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "helpers"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from SmolAgent.hospitalclaimassistant import HospitalClaimAssistant
from helpers.get_policy_and_claim_summary import get_policy_and_claim_summary
from helpers.query_handler import PolicyQueryHandler
from helpers.query_user_policy_doc import PolicyDocQuery

# === Server Management Functions ===
def is_server_running(port):
    """Check if server is running on given port"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/incident/IND-2025-0004", timeout=2)
        return True
    except:
        return False

def start_hp_server():
    """Start the HP server in background"""
    if 'hp_server_port' not in st.session_state:
        # Find free port
        port = os.getenv("MCP_PORT")
        if port is None:
            st.error("Could not find a the port for HP server")
            return None
        
        st.session_state.hp_server_port = port
        
        # # Check if server is already running
        # if is_server_running(port):
        #     st.success(f"HP Server already running on port {port}")
        #     # Remove the message after 3 seconds
        #     time.sleep(3)
        #     success_placeholder.empty()
            
        #     return port
        
        # Start server in background
        try:
            # Get the path to hp_server.py
            # Get the path to SmolAgent directory
            smol_agent_path = os.path.join(os.path.dirname(__file__), "..", "SmolAgent")
            smol_agent_path = os.path.abspath(smol_agent_path)

            # Start uvicorn server
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "hp_server:app", 
                "--reload", 
                "--host", "127.0.0.1", 
                "--port", str(port)
            ]

            # Start process in background with SmolAgent as working directory
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=smol_agent_path 
            )
            
            st.session_state.hp_server_process = process
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if server started successfully
            if is_server_running(port):
                success_placeholder = st.empty()
                success_placeholder.success(f"HP Server started successfully on port {port}")
                
                # Remove the message after 3 seconds
                time.sleep(3)
                success_placeholder.empty()
                return port
            else:
                st.error("Failed to start HP Server")
                return None
                
        except Exception as e:
            st.error(f"Error starting HP Server: {str(e)}")
            return None
    else:
        return st.session_state.hp_server_port

# === Configure Gemini API ===
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# === Initialize HP Server ===
if 'server_initialized' not in st.session_state:
    with st.spinner("Starting HP Server..."):
        server_port = start_hp_server()
        if server_port:
            st.session_state.server_initialized = True
            st.session_state.hp_server_url = f"http://127.0.0.1:{server_port}"
            
        else:
            st.error("Failed to initialize HP Server")

# === Handlers ===
query_handler = PolicyQueryHandler()
doc_query_handler = PolicyDocQuery()

# === Initialize Hospital Claim Assistant ===
hospital_assistant = HospitalClaimAssistant(gemini_api_key=os.getenv("GEMINI_API_KEY"))

# === Streamlit Page Config ===
st.set_page_config(
    page_title="Claim Approval Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === Custom Styles with fix for top padding removal ===
st.markdown("""
    <style>
        /* Remove default Streamlit top padding to push content to top */
        .block-container {
            padding-top: 0rem !important;
        }

        .stApp { background-color: #fafafa; }

        .main-header {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 1.25rem 2rem;
            border-radius: 10px;
            margin-top: 0rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }

        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 600;
        }

        .main-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .stChatMessage.user::before {
            content: url('https://cdn-icons-png.flaticon.com/512/847/847969.png');
            width: 32px; height: 32px; display: inline-block; margin-right: 0.75rem;
            vertical-align: middle;
        }

        .stChatMessage.assistant::before {
            content: url('https://cdn-icons-png.flaticon.com/512/4712/4712109.png');
            width: 32px; height: 32px; display: inline-block; margin-right: 0.75rem;
            vertical-align: middle;
        }

        .stChatMessage {
            border-radius: 12px;
            margin: 1rem 0;
            padding: 1rem;
            display: flex;
            align-items: flex-start;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            max-width: 800px;
        }

        .stChatMessage.user {
            background-color: #eff6ff !important;
            border: 1px solid #dbeafe !important;
            margin-left: auto;
        }

        .stChatMessage.assistant {
            background-color: white !important;
            border: 1px solid #e5e7eb !important;
            margin-right: auto;
        }

        #MainMenu, footer, header { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# === Session Initialization ===
def initialize_session_state():
    if "claim_messages" not in st.session_state:
        st.session_state.claim_messages = [{"role": "assistant", "content": "Welcome to the Claim Assistant.\nPlease enter the user policy number to begin."}]
    if "general_messages" not in st.session_state:
        st.session_state.general_messages = [{"role": "assistant", "content": "Welcome to General Policy Support. How can I help you today?"}]
    if "hospital_assistant_messages" not in st.session_state:
        st.session_state.hospital_assistant_messages = [{"role": "assistant", "content": "Welcome to the Hospital Assistant. You can ask anything related to hospital claim information."}]
    if "policy_verified" not in st.session_state:
        st.session_state.policy_verified = False
    if "policy_id" not in st.session_state:
        st.session_state.policy_id = None
    if "doc_mode" not in st.session_state:
        st.session_state.doc_mode = False

initialize_session_state()

# === Header ===
st.markdown("""
    <div class="main-header">
        <h1>Claim Approval Assistant</h1>
        <p>Streamlining Insurance Claim Approvals</p>
    </div>
""", unsafe_allow_html=True)

# === Server Status Display ===
# if 'hp_server_port' in st.session_state:
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         if is_server_running(st.session_state.hp_server_port):
#             st.success(f"🟢 HP Server running on port {st.session_state.hp_server_port}")
#         else:
#             st.error(f"🔴 HP Server not responding on port {st.session_state.hp_server_port}")

# === Utility Functions ===
def show_main_options():
    return ("Please select an option:\n\n"
            "\n**1.** View Policy and Claim Details\n"
            "\n**2.** Raise a Support Ticket\n"
            "\n**3.** Ask about Uploaded Documents\n\n"
            "Enter the option number (1, 2, or 3) or type 'reset' to start over.")

def handle_policy_menu(option):
    if option == "1":
        policy_summary, claims_summary = get_policy_and_claim_summary(st.session_state.policy_id)
        reply = (
            "#### Policy Summary\n\n"
            f"**Policy Holder:** {policy_summary['policy_holder']}\n\n"
            f"**Total Coverage:** ₹{policy_summary['total_insured_amount']:,}\n\n"
            f"**Used Amount:** ₹{policy_summary['used_amount']:,}\n\n"
            f"**Remaining:** ₹{policy_summary['remaining_amount']:,}\n\n"
            f"**Eligible Conditions:** {', '.join(policy_summary['eligible_diseases'])}\n\n"
        )
        if claims_summary["claims"]:
            reply += "#### Claim History\n\n"
            reply += "| Claim ID | Status | Amount Paid |\n"
            reply += "|----------|--------|-------------|\n"
            for claim in claims_summary["claims"]:
                reply += f"| {claim['claim_id']} | {claim['claim_status']} | ₹{claim['amount_paid']:,} |\n"
            reply += "\n"

        else:
            reply += "#### Claim History\n\nNo claims found for this policy."
    elif option == "2":
        reply = "**Support ticket created successfully.** Our team will contact you within 24 hours."
    elif option == "3":
        st.session_state.doc_mode = True
        reply = "You can now ask questions about your uploaded documents (medical bills, reports, etc.)."
    elif option.lower() == "reset":
        st.session_state.policy_verified = False
        st.session_state.policy_id = None
        st.session_state.doc_mode = False
        reply = st.session_state.claim_messages[0]["content"]
    else:
        reply = "Invalid selection. Please choose 1, 2, 3, or type 'reset'."
    return reply

def handle_uploaded_doc_query(user_input):
    return doc_query_handler.query(policy_id=st.session_state.policy_id, question=user_input)

def handle_general_query(query):
    return query_handler.get_response(query)

def handle_hospital_assistant_query(query):
    try:
        return hospital_assistant.process_query(query)
    except Exception as e:
        return f"I apologize, but I encountered an error processing your request: {str(e)}"

# === Tabs ===

tab1, tab2, tab3 = st.tabs(["Claim Assistant", "General Questions", "Hospital Assistant"])

# === CLAIM TAB ===
with tab1:
    st.markdown("### Claim Approval & Policy Support")
    chat_container = st.container()

    user_input = st.chat_input("Enter your message...")
    if user_input:
        st.session_state.claim_messages.append({"role": "user", "content": user_input})

        if st.session_state.doc_mode:
            if user_input.lower() == "back":
                st.session_state.doc_mode = False
                response = show_main_options()
            else:
                response = handle_uploaded_doc_query(user_input)   #chroma response
                #from src.utils.conversation import Response
                #response= Response(user_input).get_response() #mongo response
        elif not st.session_state.policy_verified:
            result = get_policy_and_claim_summary(user_input)
            if isinstance(result, dict) and "error" in result:
                response = f"**Error:** {result['error']}. Please verify the policy number and try again."
            else:
                st.session_state.policy_verified = True
                st.session_state.policy_id = user_input
                st.session_state.claim_messages.append({"role": "assistant", "content": f"**Policy `{user_input}` verified successfully.**"})
                response = show_main_options()
        else:
            response = handle_policy_menu(user_input)

        st.session_state.claim_messages.append({"role": "assistant", "content": response})

    with chat_container:
        for msg in st.session_state.claim_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# === GENERAL TAB ===
with tab2:
    st.markdown("### General Policy Information & Support")
    chat_container = st.container()

    general_input = st.chat_input("Ask about policies, coverage etc", key="general_input")
    if general_input:
        st.session_state.general_messages.append({"role": "user", "content": general_input})
        if general_input.lower() == "reset":
            st.session_state.general_messages = [{"role": "assistant", "content": "Chat reset. How can I help you with general policy questions?"}]
            st.rerun()
        try:
            response = handle_general_query(general_input)
        except:
            response = "I apologize, but I'm unable to process your request at the moment. Please try again."
        st.session_state.general_messages.append({"role": "assistant", "content": response})

    with chat_container:
        for msg in st.session_state.general_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# === HOSPITAL ASSISTANT TAB ===
with tab3:
    st.markdown("### Hospital Assistant")
    chat_container = st.container()

    hospital_assistant_input = st.chat_input("Ask about hospital incidents (e.g., 'What is the bill amount for Policy number?')", key="hospital_assistant_input")
    if hospital_assistant_input:
        st.session_state.hospital_assistant_messages.append({"role": "user", "content": hospital_assistant_input})
        if hospital_assistant_input.lower() == "reset":
            st.session_state.hospital_assistant_messages = [{"role": "assistant", "content": "Chat reset. Feel free to ask anything about hospital claim information."}]
            st.rerun()
        
        response = handle_hospital_assistant_query(hospital_assistant_input)
        st.session_state.hospital_assistant_messages.append({"role": "assistant", "content": response})

    with chat_container:
        for msg in st.session_state.hospital_assistant_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# === Footer ===
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Clear All Chats", use_container_width=True):
        st.session_state.claim_messages = [{"role": "assistant", "content": "Welcome to the Claim Assistant.\nPlease enter the user policy number to begin."}]
        st.session_state.general_messages = [{"role": "assistant", "content": "Welcome to General Policy Support. How can I help you today?"}]
        st.session_state.hospital_assistant_messages = [{"role": "assistant", "content": "Welcome to Hospital Assistant. You can ask anything related to hospital claim information"}]
        st.session_state.policy_verified = False
        st.session_state.policy_id = None
        st.session_state.doc_mode = False
        st.rerun()

# === Cleanup on app shutdown ===
import atexit

def cleanup():
    """Clean up background processes"""
    if 'hp_server_process' in st.session_state:
        try:
            st.session_state.hp_server_process.terminate()
        except:
            pass

atexit.register(cleanup)