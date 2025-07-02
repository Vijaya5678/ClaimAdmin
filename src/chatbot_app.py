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
st.set_page_config(page_title="Claim Approver Assistant", layout="centered", initial_sidebar_state="collapsed")

# === Custom Styles ===
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stChatMessage {
            padding: 10px 18px;
            margin-bottom: 12px;
            border-radius: 12px;
        }
        .stChatMessage.user {
            background-color: #e3f2fd;
        }
        .stChatMessage.assistant {
            background-color: #f1f3f4;
        }
        .option-box {
            padding: 10px;
            background-color: #e8f0fe;
            border-radius: 8px;
            margin-top: 12px;
            font-size: 15px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#1a73e8;'>🤖 Claim Approver Assistant</h1>", unsafe_allow_html=True)

# === Session State Init ===
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I’m your Claim Approver Assistant.\n\nWhat would you like to do?\n\n"
                   "1. Know about a specific policy (enter policy number)\n"
                   "2. Ask about policies in general\n\n"
                   "Type the option number (1, 2, or 3) or type `exit` to end at any time."
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


# === Core Handlers ===
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
            reply += "ℹNo claims found for this policy."

    elif option == "2":
        reply = "A support ticket has been created. Our team will get back to you shortly."

    elif option == "3":
        st.session_state.doc_mode = True
        reply = "You can now ask questions about your uploaded documents (e.g., medical bills, reports)."

    elif option.lower() == "back":
        st.session_state.mode = None
        st.session_state.policy_verified = False
        st.session_state.policy_id = None
        st.session_state.doc_mode = False
        reply = st.session_state.messages[0]["content"]
    else:
        reply = "⚠️ Invalid selection. Please choose 1, 2, 3 or type `back`."

    st.session_state.messages.append({"role": "assistant", "content": reply})



def handle_general_query(query):
    result = query_handler.get_response(query)
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.session_state.messages.append({"role": "assistant", "content": "_(Type 'back' to return to main menu.)_"})


def handle_uploaded_doc_query(user_input):
    response = doc_query_handler.query(policy_id=st.session_state.policy_id, question=user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.messages.append({"role": "assistant", "content": "_Ask another question or type `back`._"})

# === User Input ===
user_input = st.chat_input("Type your message here...")

if user_input:
    user_input = user_input.strip()
    if user_input.lower() == "exit":
        st.session_state.clear()
        st.success("👋 Session ended. Thank you for using Claim Approver Assistant.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.doc_mode:
        if user_input.lower() == "back":
            st.session_state.doc_mode = False
            st.session_state.messages.append({"role": "assistant", "content": show_main_options()})
        else:
            handle_uploaded_doc_query(user_input)

    elif st.session_state.mode is None:
        if user_input == "1":
            st.session_state.mode = "policy"
            st.session_state.messages.append({"role": "assistant", "content": "Please enter the policy number:"})
        elif user_input == "2":
            st.session_state.mode = "general"
            st.session_state.messages.append({"role": "assistant", "content": "Ask me anything about the insurance policies."})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Please choose either `1` or `2` to proceed."})

    elif st.session_state.mode == "policy":
        if not st.session_state.policy_verified:
            result = get_policy_and_claim_summary(user_input)
            if isinstance(result, dict) and "error" in result:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {result['error']}. Please try again."})
            else:
                st.session_state.policy_verified = True
                st.session_state.policy_id = user_input
                st.session_state.messages.append({"role": "assistant", "content": f"✅ Policy `{user_input}` verified."})
                st.session_state.messages.append({"role": "assistant", "content": show_main_options()})
        else:
            handle_policy_menu(user_input)

    elif st.session_state.mode == "general":
        if user_input.lower() == "back":
            st.session_state.mode = None
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.messages[0]["content"]})
        else:
            handle_general_query(user_input)

# === Chat UI ===
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])
