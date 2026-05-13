from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile",temperature=0.4)

def generate_research(topic):

    prompt = f"""
    yoy are a viral short form content strategist.

    Topic:{topic}
    Generate:
    1. Viral hook
    2. Emotional trigger
    3. Retention strategy
    4. CTA
    """
    response = llm.invoke(prompt)
    return response.content
print(generate_research("use of AI in vibe coding"))