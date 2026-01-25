# ============================================================================
# FILE: ui/components/chatbot_widget.py (ERROR-HANDLING VERSION)
# ============================================================================

import streamlit as st
from typing import Optional, Dict

def render_chatbot(analysis_results: Optional[Dict] = None):
    """Render the Gemini chatbot widget in sidebar with error handling"""
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 AI Assistant")
        st.markdown("*Powered by Gemini*")
        
        # Initialize session state for chat
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        if 'chat_initialized' not in st.session_state:
            st.session_state.chat_initialized = False
        
        if 'gemini_client' not in st.session_state:
            st.session_state.gemini_client = None
        
        if 'gemini_error' not in st.session_state:
            st.session_state.gemini_error = None
        
        # Try to initialize Gemini client (only once)
        if st.session_state.gemini_client is None and st.session_state.gemini_error is None:
            try:
                from ai.chatbot.gemini_client import GeminiClient
                st.session_state.gemini_client = GeminiClient()
                st.session_state.gemini_error = None
                
            except RuntimeError as e:
                # Store the error message
                st.session_state.gemini_error = str(e)
                st.session_state.gemini_client = None
            except Exception as e:
                st.session_state.gemini_error = f"Unexpected error: {str(e)}"
                st.session_state.gemini_client = None
        
        # If there's an error, show helpful message
        if st.session_state.gemini_error:
            st.warning("⚠️ **Chatbot Unavailable**")
            
            with st.expander("📋 Details & Setup", expanded=False):
                st.error(st.session_state.gemini_error)
                
                st.markdown("""
                **To enable the chatbot:**
                
                1. **Get Gemini API Key:**
                   - Visit: https://aistudio.google.com/app/apikey
                   - Click "Create API Key"
                   - Copy the key
                
                2. **For Streamlit Cloud:**
                   - Go to: Your App → Settings → Secrets
                   - Add: `GEMINI_API_KEY = "your-key-here"`
                   - Save and reboot app
                
                3. **For Local Development:**
                   - Create `.streamlit/secrets.toml`
                   - Add: `GEMINI_API_KEY = "your-key-here"`
                   - Restart app
                
                ℹ️ **Note:** All analysis features work without the chatbot!
                """)
            
            # Show that analysis still works
            st.info("✅ Land analysis features are fully functional")
            return  # Exit early - don't show chat interface
        
        # If Gemini is available, proceed with chat
        # Initialize chat on first load or when results change
        if not st.session_state.chat_initialized or (
            analysis_results and 
            analysis_results.get('analysis_id') != st.session_state.get('last_analysis_id')
        ):
            _initialize_chat(analysis_results)
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        # Quick action buttons (only if analysis results available)
        if analysis_results:
            st.markdown("#### Quick Questions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Score", key="q_score", use_container_width=True):
                    _handle_message("How was the overall score calculated?")
                if st.button("🏘️ Why?", key="q_why", use_container_width=True):
                    _handle_message("Why is this land use recommended?")
            
            with col2:
                if st.button("⛰️ Slope", key="q_slope", use_container_width=True):
                    _handle_message("Explain the slope analysis")
                if st.button("💧 Risk", key="q_risk", use_container_width=True):
                    _handle_message("What are the risks?")
        
        # Chat input
        prompt = st.chat_input("Ask about your analysis...")
        if prompt:
            _handle_message(prompt)


def _initialize_chat(analysis_results: Optional[Dict] = None):
    """Initialize the chat session"""
    
    # Only initialize if client exists
    if st.session_state.gemini_client is None:
        return
    
    try:
        from ai.chatbot.prompt_builder import PromptBuilder
        from ai.context.analysis_context import AnalysisContextFormatter
        
        # Build system prompt
        formatted_context = None
        if analysis_results:
            formatted_context = AnalysisContextFormatter.format_for_chat(analysis_results)
        
        system_prompt = PromptBuilder.build_system_prompt(formatted_context)
        
        # Initialize Gemini client
        st.session_state.gemini_client.initialize_chat(system_prompt)
        
        # Add welcome message
        welcome = _get_welcome_message(analysis_results)
        st.session_state.chat_messages = [{
            "role": "assistant",
            "content": welcome
        }]
        
        st.session_state.chat_initialized = True
        if analysis_results:
            st.session_state.last_analysis_id = analysis_results.get('analysis_id')
            
    except Exception as e:
        st.error(f"Failed to initialize chat: {str(e)}")
        st.session_state.chat_messages = [{
            "role": "assistant",
            "content": "⚠️ Chatbot temporarily unavailable. Analysis features still work!"
        }]


def _handle_message(message: str):
    """Handle user message and get AI response"""
    
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": message
    })
    
    # Get AI response
    try:
        if st.session_state.gemini_client is not None:
            response = st.session_state.gemini_client.send_message(message)
        else:
            response = "⚠️ Chatbot is not available. Please configure GEMINI_API_KEY."
        
        # Add AI response
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })
        
    except Exception as e:
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": f"⚠️ Sorry, I encountered an error: {str(e)}\n\nPlease try rephrasing your question."
        })
    
    st.rerun()


def _get_welcome_message(analysis_results: Optional[Dict] = None) -> str:
    """Generate contextual welcome message"""
    
    if analysis_results:
        score = analysis_results.get('overall_score', 0)
        recommendations = analysis_results.get('recommendations', [])
        top_use = recommendations[0].get('usage_type', 'development') if recommendations else 'development'
        
        return f"""Hello! I'm your AI land analysis assistant powered by Gemini. 

Your land scored **{score:.1f}/10** with **{top_use}** as the top recommendation.

I can help you understand:
- Why certain land uses are recommended
- What the criteria scores mean
- Details about terrain, soil, and infrastructure
- Potential risks and opportunities

What would you like to know?"""
    else:
        return """Hello! I'm your AI land analysis assistant powered by Gemini.

I can help you:
- Understand how land evaluation works
- Explain different criteria
- Guide you through the analysis process
- Answer questions about AHP and ML models

How can I assist you today?"""
