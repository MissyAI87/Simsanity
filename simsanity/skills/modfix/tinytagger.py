import os
import shutil
import argparse
import json
import yaml
import re
from pathlib import Path

# Safeguard: Only allow moves/deletions within EA Sims 4 Mods folder
SAFE_ROOT_KEYWORDS = ["Electronic Arts", "The Sims 4"]

def is_within_ea_mods(path):
    """Ensure all file operations remain inside Electronic Arts/The Sims 4/Mods."""
    try:
        parts = [p.lower() for p in Path(path).parts]
        return any("electronic arts" in p or "the sims 4" in p for p in parts) and "mods" in parts
    except Exception:
        return False

# Supported file types (add or remove extensions here)
FILE_EXTENSIONS = ['.package', '.zip', '.rar', '.ts4script']

#
# Fallback tag rules if tag_config.yaml is missing
# Expanded with extra mod keywords and improved categorization
DEFAULT_TAGS = {
    # --- User-suggested keywords for improved SAC/Life mod classification ---
    "drama": "Gameplay",
    "secrets": "Gameplay",
    "dirty": "Gameplay",
    "life manager": "Utility",
    "vfx": "Visuals",
    "texture": "Visuals",
    "birds": "Visuals",
    "objects": "Gameplay",
    "mod": "Gameplay",
    # Makeup / Skin Details
    "eyes": "Makeup",
    "megaeyes": "Makeup",
    "lip gloss": "Makeup",
    "eye color": "Makeup",
    "lipcolour": "Makeup",
    "lips": "Makeup",
    "taraab": "Makeup",
    "myobi": "Makeup",

    # Clothing
    "bandeau": "Clothing",
    "teddy": "Clothing",
    "denim": "Clothing",
    "stockings": "Clothing",
    "thong": "Clothing",
    "birba32": "Clothing",
    "bkbottom": "Clothing",
    "sclub": "Clothing",
    "skysims": "Clothing",
    "qicc": "Clothing",

    # Hair and Makeup
    "ade": "Hair and Makeup",

    # Accessories
    "choker": "Accessories",
    "ps_": "Accessories",

    # Decor
    "cactus": "Decor",
    "flores": "Decor",
    "scent": "Decor",
    "bucket": "Decor",
    "scrolls": "Decor",

    # Furniture
    "locker": "Furniture",
    "chest": "Furniture",
    "shelves": "Furniture",
    "sixamcc": "Furniture",

    # Kitchen
    "brewing": "Kitchen",
    "beer": "Kitchen",
    "wine": "Kitchen",
    "drink": "Kitchen",
    "aroundthesims": "Kitchen",

    # Gameplay
    "strapon": "Gameplay",
    "cum": "Gameplay",
    "ww": "Gameplay",
    "azmodan22": "Gameplay",
    "basemental": "Gameplay",
    "venue": "Gameplay",
    "mc_cmd": "Gameplay",
    "mc_dresser": "Gameplay",
    "privatepractice": "Gameplay",
    "xmllnjector": "Gameplay",
    "lot51": "Gameplay",
    "weightreactions": "Gameplay",
    "wickedwhims": "Gameplay",
    "simrealist": "Gameplay",

    # BuildBuy
    "override": "BuildBuy",
    "allisas": "BuildBuy",

    # Decor (TSR)
    "tsr": "Decor",

    # Build Mode
    "max20": "Build Mode",
    "niche": "Build Mode",
    "brush": "Build Mode",
    "separator": "Build Mode",
    "steps": "Build Mode",

    # Outdoor
    "shrub": "Outdoor",
    "firepit": "Outdoor",
    "fountain": "Outdoor",
    "balcony": "Outdoor",
    "awning": "Outdoor",

    # Office
    "folders": "Office",
    "paperrolls": "Office",
    # Creator or Collection Tags (SAC is handled by functional keywords below)
    # "sac": "SAC Collection",  # Removed: handled by functional keywords below
    # --- SAC Sound Effects Keywords ---
    "impact": "Sound Effects",
    "reverb": "Sound Effects",
    "stomp": "Sound Effects",
    "crush": "Sound Effects",
    "swish": "Sound Effects",
    "explosion": "Sound Effects",
    "sound": "Sound Effects",
    "swoosh": "Sound Effects",
    "littlemssam": "LittleMsSam Mods",
    "lms": "LittleMsSam Mods",
    "kijiko": "Hair and Makeup",
    "platinumluxesims": "Makeup",
    "kotii": "Themes",
    # Creator-Specific or Collection-Based Tags
    "snowiii": "Makeup",
    "jomsims": "Furniture",
    "slox": "Clothing",
    "rustysims": "Furniture",
    "veranka": "Clothing",
    "serenity": "Clothing",
    "greenllamas": "Clothing",
    "madlen": "Clothing",
    "mssims": "Makeup",
    "nordica": "Decor",
    "onyx": "Hair and Makeup",
    "pralinesims": "Makeup",
    "phoenix": "Themes",
    "natali": "Skin Details",
    "sims4nexus": "Skin Details",

    # Build/Buy/Functional Decor
    "laundry": "Bathroom",
    "coffee maker": "Kitchen",
    "vacuum": "Storage",
    "alarm": "Electronics",
    "security": "Electronics",
    "garage": "Build Mode",
    "garden": "Outdoor",
    "balcony": "Outdoor",
    "awning": "Outdoor",
    "ceiling fan": "Lighting",
    "books": "Decor",

    # Creator prefixes or short tags
    "msqsims": "Clothing",
    "simcredible": "Furniture",
    "peacemaker": "Furniture",
    "sims4luxury": "Decor",
    "sabbath": "Occult",
    "nynaevedesign": "Furniture",
    "aroundthesims": "Kitchen",
    "tuds": "Themes",
    "qicc": "Clothing",
    "cosimetic": "Makeup",
    # Themes (added for theme mods)
    "theme": "Themes",
    "pastel": "Themes",
    "gothic": "Themes",
    "dark academia": "Themes",
    "aesthetic": "Themes",
    "grunge": "Themes",
    "boho": "Themes",
    "minimalist": "Themes",
    "cluttercore": "Themes",
    "retro": "Themes",
    "vintage": "Themes",
    "cyberpunk": "Themes",
    "steampunk": "Themes",
    "industrial": "Themes",
    "art deco": "Themes",
    "maximalist": "Themes",
    "kawaii": "Themes",
    "y2k": "Themes",
    "victorian": "Themes",
    "medieval": "Themes",
    "futuristic": "Themes",
    "farmhouse": "Themes",
    "shabby": "Themes",
    "scandinavian": "Themes",
    "coastal": "Themes",
    "cottage": "Themes",
    "eclectic": "Themes",
    "tropical": "Themes",
    # Furniture
    "couch": "Furniture", "sofa": "Furniture", "chair": "Furniture", "bed": "Furniture",
    "dresser": "Furniture", "table": "Furniture", "desk": "Furniture", "shelf": "Furniture",
    "bookshelf": "Furniture", "mirror": "Furniture", "lamp": "Furniture", "rug": "Furniture",
    "carpet": "Furniture", "wardrobe": "Furniture", "bench": "Furniture", "cabinet": "Furniture",
    "drawer": "Furniture", "stool": "Furniture", "closet": "Furniture",
    "bar": "Furniture",

    # --- Added for violence/extreme mods/screenshots ---
    "violence": "Gameplay",
    "extremeviolence": "Gameplay",
    "blood": "Gameplay",
    "injury": "Gameplay",
    "injuries": "Gameplay",
    "chainsaw": "Gameplay",
    "stomp": "Gameplay",
    "machete": "Gameplay",
    "mask": "CAS",
    "cas": "CAS",
    "camera": "Objects",
    "video": "Objects",
    "media": "Objects",
    "flame": "Gameplay",
    "thrower": "Gameplay",
    "cigarette": "Objects",
    "wild": "Gameplay",
    "tragedies": "Gameplay",
    "torments": "Gameplay",
    "soulsteal": "Gameplay",
    "explosion": "Gameplay",
    "serial": "Gameplay",
    "killer": "Gameplay",
    "murder": "Gameplay",
    "routingjig": "Routing",
    "routing": "Routing",
    "jig": "Routing",
    "intestines": "Gameplay",
    "flesh": "Gameplay",
    "puddle": "Gameplay",
    "pyromaniac": "CAS",
    "patrick": "Gameplay",
    "zanny": "Gameplay",
    "willard": "Gameplay",
    "kline": "Gameplay",

    # --- Added/Updated Keywords for Mods/Screenshots ---
    # Family & Household / Services / Household
    "nanny": "Services",
    "babysitter": "Services",
    "chores": "Household",
    "fosterfamily": "Household",
    "roommates": "Household",
    "unlockdoorforchosensims": "Household",
    # Pregnancy
    "miscarriage": "Pregnancy",
    "pregnancyoverhaul": "Pregnancy",
    "pregnancy": "Pregnancy",
    "ultrasoundscan": "Pregnancy",
    # Relationship/Romance
    "firstlove": "Romance",
    "dating": "Dating",
    "simdadatingapp": "Dating",
    "romanticmassage": "Romance",
    # Career/Business/Retail
    "liveinbusiness": "Business",
    "vetclinic": "Pets",
    "store": "Retail",
    "petdaycare": "Pets",
    # Venue
    "club": "VenueMods",
    "cafe": "VenueMods",
    "bar": "VenueMods",
    # School/Education
    "universityboard": "SchoolMods",
    "onlinelearningsystem": "SchoolMods",
    # Skills/Parenting
    "parentingskill": "Skills",
    # Gameplay
    "buffs": "GameplayTweaks",
    "lotchallenge": "LotChallenge",
    "aspirationgoals": "AspirationMods",
    "socialactivities": "Social",
    # Services
    "fooddelivery": "Services",
    "gardener": "Services",
    "maid": "Services",
    "ranchhand": "Services",
    # Script/Framework Mods & Adult
    "mccc": "MCCC",
    "mc_": "MCCC",
    "wickedwhims": "Adult",

    # Decor
    "plant": "Decor", "flower": "Decor", "vase": "Decor", "painting": "Decor", "poster": "Decor",
    "sculpture": "Decor", "art": "Decor", "frame": "Decor", "pillow": "Decor", "curtain": "Decor",
    "blind": "Decor", "clutter": "Decor", "deco": "Decor", "statue": "Decor", "tapestry": "Decor",
    "candle": "Decor", "bowl": "Decor", "tray": "Decor", "book": "Decor", "magazine": "Decor",
    "glass": "Decor", "jar": "Decor", "basket": "Decor", "box": "Decor",
    "succulent": "Decor",
    "hydrangea": "Decor",
    "gallery": "Decor",
    "post-it": "Decor",
    "sticky": "Decor",
    "note": "Decor",
    "jug": "Decor",
    "bamboo": "Decor",
    "scissors": "Decor",
    # Expanded Decor and Furniture
    "frame": "Decor",
    "painting": "Decor",
    "vignette": "Decor",
    "planter": "Decor",
    "pottery": "Decor",
    "sculpt": "Decor",
    "picture": "Decor",
    "canvas": "Decor",
    "plaque": "Decor",
    "mirror": "Decor",
    "books": "Decor",

    # Kitchen
    "sink": "Kitchen", "fridge": "Kitchen", "oven": "Kitchen", "stove": "Kitchen",
    "microwave": "Kitchen", "pan": "Kitchen", "pot": "Kitchen", "kettle": "Kitchen",
    "grill": "Kitchen", "mug": "Kitchen", "cup": "Kitchen", "plate": "Kitchen",
    "bottle": "Kitchen", "toaster": "Kitchen", "coffee": "Kitchen", "tea": "Kitchen",
    "spoon": "Kitchen", "fork": "Kitchen", "knife": "Kitchen", "dish": "Kitchen",
    "whisk": "Kitchen",
    "dispenser": "Kitchen",
    "nectar": "Kitchen",
    # Kitchen & Food
    "appliance": "Kitchen",
    "cutting board": "Kitchen",
    "cookware": "Kitchen",
    "baking": "Kitchen",
    "food": "Kitchen",
    "recipe": "Kitchen",
    "tray": "Kitchen",
    "ingredient": "Kitchen",
    "pantry": "Kitchen",
    "spice": "Kitchen",
    "utensil": "Kitchen",

    # Bathroom
    "tub": "Bathroom", "toilet": "Bathroom", "shower": "Bathroom", "mirror": "Bathroom",
    "soap": "Bathroom", "shampoo": "Bathroom", "towel": "Bathroom", "toothbrush": "Bathroom",
    "razor": "Bathroom", "lotion": "Bathroom", "sponge": "Bathroom", "loofah": "Bathroom",
    "mat": "Bathroom", "bath": "Bathroom",
    "body wash": "Bathroom",
    "wash": "Bathroom",
    # Bathroom Additions
    "toothpaste": "Bathroom",
    "shaving": "Bathroom",
    "toilet paper": "Bathroom",
    "plunger": "Bathroom",
    "bathmat": "Bathroom",

    # Clothing
    "shirt": "Clothing", "pants": "Clothing", "jeans": "Clothing", "dress": "Clothing",
    "skirt": "Clothing", "jacket": "Clothing", "sweater": "Clothing", "hoodie": "Clothing",
    "socks": "Clothing", "shoes": "Clothing", "heels": "Clothing", "boots": "Clothing",
    "sneakers": "Clothing", "sandals": "Clothing", "scarf": "Clothing", "hat": "Clothing",
    "gloves": "Clothing", "underwear": "Clothing", "bra": "Clothing", "lingerie": "Clothing",
    "swimsuit": "Clothing", "outfit": "Clothing", "robe": "Clothing",
    # Clothing (expanded)
    "tights": "Clothing",
    "yukata": "Clothing",

    # Hair and Makeup
    "hair": "Hair and Makeup", "hairstyle": "Hair and Makeup", "wig": "Hair and Makeup",
    "bun": "Hair and Makeup", "braid": "Hair and Makeup", "ponytail": "Hair and Makeup",
    "eyebrow": "Hair and Makeup", "eyeliner": "Hair and Makeup", "eyeshadow": "Hair and Makeup",
    "lipstick": "Hair and Makeup", "blush": "Hair and Makeup", "freckle": "Hair and Makeup",
    "makeup": "Hair and Makeup", "nail": "Hair and Makeup", "nails": "Hair and Makeup",
    "tattoo": "Hair and Makeup", "piercing": "Hair and Makeup", "beard": "Hair and Makeup",
    "mustache": "Hair and Makeup", "lashes": "Hair and Makeup",
    # Hair and Makeup (expanded)
    "eyelash": "Hair and Makeup",
    "lash": "Hair and Makeup",

    # Lighting
    "chandelier": "Lighting", "light": "Lighting", "lantern": "Lighting", "sconce": "Lighting",
    "ceiling": "Lighting", "floorlamp": "Lighting", "bulb": "Lighting", "spotlight": "Lighting",

    # Doors and Windows
    "door": "Doors and Windows", "window": "Doors and Windows", "arch": "Doors and Windows",
    "shutter": "Doors and Windows",

    # Electronics
    "tv": "Electronics", "computer": "Electronics", "monitor": "Electronics",
    "keyboard": "Electronics", "mouse": "Electronics", "speaker": "Electronics",
    "console": "Electronics", "phone": "Electronics", "tablet": "Electronics",
    "laptop": "Electronics", "screen": "Electronics", "headphones": "Electronics",
    "remote": "Electronics",

    # Toys and Kids
    "toy": "Toys and Kids", "doll": "Toys and Kids", "stuffed": "Toys and Kids",
    "crib": "Toys and Kids", "stroller": "Toys and Kids", "playpen": "Toys and Kids",
    "blocks": "Toys and Kids", "bear": "Toys and Kids", "kids": "Toys and Kids", "child": "Toys and Kids",
    "piggy": "Toys and Kids",

    # Pets
    "cat": "Pets", "dog": "Pets", "pet": "Pets", "bowl": "Pets", "bed": "Pets",
    "scratcher": "Pets", "litter": "Pets", "kennel": "Pets", "collar": "Pets",
    "leash": "Pets", "toy": "Pets",

    # Gameplay
    "trait": "Gameplay",
    "script": "Gameplay",
    "tuning": "Gameplay",
    "buff": "Gameplay",
    "interaction": "Gameplay",
    "event": "Gameplay",
    "autonomy": "Gameplay",
    "pregnancy": "Gameplay",
    "relationship": "Gameplay",
    "aspiration": "Gameplay",
    # Gameplay (expanded for mods like SimDa Dating App)
    "simda": "Gameplay",
    "dating": "Gameplay",
    "app": "Gameplay",
    "boardgame": "Gameplay",
    "game": "Gameplay",

    # Surfaces
    "counter": "Surfaces",
    "island": "Surfaces",
    "surface": "Surfaces",
    "coffee table": "Surfaces",
    "endtable": "Surfaces",
    "nightstand": "Surfaces",
    "console": "Surfaces",

    # Education
    "school": "Education",
    "homework": "Education",
    "teacher": "Education",
    "class": "Education",
    "university": "Education",
    "student": "Education",

    # Outdoor
    "fence": "Outdoor",
    "gate": "Outdoor",
    "tree": "Outdoor",
    "bush": "Outdoor",
    "rock": "Outdoor",
    "path": "Outdoor",
    "terrain": "Outdoor",
    "pond": "Outdoor",
    "grass": "Outdoor",
    "leaves": "Outdoor",

    # Bedroom
    "mattress": "Bedroom",
    "blanket": "Bedroom",
    "pillow": "Bedroom",
    "bedframe": "Bedroom",
    # Bedroom Additions
    "nightlight": "Bedroom",
    "canopy": "Bedroom",
    "headboard": "Bedroom",
    "dresser": "Bedroom",

    # Baby
    "bassinet": "Baby",
    "infant": "Baby",
    "diaper": "Baby",
    "bottle": "Baby",
    "pacifier": "Baby",

    # Build Mode
    "wallpaper": "Build Mode",
    "floor": "Build Mode",
    "roof": "Build Mode",
    "tile": "Build Mode",
    "foundation": "Build Mode",
    "column": "Build Mode",

    # Vehicles
    "car": "Vehicles",
    "truck": "Vehicles",
    "bike": "Vehicles",
    "motorcycle": "Vehicles",
    "vehicle": "Vehicles",
    "taxi": "Vehicles",
    "cab": "Vehicles",

    # Interface
    "ui": "Interface",
    "overlay": "Interface",
    "menu": "Interface",
    "hud": "Interface",
    "notification": "Interface",

    # CAS - Clothing
    "top": "Clothing",
    "shirt": "Clothing",
    "blouse": "Clothing",
    "tank": "Clothing",
    "sweater": "Clothing",
    "jacket": "Clothing",
    "hoodie": "Clothing",
    "dress": "Clothing",
    "skirt": "Clothing",
    "pants": "Clothing",
    "jeans": "Clothing",
    "shorts": "Clothing",
    "leggings": "Clothing",

    # CAS - Accessories
    "bracelet": "Accessories",
    "necklace": "Accessories",
    "earring": "Accessories",
    "glasses": "Accessories",
    "piercing": "Accessories",
    "ring": "Accessories",
    "purse": "Accessories",
    "bag": "Accessories",

    # CAS - Makeup & Skin
    "eyeliner": "Makeup",
    "lipstick": "Makeup",
    "blush": "Makeup",
    "eyeshadow": "Makeup",
    "freckle": "Skin Details",
    "scar": "Skin Details",
    "tattoo": "Skin Details",
    "skin": "Skin Details",
    "overlay": "Skin Details",
    "presets": "Skin Details",

    # Age-Specific Mods
    "toddler": "Kids",
    "child": "Kids",
    "teen": "Teens",
    "elder": "Elders",
    "kid": "Kids",

    # Build Buy
    "debug": "BuildBuy",
    "hidden": "BuildBuy",
    "buy": "BuildBuy",
    "catalog": "BuildBuy",
    "unlock": "BuildBuy",

    # Pets
    "dog": "Pets",
    "cat": "Pets",
    "pet": "Pets",
    "fur": "Pets",
    "tail": "Pets",
    "whisker": "Pets",

    # Occult
    "vampire": "Occult",
    "werewolf": "Occult",
    "spellcaster": "Occult",
    "mermaid": "Occult",
    "alien": "Occult",
    "witch": "Occult",
    "fairy": "Occult",
    "occult": "Occult",

    # Office / Study
    "computer": "Office",
    "keyboard": "Office",
    "laptop": "Office",
    "notebook": "Office",
    "pen": "Office",
    "calendar": "Office",
    "clipboard": "Office",

    # Hobby / Skill
    "art": "Hobbies",
    "easel": "Hobbies",
    "instrument": "Hobbies",
    "guitar": "Hobbies",
    "violin": "Hobbies",
    "keyboard (music)": "Hobbies",
    "piano": "Hobbies",
    "sketch": "Hobbies",
    "paint": "Hobbies",
    "journal": "Hobbies",

    # Events and Holidays
    "holiday": "Events",
    "christmas": "Events",
    "halloween": "Events",
    "easter": "Events",
    "birthday": "Events",
    "wedding": "Events",
    "party": "Events",

    # Storage and Utility
    "basket": "Storage",
    "hamper": "Storage",
    "shelf": "Storage",
    "rack": "Storage",
    "bin": "Storage",
    "crate": "Storage",
    "box": "Storage",
    "drawer": "Storage",

    # Misc Game Systems
    # --- ADDED ENTRIES FROM SCREENSHOTS ---
    # Decor / Furniture
    "dryer": "Appliances",
    "locker": "Furniture",
    "scent": "Decor",
    "bucket": "Decor",
    "scrolls": "Decor",
    "niche": "Build Mode",
    "brush": "Build Mode",
    "chest": "Furniture",
    "choker": "Accessories",
    "folders": "Office",
    "paperrolls": "Office",
    "shrub": "Outdoor",
    "separator": "Build Mode",
    "firepit": "Outdoor",
    "fountain": "Outdoor",
    "shelves": "Furniture",
    "steps": "Build Mode",
    "bandeau": "Clothing",
    "teddy": "Clothing",
    "denim": "Clothing",
    "stockings": "Clothing",
    "thong": "Clothing",
    "eye color": "Makeup",
    "lipcolour": "Makeup",
    "lips": "Makeup",

    # Gameplay or System
    "mc_cmd": "Gameplay",
    "mc_dresser": "Gameplay",
    "privatepractice": "Gameplay",
    "xmllnjector": "Gameplay",
    "lot51": "Gameplay",
    "weightreactions": "Gameplay",
    "simrealist": "Gameplay",
    "wickedwhims": "Gameplay",

    # Creators / Prefixes
    "calendar": "Gameplay",
    "journal": "Gameplay",
    "mod menu": "Interface",
    "menu": "Interface",
    "custom moodlet": "Gameplay",
    "moodlet": "Gameplay",
    "buff": "Gameplay",
    "social": "Gameplay",
    "career": "Gameplay",
    "job": "Gameplay",
    "aspiration": "Gameplay",
    "whim": "Gameplay"
}

UNCATEGORIZED = "Uncategorized"
TAG_FILE = "tag_config.yaml"
LOG_FILE = "tagdb.json"


def load_tags():
    """Load tags from tag_config.yaml or fallback to default tags."""
    if os.path.exists(TAG_FILE):
        with open(TAG_FILE, 'r') as f:
            return yaml.safe_load(f)
    return DEFAULT_TAGS


def tag_file(filepath, tags):
    """Match filepath (including folder names) to best tag category based on keyword presence."""
    # Remove any prefix like '[', '!', '(', underscores, spaces before creator names for better keyword matching
    base = os.path.basename(filepath)
    filename = base
    # More robust normalization for prefixes
    normalized_name = re.sub(r'^[\[\(!]*?(LittleMsSam|SAC)[\]_ -]*', '', filename, flags=re.IGNORECASE)
    lowered = normalized_name.lower()
    # Also check the full relative path (folder context), but normalize base name first for keyword matching
    lower_path = filepath.lower()
    matches = []
    for keyword, folder in tags.items():
        kw = keyword.lower()
        # Always use normalized_name for matching
        if kw in lowered:
            matches.append((kw, folder))
        # Optionally, also match keyword in the full path (for context), but use normalized_name for filename part
        elif kw in lower_path:
            matches.append((kw, folder))
    if not matches:
        print(f"No keyword match for: {normalized_name}")
        return UNCATEGORIZED
    # Prefer the longest keyword match (more specific)
    best_match = max(matches, key=lambda x: len(x[0]))
    return best_match[1]


def log_tag_action(path, category):
    """Append tagging action to tagdb.json"""
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                pass
    log.append({"file": path, "tag": category})
    with open(LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2)


def move_files(root_path, dry_run=False):
    """Walk through the mod folder and move files into categorized subfolders."""
    SKIP_FOLDERS = ['Unsorted', 'Clothing', 'Hair', 'Build-Bathroom', 'Build-Kitchen', 'Decor-Plants', 'Themes']
    tags = load_tags()
    moved, skipped, failed = 0, 0, 0
    created_folders = set()

    for dirpath, _, filenames in os.walk(root_path):
        if any(skip in dirpath for skip in SKIP_FOLDERS):
            continue
        for file in filenames:
            ext = os.path.splitext(file)[1].lower()
            if ext not in FILE_EXTENSIONS:
                skipped += 1
                continue

            source = os.path.join(dirpath, file)
            rel = os.path.relpath(source, root_path)

            # Normalize filename for keyword detection (remove creator prefixes, robust)
            normalized_name = re.sub(r'^[\[\(!]*?(LittleMsSam|SAC)[\]_ -]*', '', file, flags=re.IGNORECASE)
            normalized_name_lower = normalized_name.lower()
            file_lower = file.lower()

            # Don't process already sorted files
            if os.path.dirname(rel).capitalize() in tags.values():
                skipped += 1
                continue

            # --- Begin Special Handling for LittleMsSam and SAC mods ---
            # LittleMsSam mod keywords and logic
            lms_keywords = [
                "betternanny", "babysitter", "chores", "firstlove", "fooddelivery", "fosterfamily",
                "letfriendsageup", "liveinbusiness", "liveinservices", "miscarriage", "morebuyablevenues",
                "mypets", "onlinelearningsystem", "parentingskill", "pregnancyoverhaul", "roommates",
                "simdadatingapp", "socialactivities", "ultrasoundscan", "unlockdoorforchosensims"
            ]
            lms_base_ids = ["littlemssam_", "littlemssam"]
            sac_keywords = [
                # Removed: "sac_", "extremeviolence", "sim torments"
            ]
            # Check for LittleMsSam mod
            lms_matched = None
            for kw in lms_keywords:
                if kw in normalized_name_lower or kw in file_lower:
                    lms_matched = kw
                    break
            # Determine if the file is a LittleMsSam mod by prefix or keyword
            is_lms = False
            lms_folder = None
            for base in lms_base_ids:
                if file_lower.startswith(base):
                    is_lms = True
                    break
            if lms_matched:
                is_lms = True
            if is_lms:
                # Remove "LittleMsSam_" or "LittleMsSam" from start for folder name
                display_name = normalized_name
                # If one of the special keywords is found, use that as folder name (capitalize)
                if lms_matched:
                    pretty = lms_matched.replace("_", " ").replace("-", " ").title().replace(" ", "")
                    lms_folder = pretty
                else:
                    # Fallback: group under "LittleMsSam"
                    lms_folder = "LittleMsSam"
                # Ensure destination stays inside the Mods folder
                mods_root = None
                for part in Path(root_path).parents:
                    if part.name.lower() == "mods":
                        mods_root = part
                        break
                if not mods_root:
                    mods_root = Path(root_path)
                dest_folder = os.path.join(mods_root, lms_folder)
                if not os.path.exists(dest_folder):
                    if not dry_run:
                        try:
                            os.makedirs(dest_folder, exist_ok=True)
                        except Exception as e:
                            print(f"❌ Failed to create folder {dest_folder}: {e}")
                            failed += 1
                            continue
                dest = os.path.join(dest_folder, file)
                created_folders.add(dest_folder)
                msg = f"Placed '{file}' into '{lms_folder}'"
                if dry_run:
                    print(f"[Dry Run] {msg}")
                else:
                    try:
                        shutil.move(source, dest)
                        log_tag_action(dest, lms_folder)
                        print(msg)
                        moved += 1
                    except Exception as e:
                        print(f"❌ Failed to move {file}: {e}")
                        failed += 1
                continue  # Don't process further
            # --- End Special Handling for LittleMsSam mods ---

            # --- Remove SAC-specific auto-sorting ---
            # Any code that previously sorted by "sac" or "SAC" is now removed/commented out.

            # --- Begin New Keyword Dictionary and Case-Insensitive Sorting ---
            keywords = {
                "violence": [
                    "ExtremeViolence", "ArmedMurders", "RoutingJigs", "Chainsaw", "Blood",
                    "Injuries", "Stomp", "Hit", "Swish", "Sais", "Impact"
                ],
                "cas": [
                    "CAS Items", "CAS_", "Plastic Surgery", "Bandages", "Clothing"
                ],
                "drama": [
                    "Drama", "Dirty Secret", "Neighbours Dirty", "Secrets"
                ],
                "fire": [
                    "Flame Thrower", "Wild Fires", "Pyromaniac", "Explosion", "Puddle"
                ],
                "vfx": [
                    "VFX Textures", "Birds VFX"
                ],
                "healthcare": [
                    "First Aid", "Cure Needle", "Confusion Mist", "Infection Needle"
                ],
                "weapons": [
                    "Handgun", "M4", "Assault Rifle", "Shotgun", "Bullets", "Shells"
                ],
                "zombie": [
                    "Zombie", "Repellent Spray", "HQ Zombie Repellent", "Apocalypse", "Survival Items"
                ],
                "radio": [
                    "Radio", "News Media Video Camera"
                ],
                "sound": [
                    "vo_warcry", "Sounds", "Reverb", "Scream"
                ],
                "life_sim": [
                    "Life Manager", "Sim Torments", "Life Tragedies", "Zanny", "Willard Kline", "Patrick Rogers"
                ]
            }

            # Case-insensitive matching for new keyword dictionary
            keyword_category = None
            for category, wordlist in keywords.items():
                for kw in wordlist:
                    if kw.lower() in normalized_name_lower or kw.lower() in file_lower:
                        keyword_category = category
                        break
                if keyword_category:
                    break

            if keyword_category:
                category = keyword_category
                print(f"Matched: {normalized_name} → {category}")
            else:
                # Fallback to legacy tags logic if not matched
                matches = []
                for keyword, folder_name in tags.items():
                    kw = keyword.lower()
                    if kw in normalized_name_lower:
                        matches.append((kw, folder_name))
                    elif kw in file_lower:
                        matches.append((kw, folder_name))
                if not matches:
                    category = UNCATEGORIZED
                else:
                    # Prefer the longest keyword match (most specific)
                    best_match = max(matches, key=lambda x: len(x[0]))
                    print(f"Matched: {normalized_name} → {best_match[1]}")
                    category = best_match[1]

            # Ensure destination stays inside the Mods folder
            mods_root = None
            for part in Path(root_path).parents:
                if part.name.lower() == "mods":
                    mods_root = part
                    break
            if not mods_root:
                mods_root = Path(root_path)
            dest_folder = os.path.join(mods_root, category)

            # Skip creating folder if it exists and is empty, to avoid duplicates
            if os.path.exists(dest_folder):
                if not os.listdir(dest_folder):
                    continue  # Skip creating or duplicating empty folders
            else:
                if not dry_run:
                    try:
                        os.makedirs(dest_folder, exist_ok=True)
                    except Exception as e:
                        print(f"❌ Failed to create folder {dest_folder}: {e}")
                        failed += 1
                        continue

            dest = os.path.join(dest_folder, file)
            created_folders.add(dest_folder)

            if dry_run:
                print(f"[Dry Run] Would move: {file} → {category}/")
            else:
                # SAFEGUARD: Only allow moves within EA Sims 4 Mods folder
                if not is_within_ea_mods(source) or not is_within_ea_mods(dest):
                    print(f"🚫 [SAFEGUARD] Skipping unsafe move outside EA Mods: {source} → {dest}")
                    continue
                try:
                    shutil.move(source, dest)
                    log_tag_action(dest, category)
                    print(f"Moved: {file} → {category}/")
                    moved += 1
                except Exception as e:
                    print(f"❌ Failed to move {file}: {e}")
                    failed += 1

    # Cleanup pass: remove any empty folders left behind
    for dirpath, dirnames, _ in os.walk(root_path, topdown=False):
        for dirname in dirnames:
            folder_path = os.path.join(dirpath, dirname)
            if os.path.exists(folder_path) and not os.listdir(folder_path):
                # SAFEGUARD: Only allow removals within EA Sims 4 Mods folder
                if not is_within_ea_mods(folder_path):
                    print(f"🚫 [SAFEGUARD] Skipping deletion outside EA Mods folder: {folder_path}")
                    continue
                try:
                    os.rmdir(folder_path)
                    print(f"🗑️ Removed empty folder: {folder_path}")
                except Exception as e:
                    print(f"❌ Failed to remove empty folder {folder_path}: {e}")

    print(f"\n✅ Done. {moved} moved | {skipped} skipped | {failed} failed.")
    if dry_run and created_folders:
        print("\n📁 Folders that would be created:")
        for folder in sorted(created_folders):
            print(f"  - {os.path.basename(folder)}")


if __name__ == "__main__":
    # Command-line interface and dry-run support
    parser = argparse.ArgumentParser(description="🧹 Tiny Tagger - Sort and tag your mod files.")
    parser.add_argument("folder", help="Path to your Mods folder")
    parser.add_argument("--dry-run", action="store_true", help="Preview file moves without making changes")
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print("❌ That folder doesn't exist. Try again.")
    else:
        move_files(args.folder, dry_run=args.dry_run)
