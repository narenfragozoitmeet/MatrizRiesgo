import asyncio
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend directory
backend_dir = Path(__file__).parent / "backend"
load_dotenv(backend_dir / '.env')

async def test_gemini():
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    print(f"API Key: {api_key[:20]}..." if api_key else "No API key found")
    
    if not api_key:
        return
    
    chat = LlmChat(
        api_key=api_key,
        session_id="test-session",
        system_message="You are a helpful assistant. Respond with valid JSON."
    )
    
    chat.with_model("gemini", "gemini-2.5-flash")
    
    user_message = UserMessage(
        text="Please respond with this exact JSON: {\"test\": \"success\", \"message\": \"Hello world\"}"
    )
    
    try:
        response = await chat.send_message(user_message)
        print(f"Raw response: {repr(response)}")
        print(f"Response type: {type(response)}")
        print(f"Response length: {len(response) if response else 0}")
        
        if response:
            print(f"First 100 chars: {response[:100]}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())