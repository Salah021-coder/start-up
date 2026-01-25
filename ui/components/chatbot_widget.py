import streamlit as st
from typing import Optional, Dict

def render_chatbot(analysis_results: Optional[Dict] = None):
    """Render the Gemini chatbot widget safely without blocking UI."""
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 AI Assistant")
        st.markdown("*Powered by Gemini*")
        
        # Ensure session state variables exist
        st.session_state.setdefault("chat_messages", [])
        st.session_state.setdefault("chat_initialized", False)
        st.session_state.setdefault("gemini_client", None)
        
        # Try to initialize Gemini client (non-blocking)
        if st.session_state.gemini_client is None:
            try:
                from ai.chatbot.gemini_client import GeminiClient
                st.session_state.gemini_client = GeminiClient()
            except Exception as e:
                st.session_state.gemini_client = None
                st.warning("⚠️ Gemini AI not configured. Chatbot disabled.")
                st.caption("Add GEMINI_API_KEY to .env or Streamlit secrets to enable.")
        
        # Only initialize chat if client is available
        if st.session_state.gemini_client and not st.session_state.chat_initialized:
            try:
                _initialize_chat(analysis_results)
            except Exception as e:
                st.warning("⚠️ Failed to initialize chat.")
                st.caption(str(e))
                st.session_state.chat_messages = [{
                    "role": "assistant",
                    "content": "Chatbot temporarily unavailable. Analysis features still work."
                }]
                st.session_state.chat_initialized = True
        
        # Display chat messages (even if Gemini failed, show fallback)
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input only if client available
        if st.session_state.gemini_client:
            prompt = st.chat_input("Ask about your analysis...")
            if prompt:
                _handle_message(prompt)
        else:
            st.info("Chat input disabled until Gemini API is configured.")


def _initialize_chat(analysis_results: Optional[Dict] = None):
    """Initialize chat session safely"""
    if not st.session_state.gemini_client:
        return
    
    try:
        from ai.chatbot.prompt_builder import PromptBuilder
        from ai.context.analysis_context import AnalysisContextFormatter
        
        context = AnalysisContextFormatter.format_for_chat(analysis_results) if analysis_results else None
        system_prompt = PromptBuilder.build_system_prompt(context)
        
        st.session_state.gemini_client.initialize_chat(system_prompt)
        
        # Add welcome message
        st.session_state.chat_messages = [{
            "role": "assistant",
            "content": "Hello! Chatbot ready to help you with your land analysis."
        }]
        st.session_state.chat_initialized = True
        if analysis_results:
            st.session_state.last_analysis_id = analysis_results.get('analysis_id')
            
    except Exception as e:
        st.session_state.chat_messages = [{
            "role": "assistant",
            "content": "⚠️ Chatbot temporarily unavailable. Analysis features still work."
        }]
        st.session_state.chat_initialized = True
        print(f"Chat init error: {e}")


def _handle_message(message: str):
    """Send message to Gemini and append response (failsafe)"""
    st.session_state.chat_messages.append({"role": "user", "content": message})
    
    if st.session_state.gemini_client:
        try:
            response = st.session_state.gemini_client.send_message(message)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": "⚠️ Chatbot failed to respond. Try again later."
            })
    else:
        # Fallback response
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": "⚠️ Chatbot disabled. Cannot answer at the moment."
        })
    
    st.rerun()
