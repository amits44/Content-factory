import requests
import os
from pathlib import Path

API_KEY = os.getenv("PEXELS_API_KEY")

def fetch_video(query):

    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"

    headers = {
        "Authorization": API_KEY
    }

    response = requests.get(url, headers=headers)

    data = response.json()

    video_url = data["videos"][0]["video_files"][0]["link"]

    save_path = Path("outputs/clips/clip.mp4")

    video_data = requests.get(video_url)

    with open(save_path, "wb") as f:
        f.write(video_data.content)

    return str(save_path)