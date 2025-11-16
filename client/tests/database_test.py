import streamlit as st
import os

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Database environment variables
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ai_launchpad')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

def test_db_connection() -> dict:
    """Test PostgreSQL database connection"""
    if not PSYCOPG2_AVAILABLE:
        return {"error": "psycopg2 not installed. Run: pip install psycopg2-binary"}
    
    if not DB_PASSWORD:
        return {"error": "Database not configured. Set POSTGRES_PASSWORD in .env.postgres"}
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
        """)
        users_table_exists = cursor.fetchone()[0]
        
        user_count = 0
        if users_table_exists:
            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_NAME,
            "user": DB_USER,
            "version": version,
            "users_table_exists": users_table_exists,
            "user_count": user_count
        }
        
    except psycopg2.OperationalError as e:
        return {"error": f"Connection failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

def render():
    """Render database test section"""
    st.markdown("### Test your Database connection")
    
    # Show database status
    if DB_PASSWORD:
        st.info(f"**Database:** {DB_NAME} @ {DB_HOST}:{DB_PORT}")
    else:
        st.warning("⚠️ Database not configured. Enable PostgreSQL in `services.config` and create `.env.postgres`")
    
    # Test button
    if st.button("🗄️ Test Database Connection", type="secondary", use_container_width=True, disabled=not DB_PASSWORD):
        with st.spinner("Connecting to database..."):
            result = test_db_connection()
            
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            else:
                st.success("✅ Database connection successful!")
                
                st.markdown("### Connection Details:")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Host", result['host'])
                    st.metric("Database", result['database'])
                with col2:
                    st.metric("Port", result['port'])
                    st.metric("User", result['user'])
                
                with st.expander("📊 Database Information"):
                    st.markdown(f"**PostgreSQL Version:**")
                    st.code(result['version'], language=None)
                    st.markdown(f"**Users Table:** {'✅ Exists' if result['users_table_exists'] else '❌ Not found'}")
                    if result['users_table_exists']:
                        st.markdown(f"**User Count:** {result['user_count']}")

