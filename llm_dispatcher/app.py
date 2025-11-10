from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from functools import wraps
from typing import Dict, List, Any, Optional
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_API_ENDPOINT = os.getenv('LLM_API_ENDPOINT')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
OLLAMA_HOST = os.getenv('LLM_HOST', 'llm')
OLLAMA_PORT = int(os.getenv('LLM_PORT', '11434'))
OLLAMA_MODEL = os.getenv('LLM_MODEL', 'gemma3n:e2b')
VLLM_HOST = os.getenv('VLLM_HOST', 'llm-vllm')
VLLM_PORT = int(os.getenv('VLLM_PORT', '8000'))
VLLM_MODEL = os.getenv('VLLM_MODEL', 'facebook/opt-125m')

# Conditional imports based on LLM_PROVIDER
if LLM_PROVIDER == 'openai':
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=LLM_API_KEY)
        logger.info("OpenAI client initialized")
    except ImportError:
        logger.error("OpenAI package not installed but LLM_PROVIDER is 'openai'")
        openai_client = None
elif LLM_PROVIDER == 'anthropic':
    try:
        import anthropic
        anthropic_client = anthropic.Anthropic(api_key=LLM_API_KEY)
        logger.info("Anthropic client initialized")
    except ImportError:
        logger.error("Anthropic package not installed but LLM_PROVIDER is 'anthropic'")
        anthropic_client = None

def query_openai(prompt: str, model: str = None) -> Dict[str, Any]:
    """Send a query to OpenAI"""
    if not openai_client:
        return {"error": "OpenAI client not available"}
    
    try:
        response = openai_client.chat.completions.create(
            model=model or LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": response.model,
            "total_tokens": response.usage.total_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens
        }
    except Exception as e:
        return {"error": f"Failed to query OpenAI: {str(e)}"}

def query_anthropic(prompt: str, model: str = None) -> Dict[str, Any]:
    """Send a query to Anthropic"""
    if not anthropic_client:
        return {"error": "Anthropic client not available"}
    
    try:
        response = anthropic_client.messages.create(
            model=model or LLM_MODEL or "claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "response": response.content[0].text,
            "model": response.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    except Exception as e:
        return {"error": f"Failed to query Anthropic: {str(e)}"}

def query_ollama(prompt: str, model: str = None, stream: bool = False) -> Dict[str, Any]:
    """Send a query to Ollama"""
    url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
    
    payload = {
        "model": model or OLLAMA_MODEL,
        "prompt": prompt,
        "stream": stream
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Ollama returned status {response.status_code}: {response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "Request to Ollama timed out"}
    except Exception as e:
        return {"error": f"Failed to query Ollama: {str(e)}"}

def query_vllm(prompt: str, model: str = None) -> Dict[str, Any]:
    """Send a query to vLLM using OpenAI-compatible API"""
    url = f"http://{VLLM_HOST}:{VLLM_PORT}/v1/completions"
    
    payload = {
        "model": model or VLLM_MODEL,
        "prompt": prompt,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return {
                "response": data['choices'][0]['text'],
                "model": data.get('model', model or VLLM_MODEL),
                "usage": data.get('usage', {}),
                "finish_reason": data['choices'][0].get('finish_reason', 'stop')
            }
        else:
            return {"error": f"vLLM returned status {response.status_code}: {response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "Request to vLLM timed out"}
    except Exception as e:
        return {"error": f"Failed to query vLLM: {str(e)}"}

def query_llm_provider(prompt: str, model: str = None) -> Dict[str, Any]:
    """Route query to appropriate LLM provider"""
    if LLM_PROVIDER == 'openai':
        return query_openai(prompt, model)
    elif LLM_PROVIDER == 'anthropic':
        return query_anthropic(prompt, model)
    elif LLM_PROVIDER == 'ollama':
        return query_ollama(prompt, model)
    elif LLM_PROVIDER == 'vllm':
        return query_vllm(prompt, model)
    elif LLM_PROVIDER == 'local':
        # Backward compatibility - default to ollama
        return query_ollama(prompt, model)
    else:
        return {"error": f"Unsupported LLM provider: {LLM_PROVIDER}"}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "llm_provider": LLM_PROVIDER,
        "services": {
            "api": "up",
            "llm": "unknown"
        }
    }
    
    # Check LLM service based on provider
    if LLM_PROVIDER in ['ollama', 'local']:
        try:
            response = requests.get(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags", timeout=2)
            health_status["services"]["llm"] = "up" if response.status_code == 200 else "down"
        except:
            health_status["services"]["llm"] = "down"
    elif LLM_PROVIDER == 'vllm':
        try:
            response = requests.get(f"http://{VLLM_HOST}:{VLLM_PORT}/v1/models", timeout=2)
            health_status["services"]["llm"] = "up" if response.status_code == 200 else "down"
        except:
            health_status["services"]["llm"] = "down"
    elif LLM_PROVIDER in ['openai', 'anthropic']:
        # For external providers, we'll mark as up if we have an API key
        health_status["services"]["llm"] = "up" if LLM_API_KEY else "down"
    
    # Overall status
    if any(status == "down" for status in health_status["services"].values()):
        health_status["status"] = "degraded"
    
    return jsonify(health_status)


@app.route('/query', methods=['POST'])
def query_llm():
    """Direct query to LLM endpoint"""
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Missing prompt in request body'}), 400
    
    prompt = data['prompt']
    model = data.get('model')

    logger.info(f"Querying {LLM_PROVIDER} LLM with prompt: {prompt[:100]}...")
    
    result = query_llm_provider(prompt, model)
    
    if 'error' in result:
        return jsonify(result), 500
    
    # Standardize response format
    response_data = {
        'response': result.get('response', ''),
        'provider': LLM_PROVIDER,
        'model': result.get('model', model or 'unknown')
    }
    
    # Add provider-specific metrics
    if LLM_PROVIDER in ['ollama', 'local']:
        response_data.update({
            'total_duration': result.get('total_duration', 0),
            'load_duration': result.get('load_duration', 0),
            'prompt_eval_duration': result.get('prompt_eval_duration', 0),
            'eval_duration': result.get('eval_duration', 0),
            'eval_count': result.get('eval_count', 0)
        })
    elif LLM_PROVIDER == 'vllm':
        usage = result.get('usage', {})
        response_data.update({
            'total_tokens': usage.get('total_tokens', 0),
            'prompt_tokens': usage.get('prompt_tokens', 0),
            'completion_tokens': usage.get('completion_tokens', 0),
            'finish_reason': result.get('finish_reason', 'stop')
        })
    elif LLM_PROVIDER == 'openai':
        response_data.update({
            'total_tokens': result.get('total_tokens', 0),
            'prompt_tokens': result.get('prompt_tokens', 0),
            'completion_tokens': result.get('completion_tokens', 0)
        })
    elif LLM_PROVIDER == 'anthropic':
        response_data.update({
            'input_tokens': result.get('input_tokens', 0),
            'output_tokens': result.get('output_tokens', 0)
        })
    
    return jsonify(response_data)

@app.route('/models', methods=['GET'])
def list_models():
    """List available models based on LLM provider"""
    if LLM_PROVIDER in ['ollama', 'local']:
        try:
            response = requests.get(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return jsonify({
                    'provider': 'ollama',
                    'models': [
                        {
                            'name': model['name'],
                            'size': model['size'],
                            'modified': model['modified_at']
                        }
                        for model in data.get('models', [])
                    ],
                    'default_model': OLLAMA_MODEL
                })
            else:
                return jsonify({'error': 'Failed to fetch models from Ollama'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to list models: {str(e)}'}), 500
    
    elif LLM_PROVIDER == 'vllm':
        try:
            response = requests.get(f"http://{VLLM_HOST}:{VLLM_PORT}/v1/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return jsonify({
                    'provider': 'vllm',
                    'models': [
                        {
                            'name': model['id'],
                            'created': model.get('created', 0)
                        }
                        for model in data.get('data', [])
                    ],
                    'default_model': VLLM_MODEL
                })
            else:
                return jsonify({'error': 'Failed to fetch models from vLLM'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to list models: {str(e)}'}), 500
    
    elif LLM_PROVIDER == 'openai':
        return jsonify({
            'provider': 'openai',
            'models': [
                {'name': 'gpt-4', 'description': 'Most capable GPT-4 model'},
                {'name': 'gpt-4-turbo', 'description': 'GPT-4 Turbo with 128k context'},
                {'name': 'gpt-3.5-turbo', 'description': 'Fast and affordable model'}
            ],
            'default_model': LLM_MODEL
        })
    
    elif LLM_PROVIDER == 'anthropic':
        return jsonify({
            'provider': 'anthropic',
            'models': [
                {'name': 'claude-3-opus-20240229', 'description': 'Most powerful Claude model'},
                {'name': 'claude-3-sonnet-20240229', 'description': 'Balanced performance and speed'},
                {'name': 'claude-3-haiku-20240307', 'description': 'Fastest Claude model'}
            ],
            'default_model': LLM_MODEL or 'claude-3-sonnet-20240229'
        })
    
    else:
        return jsonify({'error': f'Unsupported LLM provider: {LLM_PROVIDER}'}), 500


@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'name': 'LLM Dispatcher',
        'version': '1.0',
        'provider': LLM_PROVIDER,
        'endpoints': {
            '/health': 'GET - Health check',
            '/query': 'POST - Direct LLM query',
            '/models': 'GET - List available LLM models'
        },
        'documentation': {
            'query': {
                'method': 'POST',
                'body': {
                    'prompt': 'Your question here',
                    'model': f'model name (optional, defaults to {LLM_MODEL if LLM_PROVIDER not in ["local", "ollama", "vllm"] else (VLLM_MODEL if LLM_PROVIDER == "vllm" else OLLAMA_MODEL)})'
                }
            }
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)