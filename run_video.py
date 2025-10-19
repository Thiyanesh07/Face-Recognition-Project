
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


from ui.video_stream import run_video_stream

if __name__ == "__main__":
    print("=" * 60)
    print("Face Recognition System - Video Stream")
    print("=" * 60)
    run_video_stream()
