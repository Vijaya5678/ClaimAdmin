import os
import sys

import streamlit as st
from pymongo import MongoClient

# Add helpers folder to path for import
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "helpers"))
# Add root path to load document query module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import google.generativeai as genai

from helpers.get_policy_and_claim_summary import get_policy_and_claim_summary
from helpers.query_handler import PolicyQueryHandler
from helpers    .query_user_policy_doc import PolicyDocQuery

# === Configure Gemini ===
os.environ["GEMINI_API_KEY"] = "AIzaSyBKMV8TARxNEOnTvA4sviV1wEb0uZA9pv4"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

query_handler = PolicyQueryHandler()
doc_query_handler = PolicyDocQuery()

# === Streamlit UI Setup ===
st.set_page_config(page_title="Claim Approver Assistant", layout="centered")
st.markdown("<h1 style='color:#1a73e8;'>💬 Claim Approver Assistant</h1>", unsafe_allow_html=True)

# === Session State Init ===
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I’m your Claim Approver Assistant.\n\nWhat would you like to do?\n\n"
                   "1. Know about a specific policy (enter policy number)\n"
                   "2. Ask about policies in general\n\n"
                   "Select your option:\n_(Type 'exit' to end at any time.)_"
    }]
if "mode" not in st.session_state:
    st.session_state.mode = None
if "policy_verified" not in st.session_state:
    st.session_state.policy_verified = False
if "policy_id" not in st.session_state:
    st.session_state.policy_id = None
if "doc_mode" not in st.session_state:
    st.session_state.doc_mode = False


# === Utility Functions ===
def handle_policy_menu(option):
    if option == "1":
        policy_summary, _ = get_policy_and_claim_summary(st.session_state.policy_id)
        reply = (
            f"**Policy Summary:**\n\n"
            f"- Policy Holder: {policy_summary['policy_holder']}\n"
            f"- Total Coverage: ₹{policy_summary['total_insured_amount']}\n"
            f"- Used: ₹{policy_summary['used_amount']}\n"
            f"- Remaining: ₹{policy_summary['remaining_amount']}\n"
            f"- Eligible Conditions: {', '.join(policy_summary['eligible_diseases'])}"
        )

    elif option == "2":
        _, claims_summary = get_policy_and_claim_summary(st.session_state.policy_id)
        if claims_summary["claims"]:
            claim_texts = [
                f"- **Claim ID:** {c['claim_id']}, Status: {c['claim_status']}, Paid: ₹{c['amount_paid']}"
                for c in claims_summary["claims"]
            ]
            reply = "**Claim History:**\n" + "\n".join(claim_texts)
        else:
            reply = "No claims found for this policy."

    elif option == "3":
        reply = "🎫 Support ticket created. Our team will reach out to you shortly!"

    elif option == "4":
        st.session_state.doc_mode = True
        reply = "Ask your question about the uploaded documents (e.g., reports, bills):"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        return

    elif option.lower() == "back":
        st.session_state.mode = None
        st.session_state.policy_verified = False
        st.session_state.policy_id = None
        st.session_state.doc_mode = False
        reply = "You are now back at the main menu.\n\n1. Know about a specific policy\n2. Ask about policies in general\n\nSelect your option:"

    else:
        reply = "Please select a valid option: 1, 2, 3, 4 or type `back` to return."

    st.session_state.messages.append({"role": "assistant", "content": reply})


def handle_general_query(query):
    result = query_handler.get_response(query)
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.session_state.messages.append({"role": "assistant", "content": "\n(Type 'back' to return to main menu.)"})


def handle_uploaded_doc_query(user_input):
    response = doc_query_handler.query(policy_id=st.session_state.policy_id, question=user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.messages.append({"role": "assistant", "content": "Ask another document-related question, or type `back` to return."})


# === Chat Input Handling ===
user_input = st.chat_input("Type your message here...")

if user_input:
    user_input = user_input.strip()

    if user_input.lower() == "exit":
        st.session_state.clear()
        st.markdown("<div style='color: green;'>👋 Thank you for using Claim Admin Assistant. Your session has ended.</div>",
                    unsafe_allow_html=True)
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.doc_mode:
        if user_input.lower() == "back":
            st.session_state.doc_mode = False
            reply = (
                f"Select an option:\n"
                f"1. View Policy Details\n"
                f"2. View Claim History\n"
                f"3. Raise a Support Ticket\n"
                f"4. Ask about uploaded documents\n\n"
                f"_(Type the number or `back` to return)_"
            )
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            handle_uploaded_doc_query(user_input)

    elif st.session_state.mode is None:
        if user_input == "1":
            st.session_state.mode = "policy"
            st.session_state.messages.append(
                {"role": "assistant", "content": "Please enter your policy number:"})
        elif user_input == "2":
            st.session_state.mode = "general"
            st.session_state.messages.append(
                {"role": "assistant", "content": "You can now ask anything about the policies."})
        else:
            st.session_state.messages.append(
                {"role": "assistant", "content": "Please select a valid option: 1 or 2."})

    elif st.session_state.mode == "policy":
        if not st.session_state.policy_verified:
            result = get_policy_and_claim_summary(user_input)
            if isinstance(result, dict) and "error" in result:
                reply = f"❌ {result['error']}. Please provide a valid policy number."
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.session_state.policy_verified = True
                st.session_state.policy_id = user_input  # Preserve case
                reply = (
                    f"✅ Policy `{user_input}` verified successfully!\n\n"
                    f"Select an option:\n"
                    f"1. View Policy Details\n"
                    f"2. View Claim History\n"
                    f"3. Raise a Support Ticket\n"
                    f"4. Ask about uploaded documents\n\n"
                    f"_(Type the number or `back` to return)_"
                )
                st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            handle_policy_menu(user_input)

    elif st.session_state.mode == "general":
        if user_input.lower() == "back":
            st.session_state.mode = None
            st.session_state.messages.append({"role": "assistant", "content": "Back at main menu.\n\n1. Know about a specific policy\n2. Ask about policies in general\n\nSelect your option:"})
        else:
            handle_general_query(user_input)

# === Display Chat Messages ===
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])
