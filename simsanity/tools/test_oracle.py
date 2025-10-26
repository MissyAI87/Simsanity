"""
Test suite for oracle pizza skills
"""

from support.map_route import import_from_route

execute = import_from_route("core/controller.py").execute

def run_tests():
    print("\n=== Content Generator ===")
    print(execute("content_generator: New AI launch post for LinkedIn"))

    print("\n=== Platform Adapter ===")
    print(execute("platform_adapter: Check out our new AI tool!"))

    print("\n=== Hashtag Finder ===")
    print(execute("hashtag_finder: Launching an AI marketing startup tool"))

    print("\n=== Schedule Planner ===")
    print(execute("schedule_planner: Campaign kickoff for TikTok"))

    print("\n=== Engagement Analyzer ===")
    comments = [
        "Love this feature!",
        "Terrible UI, I hate it.",
        "Awesome idea, very helpful."
    ]
    metrics = {"likes": 120, "comments": 15, "shares": 5, "views": 2000}
    # Pass as string for now, since controller splits input at colon
    test_input = f"engagement_analyzer: {comments} | {metrics}"
    print(execute(test_input))

    print("\n=== Report Builder ===")
    sample_data = [
        {"platform": "Twitter", "likes": 120, "comments": 15, "shares": 10, "views": 1000},
        {"platform": "TikTok", "likes": 400, "comments": 50, "shares": 100, "views": 5000},
    ]
    print(execute(f"report_builder: {sample_data}"))

if __name__ == "__main__":
    run_tests()
