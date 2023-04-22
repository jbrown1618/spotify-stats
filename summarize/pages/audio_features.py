import pandas as pd

from utils.audio_features import top_and_bottom_lists

def make_audio_features_page(tracks: pd.DataFrame, description: str, relative_to: str):
    content = [
        f"# Audio Features for {description}"
        ""
    ] + top_and_bottom_lists(tracks)

    with open(relative_to, "w") as f:
        f.write("\n".join(content))

