
def get_trend_researcher_prompt(niche: str, filtered_titles: list, feedback: str)-> str:
    """Returns the strict selection prompt for the Trend Researcher."""
    
    return f"""You are an expert '{niche}' content strategist. 

Your task is to analyze the following list of current trends and find the ONE best topic for a {niche} video.

TRENDING LIST:
{filtered_titles}

STRICT SELECTION RULES:
1. ONLY pick from the list if it is inherently and obviously related to {niche}.
2. If EVERY topic in the list is unrelated to {niche}, completely ignore the list. Instead, provide a popular, evergreen {niche} topic from your own knowledge.

{feedback}

CRITICAL FORMATTING RULES:
The 'topic' field is used directly in computer file paths. It MUST be 100% clean.
❌ BAD 'topic': "None from the list fit, so: Home Workouts"
❌ BAD 'topic': "I suggest High Intensity Interval Training"
❌ BAD 'topic': "none from trending list, so:",
❌ BAD 'topic': "none from the list, so:",
❌ BAD 'topic': "suggesting a new topic:",
❌ BAD 'topic': "none from trending list:",
❌ BAD 'topic': "not in list:",
✅ GOOD 'topic': "Home Workouts"
✅ GOOD 'topic': "High Intensity Interval Training"

OUTPUT FORMAT (JSON ONLY):
You must output a strictly valid JSON object. You must include a '_thought_process' key FIRST to explain your logic before outputting the final topic.

{{
  "_thought_process": "Step-by-step logic. e.g., 'I looked at the list. None of these relate to fitness. I will ignore the list and choose a popular fitness topic like Kettlebell workouts.'",
  "topic": "The clean, raw topic string ONLY (maximum 5 words).",
  "reason": "Briefly explain why this is a strong topic for the niche.",
  "source": "trending_list OR llm_knowledge"
}}"""