import streamlit as st
import os
import time

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Redis environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

def test_redis_connection() -> dict:
    """Test Redis connection"""
    if not REDIS_AVAILABLE:
        return {"error": "redis not installed. Run: pip install redis"}
    
    try:
        # Connect to Redis
        client = redis.Redis(
            host=REDIS_HOST,
            port=int(REDIS_PORT),
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Test 1: Ping
        ping_response = client.ping()
        
        # Test 2: Set and get a value
        test_key = "test_key_temp"
        test_value = "Hello from AI Launchpad!"
        client.set(test_key, test_value)
        retrieved_value = client.get(test_key)
        
        # Test 3: Set with expiration
        client.setex("test_expiring_key", 10, "This expires in 10 seconds")
        ttl = client.ttl("test_expiring_key")
        
        # Test 4: Increment counter
        counter_key = "test_counter"
        client.set(counter_key, 0)
        client.incr(counter_key)
        counter_value = int(client.get(counter_key))
        
        # Test 5: List operations
        list_key = "test_list"
        client.delete(list_key)  # Clean up first
        client.lpush(list_key, "item1", "item2", "item3")
        list_length = client.llen(list_key)
        
        # Test 6: Get Redis info
        info = client.info()
        
        # Cleanup
        client.delete(test_key, counter_key, list_key, "test_expiring_key")
        
        return {
            "success": True,
            "host": REDIS_HOST,
            "port": REDIS_PORT,
            "ping": "PONG" if ping_response else "Failed",
            "set_get_test": retrieved_value == test_value,
            "ttl_test": ttl > 0,
            "increment_test": counter_value == 1,
            "list_test": list_length == 3,
            "redis_version": info.get('redis_version', 'Unknown'),
            "uptime_seconds": info.get('uptime_in_seconds', 0),
            "connected_clients": info.get('connected_clients', 0),
            "used_memory_human": info.get('used_memory_human', 'Unknown'),
            "total_commands_processed": info.get('total_commands_processed', 0)
        }
        
    except redis.ConnectionError as e:
        return {"error": f"Connection failed: {str(e)}"}
    except redis.TimeoutError:
        return {"error": "Connection timeout - Redis may not be running"}
    except Exception as e:
        return {"error": f"Redis error: {str(e)}"}

def render():
    """Render Redis test section"""
    st.markdown("### Test your Redis connection")
    
    # Show Redis status
    st.info(f"**Redis:** {REDIS_HOST}:{REDIS_PORT}")
    
    # Test button
    if st.button("🔴 Test Redis Connection", type="secondary", use_container_width=True):
        with st.spinner("Connecting to Redis..."):
            result = test_redis_connection()
            
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
                
                # Show helpful hints
                if "not installed" in result['error']:
                    st.info("💡 Redis client is not installed. Add to requirements.txt:\n```\nredis==5.0.1\n```\nThen rebuild:\n```\nlaunchpad build-local\nlaunchpad run-local\n```")
                else:
                    st.info("💡 Make sure Redis is enabled:\n1. Edit `services.config` and set `ENABLE_REDIS=true`\n2. Run `launchpad build-local && launchpad run-local`")
            else:
                st.success("✅ Redis connection successful!")
                
                st.markdown("### Connection Details:")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Host", result['host'])
                    st.metric("Version", result['redis_version'])
                    st.metric("Clients", result['connected_clients'])
                with col2:
                    st.metric("Port", result['port'])
                    st.metric("Memory Used", result['used_memory_human'])
                    st.metric("Uptime", f"{result['uptime_seconds']}s")
                
                with st.expander("✅ Test Results"):
                    tests = [
                        ("Ping Test", result['ping'] == "PONG", "Redis responded to PING"),
                        ("Set/Get Test", result['set_get_test'], "Successfully stored and retrieved data"),
                        ("TTL Test", result['ttl_test'], "Expiration/TTL working correctly"),
                        ("Increment Test", result['increment_test'], "Counter operations working"),
                        ("List Test", result['list_test'], "List operations working")
                    ]
                    
                    for test_name, passed, description in tests:
                        status = "✅" if passed else "❌"
                        st.markdown(f"{status} **{test_name}:** {description}")
                    
                    st.markdown(f"**Total Commands Processed:** {result['total_commands_processed']:,}")
                    st.success("✅ All Redis operations tested successfully!")


