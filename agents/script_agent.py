from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile",temperature=0.4)

def generate_script(topic):
    prompt = f"""
    Create a 30-60 second Instagram reel script.

    Topic: {topic}

    Requirements:
    - strong first 5 seconds
    - short punchy sentences
    - scene-by-scene narration
    - cinematic pacing
    """
    response = llm.invoke(prompt)
    return response.content