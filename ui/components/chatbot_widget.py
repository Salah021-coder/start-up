import streamlit as st
from typing import Optional, Dict

def render_chatbot(analysis_results: Optional[Dict] = None):
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 AI Assistant")
        
        # 1. State Management
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'gemini_client' not in st.session_state:
            try:
                from ai.chatbot.gemini_client import GeminiClient
                st.session_state.gemini_client = GeminiClient()
            except Exception as e:
                st.error(f"Setup Error: {e}")
                return

        # 2. Chat Initialization (When analysis changes)
        current_id = analysis_results.get('analysis_id') if analysis_results else None
        if not st.session_state.get('chat_initialized') or current_id != st.session_state.get('last_analysis_id'):
            _initialize_chat_session(analysis_results)
            st.session_state.last_analysis_id = current_id
            st.session_state.chat_initialized = True

        # 3. Display Chat
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 4. Input handling
        prompt = st.chat_input("Ask about your land...")
        if prompt:
            _process_user_input(prompt)

def _initialize_chat_session(analysis_results):
    from ai.chatbot.prompt_builder import PromptBuilder
    from ai.context.analysis_context import AnalysisContextFormatter
    
    context = AnalysisContextFormatter.format_for_chat(analysis_results) if analysis_results else ""
    sys_prompt = PromptBuilder.build_system_prompt(context)
    
    try:
        st.session_state.gemini_client.initialize_chat(sys_prompt)
        welcome_msg = "Hello! I've analyzed your land data. How can I help?" if analysis_results else "Hello! How can I help you today?"
        st.session_state.chat_messages = [{"role": "assistant", "content": welcome_msg}]
    except Exception as e:
        st.error(f"Initialization Failed: {e}")

def _process_user_input(prompt: str):
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = st.session_state.gemini_client.send_message(prompt)
            message_placeholder.markdown(response)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
        except RuntimeError as e:
            if "QUOTA_EXCEEDED" in str(e):
                err_text = "🚫 **Quota Reached**: I've hit the limit for free messages (20/day). Please try again in a few hours or tomorrow!"
                message_placeholder.warning(err_text)
                st.session_state.chat_messages.append({"role": "assistant", "content": err_text})
            else:
                message_placeholder.error(f"Error: {e}")
    st.rerun()
