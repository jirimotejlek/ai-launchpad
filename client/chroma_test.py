import streamlit as st
import os

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# ChromaDB environment variables
CHROMA_HOST = os.getenv('CHROMA_HOST', 'chroma')
CHROMA_PORT = os.getenv('CHROMA_PORT', '8000')

def test_chroma_connection() -> dict:
    """Test ChromaDB connection"""
    if not CHROMADB_AVAILABLE:
        return {"error": "chromadb not installed. Run: pip install chromadb"}
    
    try:
        # Connect to ChromaDB
        client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=int(CHROMA_PORT)
        )
        
        # Test heartbeat
        heartbeat = client.heartbeat()
        
        # Create a temporary test collection
        test_collection_name = "test_collection_temp"
        
        # Delete if exists (cleanup from previous test)
        try:
            client.delete_collection(name=test_collection_name)
        except:
            pass
        
        # Create collection
        collection = client.create_collection(name=test_collection_name)
        
        # Add test documents
        collection.add(
            documents=[
                "ChromaDB is a vector database",
                "AI Launchpad supports multiple services",
                "Docker makes deployment easy"
            ],
            metadatas=[
                {"source": "test1", "type": "info"},
                {"source": "test2", "type": "info"},
                {"source": "test3", "type": "info"}
            ],
            ids=["doc1", "doc2", "doc3"]
        )
        
        # Query the collection
        results = collection.query(
            query_texts=["What is ChromaDB?"],
            n_results=1
        )
        
        # Get collection info
        collection_count = collection.count()
        
        # Get all collections
        all_collections = client.list_collections()
        
        # Cleanup - delete test collection
        client.delete_collection(name=test_collection_name)
        
        return {
            "success": True,
            "host": CHROMA_HOST,
            "port": CHROMA_PORT,
            "heartbeat": heartbeat,
            "test_query_result": results['documents'][0][0] if results['documents'] else "No results",
            "test_collection_count": collection_count,
            "total_collections": len(all_collections)
        }
        
    except Exception as e:
        return {"error": f"Connection failed: {str(e)}"}

def render():
    """Render ChromaDB test section"""
    st.markdown("### Test your ChromaDB connection")
    
    # Show ChromaDB status
    st.info(f"**ChromaDB:** {CHROMA_HOST}:{CHROMA_PORT}")
    
    # Test button
    if st.button("🔷 Test ChromaDB Connection", type="secondary", use_container_width=True):
        with st.spinner("Connecting to ChromaDB..."):
            result = test_chroma_connection()
            
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
                
                # Show helpful hints
                if "not installed" in result['error']:
                    st.info("💡 ChromaDB is already in requirements.txt. Rebuild the container:\n```\nlaunchpad build-local\nlaunchpad run-local\n```")
                else:
                    st.info("💡 Make sure ChromaDB is enabled:\n1. Edit `services.config` and set `ENABLE_CHROMA=true`\n2. Run `launchpad build-local && launchpad run-local`")
            else:
                st.success("✅ ChromaDB connection successful!")
                
                st.markdown("### Connection Details:")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Host", result['host'])
                    st.metric("Collections", result['total_collections'])
                with col2:
                    st.metric("Port", result['port'])
                    st.metric("Heartbeat", result['heartbeat'])
                
                with st.expander("📊 Test Results"):
                    st.markdown(f"**Test Query:**")
                    st.code("What is ChromaDB?", language=None)
                    st.markdown(f"**Best Match:**")
                    st.code(result['test_query_result'], language=None)
                    st.markdown(f"**Test Collection Documents:** {result['test_collection_count']}")
                    st.success("✅ Test collection created, queried, and cleaned up successfully!")

