import streamlit as st
import llm_test
import database_test
import chroma_test

# Configuration
st.set_page_config(
    page_title="AI Launchpad",
    page_icon="🚀",
    layout="centered"
)

def main():
    """Main application"""
    st.title("🚀 AI Launchpad")
    
    st.markdown("---")
    
    # LLM Test Section
    llm_test.render()
    
    st.markdown("---")
    
    # Database Test Section
    database_test.render()
    
    st.markdown("---")
    
    # ChromaDB Test Section
    chroma_test.render()
    
    st.markdown("---")
    st.caption("Build your AI-powered Streamlit app with AI Launchpad! 🎉")

if __name__ == "__main__":
    main()

