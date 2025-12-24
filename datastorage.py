# data_storage.py

import json  # Used for reading and writing JSON files
import os    # Used for file system operations like path joining and directory creation

# Define where our data lives
DATA_DIR = "data"
# User data will be stored in a subdirectory called 'users'
USERS_DIR = os.path.join(DATA_DIR, "users")

# Paths to the static content files
LESSONS_FILE = os.path.join(DATA_DIR, "lessons.json")
CHALLENGES_FILE = os.path.join(DATA_DIR, "challenges.json")

def ensure_directories():
    """Make sure the folders we need exist so we don't get errors."""
    # exist_ok=True means it won't crash if the directory is already there
    os.makedirs(USERS_DIR, exist_ok=True)


def _read_json_file(path, default):
    """
    Reads data from a JSON file.
    If the file is missing or broken, it returns the 'default' value instead of crashing.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return the default value if something goes wrong
        return default


def _write_json_file(path, data):
    """Saves data to a JSON file with nice formatting."""
    with open(path, "w", encoding="utf-8") as f:
        # indent=2 makes the file human-readable
        json.dump(data, f, indent=2)


def load_lessons():
    """
    Reads all lessons and organizes them by their ID for easy lookup.
    """
    # Read the raw list of lessons from the file
    lessons_list = _read_json_file(LESSONS_FILE, default=[])
    lessons_by_id = {}

    # Convert the list into a dictionary: {lesson_id: lesson_data}
    for lesson in lessons_list:
        lesson_id = lesson.get("lesson_id")
        if lesson_id is not None:
            # JSON keys must be strings. 
            # We convert to string here to avoid FastAPI validation errors.
            lessons_by_id[str(lesson_id)] = lesson

    return lessons_by_id


def load_challenges():
    """
    Reads all challenges and organizes them by their ID for easy lookup.
    """
    # Read the raw list of challenges from the file
    challenges_list = _read_json_file(CHALLENGES_FILE, default=[])
    challenges_by_id = {}

    # Convert the list into a dictionary: {challenge_id: challenge_data}
    for challenge in challenges_list:
        challenge_id = challenge.get("challenge_id")
        if challenge_id is not None:
            # JSON keys must be strings.
            challenges_by_id[str(challenge_id)] = challenge

    return challenges_by_id


def load_user_progress(username):
    """
    Gets a user's progress. Creates a new profile if one doesn't exist.
    """
    ensure_directories()  # Make sure the users folder exists
    filename = os.path.join(USERS_DIR, f"{username}.json")

    # This is what a brand new user looks like
    default_progress = {
        "username": username,
        "age_range": "8-12",
        "current_lesson": 1,
        "lessons_completed": [],
        "challenges_completed": [],
        "badges_earned": [],
        "coins": 0
    }

    # Try to read the file
    data = _read_json_file(filename, default=None)

    if data is None:
        # If no file found, save and return the new user data
        _write_json_file(filename, default_progress)
        return default_progress

    return data


def save_user_progress(user_progress):
    """
    Updates the user's progress file with new data.
    """
    ensure_directories()
    username = user_progress.get("username", "unknown")
    filename = os.path.join(USERS_DIR, f"{username}.json")
    _write_json_file(filename, user_progress)

def load_user(uid):
    """
    Gets a user's master record.
    """
    ensure_directories()
    filename = os.path.join(USERS_DIR, f"{uid}.json")
    
    # Default structure with room for children
    default_user = {
        "uid": uid,
        "children": {}  # Dictionary of child profiles: {child_id: profile_data}
    }
    
    data = _read_json_file(filename, default=None)
    if data is None:
        _write_json_file(filename, default_user)
        return default_user
    return data

def get_child_profile(uid, child_id):
    """
    Gets a specific child's profile from the user's record.
    """
    user = load_user(uid)
    children = user.get("children", {})
    
    if child_id not in children:
        # Create a default profile if it doesn't exist
        children[child_id] = {
            "nickname": child_id,
            "ageRange": "8-12",
            "currentLesson": 1,
            "lessonsCompleted": [],
            "challengesCompleted": [],
            "badgesEarned": [],
            "coins": 0,
            "points": 0
        }
        _write_json_file(os.path.join(USERS_DIR, f"{uid}.json"), user)
        
    return children[child_id]

def update_child_profile(uid, child_id, update_data):
    """
    Updates a child's profile with new data.
    """
    user = load_user(uid)
    children = user.get("children", {})
    
    if child_id not in children:
        get_child_profile(uid, child_id) # Ensure it exists
        user = load_user(uid) # Reload
        children = user.get("children", {})

    # Update the profile
    children[child_id].update(update_data)
    _write_json_file(os.path.join(USERS_DIR, f"{uid}.json"), user)
    return children[child_id]

# The block below was for testing and can be removed or kept as reference
if __name__ == "__main__":
    print(load_user_progress("testuser"))
    save_user_progress({'username': 'testuser', 'age_range': '8-12', 'current_lesson': 1, 'lessons_completed': [1], 'challenges_completed': ["CH1"], 'badges_earned': [], 'coins': 0})

