import os
from dotenv import load_dotenv

from agents.research_agent import generate_research
from agents.script_agent import generate_script
from services.voice_service import generate_voice
from services.pexels import fetch_video
from services.video_editor import create_reel

load_dotenv()

TOPIC = "AI is replacing marketers"

print("\nGenerating research...")

research = generate_research(TOPIC)

print("\nGenerating script...")

script = generate_script(TOPIC)

print("\nSCRIPT:\n")
print(script)

print("\nGenerating voice...")
audio_path = generate_voice(script)

print("\nFetching stock video...")
video_path = fetch_video("artificial intelligence")

print("\nCreating reel...")
final_path = create_reel(video_path, audio_path)

print(f"\nDone! Reel saved to: {final_path}")