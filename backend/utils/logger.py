import os


def add_debug_logs(*args, **kwargs):
    if os.getenv("DEBUG", "").lower() == "true":   
        print("=" * 30)
        print(*args, **kwargs)
        print("=" * 30)