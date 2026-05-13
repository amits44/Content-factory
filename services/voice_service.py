from gtts import gTTS
from pathlib import Path

def generate_voice(script):

    output_dir = Path("outputs/audio")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "voice.mp3"

    tts = gTTS(
        text=script,
        lang="en"
    )

    tts.save(str(output_path))

    return str(output_path)