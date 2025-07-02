import os
import sys
import streamlit as st
from pymongo import MongoClient
import google.generativeai as genai

# === Path Setup ===
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "helpers"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from helpers.get_policy_and_claim_summary import get_policy_and_claim_summary
from helpers.query_handler import PolicyQueryHandler
from helpers.query_user_policy_doc import PolicyDocQuery

# === Configure Gemini API ===
os.environ["GEMINI_API_KEY"] = "AIzaSyBKMV8TARxNEOnTvA4sviV1wEb0uZA9pv4"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# === Handlers ===
query_handler = PolicyQueryHandler()
doc_query_handler = PolicyDocQuery()

# === Streamlit Page Config ===
st.set_page_config(page_title="Claim Approver Assistant", layout="centered")

# === Custom Styles ===
st.markdown("""
    <style>
        .stChatMessage.user {
            background-color: #DCF8C6 !important;
            border-radius: 10px !important;
            margin-left: auto !important;
            margin-right: 0 !important;
            max-width: 75%;
        }
        .stChatMessage.assistant {
            background-color: #F1F0F0 !important;
            border-radius: 10px !important;
            margin-right: auto !important;
            margin-left: 0 !important;
            max-width: 75%;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# === Session State ===
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! 👋 I'm your Claim Approver Assistant.\n\nPlease enter your policy number to begin."
    }]
if "mode" not in st.session_state:
    st.session_state.mode = None
if "policy_verified" not in st.session_state:
    st.session_state.policy_verified = False
if "policy_id" not in st.session_state:
    st.session_state.policy_id = None
if "doc_mode" not in st.session_state:
    st.session_state.doc_mode = False

# === Utility ===
def show_main_options():
    return (
        "Please choose an option:\n"
        "1. View Policy and Claim Details\n"
        "2. Raise a Support Ticket\n"
        "3. Ask about Uploaded Documents\n\n"
        "Type the option number (1, 2, or 3) or type `back` to return to the main menu."
    )

# === Chat Handlers ===
def handle_policy_menu(option):
    if option == "1":
        policy_summary, claims_summary = get_policy_and_claim_summary(st.session_state.policy_id)
        reply = (
            f"**Policy Summary**\n"
            f"- **Policy Holder:** {policy_summary['policy_holder']}\n"
            f"- **Total Coverage:** ₹{policy_summary['total_insured_amount']}\n"
            f"- **Used Amount:** ₹{policy_summary['used_amount']}\n"
            f"- **Remaining:** ₹{policy_summary['remaining_amount']}\n"
            f"- **Eligible Conditions:** {', '.join(policy_summary['eligible_diseases'])}\n\n"
        )
        if claims_summary["claims"]:
            table_header = "| Claim ID | Status | Amount Paid (₹) |\n|----------|--------|------------------|"
            table_rows = [
                f"| `{c['claim_id']}` | {c['claim_status']} | ₹{c['amount_paid']} |"
                for c in claims_summary["claims"]
            ]
            claims_table = "\n".join([table_header] + table_rows)
            reply += f"**Claim History:**\n{claims_table}"
        else:
            reply += "ℹ️ No claims found for this policy."

    elif option == "2":
        reply = "✅ A support ticket has been created. Our team will get back to you shortly."

    elif option == "3":
        st.session_state.doc_mode = True
        reply = "📄 You can now ask questions about your uploaded documents (e.g., medical bills, reports)."

    elif option.lower() == "back":
        st.session_state.mode = None
        st.session_state.policy_verified = False
        st.session_state.policy_id = None
        st.session_state.doc_mode = False
        reply = st.session_state.messages[0]["content"]
    else:
        reply = "⚠️ Invalid selection. Please choose 1, 2, 3 or type `back`."

    return reply

def handle_general_query(query):
    result = query_handler.get_response(query)
    return result

def handle_uploaded_doc_query(user_input):
    response = doc_query_handler.query(policy_id=st.session_state.policy_id, question=user_input)
    return response

# === UI Title ===
st.title("🤖 Claim Approver Assistant")

# === Chat History Display ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === Chat Input Handler ===
if user_input := st.chat_input("Type your message here..."):
    user_input = user_input.strip()
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Handle exit
    if user_input.lower() == "exit":
        st.session_state.clear()
        st.success("👋 Session ended. Thank you for using Claim Approver Assistant.")
        st.stop()

    # Process user input and generate response
    assistant_response = None
    
    if st.session_state.doc_mode:
        if user_input.lower() == "back":
            st.session_state.doc_mode = False
            assistant_response = show_main_options()
        else:
            assistant_response = handle_uploaded_doc_query(user_input)
            # Add additional message for doc mode
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
            assistant_response = "_Ask another question or type `back`._"

    elif st.session_state.mode is None:
        if not st.session_state.policy_verified:
            result = get_policy_and_claim_summary(user_input)
            if isinstance(result, dict) and "error" in result:
                assistant_response = f"❌ {result['error']}. Please try again."
            else:
                st.session_state.policy_verified = True
                st.session_state.policy_id = user_input
                # Add verification message
                st.session_state.messages.append({"role": "assistant", "content": f"✅ Policy `{user_input}` verified."})
                with st.chat_message("assistant"):
                    st.markdown(f"✅ Policy `{user_input}` verified.")
                assistant_response = show_main_options()
        else:
            assistant_response = handle_policy_menu(user_input)

    elif st.session_state.mode == "policy":
        assistant_response = handle_policy_menu(user_input)

    elif st.session_state.mode == "general":
        if user_input.lower() == "back":
            st.session_state.mode = None
            assistant_response = st.session_state.messages[0]["content"]
        else:
            assistant_response = handle_general_query(user_input)
            # Add additional message for general mode
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
            assistant_response = "_(Type 'back' to return to main menu.)_"

    # Add assistant response to chat
    if assistant_response:
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

# # === Optional: Policy Comparison Q&A ===
# with st.expander("🛠 General Policy Comparison", expanded=False):
#     general_query = st.text_input("Ask about policies:", key="general_query")
#     if general_query:
#         general_response = query_handler.get_response(general_query)
#         st.markdown(f"**Response:**\n\n{general_response}")