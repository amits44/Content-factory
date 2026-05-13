from moviepy import VideoFileClip, AudioFileClip

def create_reel(video_path, audio_path):

    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    final_duration = min(video.duration, audio.duration)

    video = video.subclipped(0, final_duration)
    audio = audio.subclipped(0, final_duration)

    final = video.with_audio(audio)

    output_path = "outputs/final/final_reel.mp4"

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )

    return output_path