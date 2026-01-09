# Tracks containing these phrases (case-insensitive) will be excluded from processing
blacklisted_phrases = ["white noise", "loopable"]


def is_blacklisted(track_name: str) -> bool:
    """Check if a track name contains any blacklisted phrases."""
    track_name_lower = track_name.lower()
    return any(phrase in track_name_lower for phrase in blacklisted_phrases)
