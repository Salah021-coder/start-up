# ============================================================================
# FILE: ui/components/chatbot_widget.py (FIXED VERSION)
# ============================================================================

import streamlit as st
from typing import Optional, Dict

def render_chatbot(analysis_results: Optional[Dict] = None):
    """Render the Gemini chatbot widget in sidebar"""
    
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
        
        # Try to initialize Gemini client
        if st.session_state.gemini_client is None:
            try:
                from ai.chatbot.gemini_client import GeminiClient
                st.session_state.gemini_client = GeminiClient()
            except Exception as e:
                st.warning("⚠️ Gemini AI not configured. Chatbot disabled.")
                st.caption(f"Error: {str(e)}")
                st.info("💡 Add GEMINI_API_KEY to .env file to enable chatbot")
                return  # Exit early if Gemini not available
        
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
            # Fallback response if Gemini not available
            response = _get_fallback_response(message)
        
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


def _get_fallback_response(message: str) -> str:
    """Provide fallback responses when Gemini is unavailable"""
    
    message_lower = message.lower()
    
    # Pattern matching for common questions
    if 'score' in message_lower or 'calculate' in message_lower:
        return """The overall score is calculated by combining:
- **AHP Analysis (40%)**: Multi-criteria decision making using weighted factors
- **ML Prediction (60%)**: Machine learning model based on similar land parcels

Each criterion (terrain, infrastructure, environment) is scored 0-10 and weighted according to importance."""
    
    elif 'slope' in message_lower or 'terrain' in message_lower:
        return """Slope analysis measures the steepness of your land:
- **0-3°**: Flat - Excellent for construction
- **3-8°**: Gentle - Good for most uses
- **8-15°**: Moderate - May need terracing
- **15-30°**: Steep - Higher development costs
- **>30°**: Very steep - Limited uses

Lower slopes generally mean lower construction costs and easier access."""
    
    elif 'flood' in message_lower or 'risk' in message_lower:
        return """Risk assessment considers:
- **Flood risk**: Based on historical water occurrence data
- **Slope stability**: Steep areas may have erosion risk
- **Infrastructure access**: Limited access increases development risk
- **Environmental factors**: Protected areas or sensitive ecosystems

Check the detailed insights section for specific risk factors affecting your land."""
    
    elif 'residential' in message_lower or 'why' in message_lower:
        return """Land suitability recommendations are based on:
- **Terrain characteristics**: Slope, elevation, buildability
- **Infrastructure**: Road access, utilities availability
- **Environmental factors**: Flood risk, vegetation, air quality
- **Economic factors**: Development costs, market potential

The top recommendation has the highest combined score across all these factors."""
    
    else:
        return """I'm currently running in offline mode. However, I can still help with:

- General questions about land evaluation
- Explanation of criteria and scoring
- Guidance on interpreting results
- Information about data sources

For detailed, context-aware answers, please configure the Gemini API key in your .env file.

What else would you like to know?"""