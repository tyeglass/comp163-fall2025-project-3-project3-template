"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Implementation

Name: Tye Glass
AI Usage: AI tools were used to support approximately 60% of the code implementation and documentation comments. AI assistance also guided me 
through parts of the version-control process, including making commits to GitHub. All final code was reviewed, tested, and approved by me.”
"""

import os

from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)


# ====================================================================
# DATA LOADING FUNCTIONS
# ====================================================================

def load_quests(filename="data/quests.txt"):
    """
    Load all quest entries from a text file.

    Returns:
        dict: A dictionary mapping quest_id → quest_data_dict
    Raises:
        MissingDataFileError: If the file does not exist.
        InvalidDataFormatError: If formatting inside the file is invalid.
        CorruptedDataError: If the file cannot be read correctly.
    """
    # Ensure file exists before attempting to read
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quest data file not found: {filename}")

    # Safely read the file while catching read errors
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as exc:
        raise CorruptedDataError(f"Could not read quest file: {exc}")

    # Split file into blocks separated by blank lines
    blocks = []
    current = []
    for line in content.splitlines():
        line_stripped = line.strip()
        if line_stripped == "":
            # End of block → save it
            if current:
                blocks.append(current)
                current = []
        else:
            # Keep original formatting for parsing
            current.append(line)
    # Add final block if not followed by blank line
    if current:
        blocks.append(current)

    quests = {}
    # Parse each block into a quest dictionary
    for block in blocks:
        try:
            q = parse_quest_block(block)
        except InvalidDataFormatError:
            raise
        except Exception as exc:
            # Wrap unknown errors as format errors for consistency
            raise InvalidDataFormatError(f"Error parsing quest block: {exc}")

        qid = q.get("quest_id")

        # All quests must have a unique quest_id
        if not qid:
            raise InvalidDataFormatError("Quest block missing quest_id")
        if qid in quests:
            raise InvalidDataFormatError(f"Duplicate quest_id found: {qid}")

        quests[qid] = q

    # Validate each quest to ensure required fields exist and are typed correctly
    for q in quests.values():
        validate_quest_data(q)

    return quests


def load_items(filename="data/items.txt"):
    """
    Load all item entries from a text file.

    Returns:
        dict: A dictionary mapping item_id → item_data_dict
    Raises:
        MissingDataFileError: If the file is missing.
        InvalidDataFormatError: If any item section is malformed.
        CorruptedDataError: If file cannot be opened or read.
    """
    # Ensure the file exists
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item data file not found: {filename}")

    # Attempt to read file
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as exc:
        raise CorruptedDataError(f"Could not read item file: {exc}")

    # Break file into blocks separated by blank lines
    blocks = []
    current = []
    for line in content.splitlines():
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    items = {}
    # Parse each item block
    for block in blocks:
        try:
            it = parse_item_block(block)
        except InvalidDataFormatError:
            raise
        except Exception as exc:
            raise InvalidDataFormatError(f"Error parsing item block: {exc}")

        iid = it.get("item_id")

        # All items must have unique IDs
        if not iid:
            raise InvalidDataFormatError("Item block missing item_id")
        if iid in items:
            raise InvalidDataFormatError(f"Duplicate item_id found: {iid}")

        items[iid] = it

    # Validate items after parsing
    for it in items.values():
        validate_item_data(it)

    return items


# ====================================================================
# VALIDATION
# ====================================================================

def validate_quest_data(quest_dict):
    """
    Ensure a quest dictionary contains all required fields and correct data types.

    Raises:
        InvalidDataFormatError: If any required field is missing or typed incorrectly.
    """
    required = {
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite"
    }

    # Check for missing fields
    if not required.issubset(set(quest_dict.keys())):
        missing = required - set(quest_dict.keys())
        raise InvalidDataFormatError(
            f"Quest missing required fields: {', '.join(sorted(missing))}"
        )

    # Validate integer fields
    for key in ("reward_xp", "reward_gold", "required_level"):
        val = quest_dict.get(key)
        if not isinstance(val, int):
            raise InvalidDataFormatError(f"Quest field {key} must be integer")

    # Prerequisite must be a string (e.g., quest id or "NONE")
    prereq = quest_dict.get("prerequisite")
    if not isinstance(prereq, str):
        raise InvalidDataFormatError("Quest prerequisite must be a string")

    return True


def validate_item_data(item_dict):
    """
    Ensure an item dictionary contains all required fields and proper types.

    Raises:
        InvalidDataFormatError: If required fields are missing or invalid.
    """
    required = {"item_id", "name", "type", "effect", "cost", "description"}

    # Check for missing required keys
    if not required.issubset(set(item_dict.keys())):
        missing = required - set(item_dict.keys())
        raise InvalidDataFormatError(
            f"Item missing required fields: {', '.join(sorted(missing))}"
        )

    # Validate item type category
    if item_dict["type"] not in {"weapon", "armor", "consumable"}:
        raise InvalidDataFormatError(f"Invalid item type: {item_dict['type']}")

    # Cost must be an integer
    if not isinstance(item_dict["cost"], int):
        raise InvalidDataFormatError("Item cost must be integer")

    # Effect must be a string like "health:20" (or empty)
    if not isinstance(item_dict["effect"], str):
        raise InvalidDataFormatError("Item effect must be a string")

    return True


# ====================================================================
# DEFAULT FILE CREATION
# ====================================================================

def create_default_data_files():
    """
    Automatically generate default quest and item text files if missing.
    This ensures the game can run at least minimal content.
    """
    os.makedirs("data", exist_ok=True)

    quests_path = os.path.join("data", "quests.txt")
    items_path = os.path.join("data", "items.txt")

    # Create a sample quests file if none exists
    if not os.path.exists(quests_path):
        default_quests = [
            "QUEST_ID: first_quest",
            "TITLE: First Steps",
            "DESCRIPTION: Complete your first task.",
            "REWARD_XP: 50",
            "REWARD_GOLD: 25",
            "REQUIRED_LEVEL: 1",
            "PREREQUISITE: NONE",
            "",
            "QUEST_ID: second_quest",
            "TITLE: Second Trial",
            "DESCRIPTION: Requires finishing first quest.",
            "REWARD_XP: 75",
            "REWARD_GOLD: 40",
            "REQUIRED_LEVEL: 2",
            "PREREQUISITE: first_quest",
            "",
        ]
        # Write the file in text format
        with open(quests_path, "w", encoding="utf-8") as f:
            f.write("\n".join(default_quests) + "\n")

    # Create a sample items file if missing
    if not os.path.exists(items_path):
        default_items = [
            "ITEM_ID: health_potion",
            "NAME: Health Potion",
            "TYPE: consumable",
            "EFFECT: health:20",
            "COST: 10",
            "DESCRIPTION: Restores 20 health",
            "",
            "ITEM_ID: iron_sword",
            "NAME: Iron Sword",
            "TYPE: weapon",
            "EFFECT: strength:5",
            "COST: 50",
            "DESCRIPTION: Basic iron sword",
            "",
            "ITEM_ID: leather_armor",
            "NAME: Leather Armor",
            "TYPE: armor",
            "EFFECT: max_health:10",
            "COST: 40",
            "DESCRIPTION: Light protective armor",
            "",
        ]
        with open(items_path, "w", encoding="utf-8") as f:
            f.write("\n".join(default_items) + "\n")


# ====================================================================
# PARSING HELPERS
# ====================================================================

def parse_quest_block(lines):
    """
    Convert a block of quest lines into a structured dictionary.

    Raises:
        InvalidDataFormatError: If a line is missing a ':' separator or contains bad data.
    """
    data = {}
    for raw in lines:
        # Ensure the line follows "KEY: value" format
        if ":" not in raw:
            raise InvalidDataFormatError("Invalid quest line (missing ':'): " + raw)

        key, val = raw.split(":", 1)
        key = key.strip().upper()
        val = val.strip()

        # Map each field to internal dictionary keys
        if key == "QUEST_ID":
            data["quest_id"] = val
        elif key == "TITLE":
            data["title"] = val
        elif key == "DESCRIPTION":
            data["description"] = val
        elif key == "REWARD_XP":
            try:
                data["reward_xp"] = int(val)
            except Exception:
                raise InvalidDataFormatError("Invalid REWARD_XP value")
        elif key == "REWARD_GOLD":
            try:
                data["reward_gold"] = int(val)
            except Exception:
                raise InvalidDataFormatError("Invalid REWARD_GOLD value")
        elif key == "REQUIRED_LEVEL":
            try:
                data["required_level"] = int(val)
            except Exception:
                raise InvalidDataFormatError("Invalid REQUIRED_LEVEL value")
        elif key == "PREREQUISITE":
            data["prerequisite"] = val
        else:
            # Unknown values are stored but ignored by validators
            data[key.lower()] = val

    # Default prerequisite if not defined
    data.setdefault("prerequisite", "NONE")

    # Ensure required textual fields exist
    if "quest_id" not in data or "title" not in data or "description" not in data:
        raise InvalidDataFormatError("Quest block missing required textual fields")

    # Ensure numeric values exist (defaulting if missing)
    for num_field in ("reward_xp", "reward_gold", "required_level"):
        if num_field not in data:
            if num_field == "required_level":
                data[num_field] = 1
            else:
                data[num_field] = 0

    return data


def parse_item_block(lines):
    """
    Convert a block of item text into a structured dictionary.

    Raises:
        InvalidDataFormatError: If formatting is wrong or required values are missing.
    """
    data = {}
    for raw in lines:
        # Must contain "KEY: value"
        if ":" not in raw:
            raise InvalidDataFormatError("Invalid item line (missing ':'): " + raw)

        key, val = raw.split(":", 1)
        key = key.strip().upper()
        val = val.strip()

        # Assign fields
        if key == "ITEM_ID":
            data["item_id"] = val
        elif key == "NAME":
            data["name"] = val
        elif key == "TYPE":
            data["type"] = val.lower()
        elif key == "EFFECT":
            data["effect"] = val
        elif key == "COST":
            try:
                data["cost"] = int(val)
            except Exception:
                raise InvalidDataFormatError("Invalid COST value")
        elif key == "DESCRIPTION":
            data["description"] = val
        else:
            data[key.lower()] = val

    # Minimal required fields check
    if "item_id" not in data or "name" not in data or "type" not in data:
        raise InvalidDataFormatError("Item block missing required fields")

    # Provide default values for optional fields
    data.setdefault("effect", "")
    data.setdefault("cost", 0)
    data.setdefault("description", "")

    return data


# ====================================================================
# TESTING
# ====================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    try:
        # Ensure sample files exist
        create_default_data_files()

        # Attempt to load both quests and items
        quests = load_quests()
        items = load_items()

        print(f"Loaded {len(quests)} quests and {len(items)} items")
    except MissingDataFileError as e:
        print("Missing data file:", e)
    except InvalidDataFormatError as e:
        print("Invalid data format:", e)
    except CorruptedDataError as e:
        print("Data corrupted:", e)
