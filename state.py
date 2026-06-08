from typing import TypedDict

class ContentState(TypedDict):
    niche: str
    
    topic: str
    tend_reason: str
    reject_topic: bool
    topic_rejection_reason: str
    script: str
    hook: str
    audio_path: str
    human_approved: bool
    rejection_reason: str
    iteration_count: int

    
