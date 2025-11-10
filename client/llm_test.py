import streamlit as st
import requests
import os

# Environment variables
LLM_DISPATCHER = os.getenv('LLM_DISPATCHER', 'llm-dispatcher')
LLM_DISPATCHER_PORT = os.getenv('LLM_DISPATCHER_PORT', '5100')
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'local')

def query_llm(prompt: str) -> dict:
    """Send a query to the LLM dispatcher"""
    url = f"http://{LLM_DISPATCHER}:{LLM_DISPATCHER_PORT}/query"
    
    try:
        response = requests.post(
            url,
            json={"prompt": prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Request failed with status {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out after 60 seconds"}
    except Exception as e:
        return {"error": f"Failed to connect to LLM: {str(e)}"}

def render():
    """Render LLM test section"""
    st.markdown("### Test your LLM connection")
    
    # Display current provider
    st.info(f"**Current LLM Provider:** {LLM_PROVIDER}")
    
    # Test button
    if st.button("🧪 Test LLM Connection", type="primary", use_container_width=True):
        with st.spinner("Querying the LLM..."):
            result = query_llm("What is the capital of France?")
            
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            else:
                st.success("✅ LLM connection successful!")
                
                st.markdown("### Response:")
                st.markdown(result.get('response', 'No response received'))
                
                with st.expander("📊 Response Metadata"):
                    st.json({
                        "provider": result.get('provider', 'unknown'),
                        "model": result.get('model', 'unknown'),
                        **{k: v for k, v in result.items() 
                           if k not in ['response', 'provider', 'model']}
                    })

