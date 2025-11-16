import streamlit as st
import requests
import os
import json
from typing import Generator

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

def query_llm_stream(prompt: str) -> Generator[str, None, dict]:
    """Send a streaming query to the LLM dispatcher and yield tokens as they arrive"""
    url = f"http://{LLM_DISPATCHER}:{LLM_DISPATCHER_PORT}/query/stream"
    
    metadata = {}
    
    try:
        response = requests.post(
            url,
            json={"prompt": prompt},
            stream=True,
            timeout=60
        )
        
        if response.status_code != 200:
            yield f"Error: Request failed with status {response.status_code}"
            return metadata
        
        # Parse SSE stream
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                # SSE format: "data: {json}"
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove 'data: ' prefix
                    
                    try:
                        chunk = json.loads(data_str)
                        
                        # Check for errors
                        if 'error' in chunk:
                            yield f"\n\nError: {chunk['error']}"
                            return metadata
                        
                        # Check if stream is done
                        if chunk.get('done'):
                            # Store metadata for later display
                            metadata = {k: v for k, v in chunk.items() if k != 'done'}
                            break
                        
                        # Yield token
                        if 'token' in chunk:
                            yield chunk['token']
                    
                    except json.JSONDecodeError:
                        # Skip malformed JSON
                        pass
    
    except requests.exceptions.Timeout:
        yield "\n\nError: Request timed out after 60 seconds"
    except Exception as e:
        yield f"\n\nError: Failed to connect to LLM: {str(e)}"
    
    return metadata

def stream_with_metadata(prompt: str):
    """Wrapper to handle streaming and metadata collection"""
    metadata = {}
    full_text = ""
    
    stream_gen = query_llm_stream(prompt)
    
    try:
        while True:
            token = next(stream_gen)
            full_text += token
            yield token
    except StopIteration as e:
        # Capture the return value (metadata)
        metadata = e.value if e.value else {}
    
    return metadata

def render():
    """Render LLM test section"""
    st.markdown("### Test your LLM connection")

    # Display current provider
    st.info(f"**Current LLM Provider:** {LLM_PROVIDER}")

    # Test button
    if st.button("🧪 Test LLM Connection (Streaming)", type="primary", use_container_width=True):
        st.markdown("### Response:")
        
        # Stream the response
        try:
            # Manually handle streaming to capture metadata
            full_response = ""
            metadata = {}
            response_container = st.empty()
            
            stream_gen = query_llm_stream("What is the capital of France?")
            
            try:
                while True:
                    token = next(stream_gen)
                    full_response += token
                    # Update the display with accumulated text
                    response_container.markdown(full_response)
            except StopIteration as e:
                # Capture the return value (metadata)
                metadata = e.value if e.value else {}
            
            # Check if the response contains an error
            if full_response and "Error:" in full_response:
                st.error(f"❌ {full_response}")
            else:
                st.success("✅ LLM connection successful!")
                
                # Display metadata if available
                if metadata:
                    with st.expander("📊 Response Metadata"):
                        st.json({
                            "provider": LLM_PROVIDER,
                            **metadata
                        })
                else:
                    with st.expander("📊 Response Metadata"):
                        st.info(f"Provider: {LLM_PROVIDER}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

