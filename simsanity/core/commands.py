

# core/commands.py
import difflib

# This list is intended to be used only for the first "what socials" request,
# and will be replaced or expanded later for other requests.
VALID_COMMANDS = [
    "twitter",
    "instagram",
    "facebook",
    "linkedin",
    "tiktok",
    "youtube",
    "snapchat",
]

def normalize_command(text):
    """Normalize user input for matching."""
    return text.strip().lower()

def match_command(user_input, valid_commands=VALID_COMMANDS, cutoff=0.7):
    """
    Attempt to match user input to a valid command.
    Returns the matched command or None if no good match.
    """
    norm_input = normalize_command(user_input)
    # Exact match first
    if norm_input in valid_commands:
        return norm_input
    # Fuzzy match using difflib
    matches = difflib.get_close_matches(norm_input, valid_commands, n=1, cutoff=cutoff)
    if matches:
        return matches[0]
    return None
