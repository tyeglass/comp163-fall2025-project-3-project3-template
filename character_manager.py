"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: Tye Glass

AI Usage: AI tools were used to support approximately 60% of the code implementation and documentation comments. AI assistance also guided me through parts of the version-control process, including making commits to GitHub. All final code was reviewed, tested, and approved by me.

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    """
    Create a new character with base stats depending on the chosen class.

    - Verifies that the provided class is valid.
    - Assigns default health, strength, and magic values.
    - Returns a fully initialized character dictionary.
    """
    valid_classes = ["Warrior", "Mage", "Rogue", "Cleric"]

    # Reject unknown classes
    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"{character_class} is not a valid character class!")

    # Assign class-specific stats
    if character_class == "Warrior":
        health = 120
        strength = 15
        magic = 5
    elif character_class == "Mage":
        health = 80
        strength = 8
        magic = 20
    elif character_class == "Rogue":
        health = 90
        strength = 12
        magic = 10
    elif character_class == "Cleric":
        health = 100
        strength = 10
        magic = 15

    # Build the character dictionary that holds all core data
    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": health,
        "max_health": health,
        "strength": strength,
        "magic": magic,
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }

    return character


def save_character(character, save_directory="data/save_games"):
    """
    Save the character to a text file.

    - Creates the save directory if it does not exist.
    - Writes each character attribute on its own line.
    - Returns True when save succeeds.
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Save file named after the character
    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

    # Write character data to file (NO BLANK LINES!)
    with open(filename, "w") as f:
        f.write(f"NAME: {character['name']}\n")
        f.write(f"CLASS: {character['class']}\n")
        f.write(f"LEVEL: {character['level']}\n")
        f.write(f"HEALTH: {character['health']}\n")
        f.write(f"MAX_HEALTH: {character['max_health']}\n")
        f.write(f"STRENGTH: {character['strength']}\n")
        f.write(f"MAGIC: {character['magic']}\n")
        f.write(f"EXPERIENCE: {character['experience']}\n")
        f.write(f"GOLD: {character['gold']}\n")
        f.write(f"INVENTORY: {','.join(character['inventory'])}\n")
        f.write(f"ACTIVE_QUESTS: {','.join(character['active_quests'])}\n")
        f.write(f"COMPLETED_QUESTS: {','.join(character['completed_quests'])}\n")

    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load a character from a save file.

    - Ensures the save file exists.
    - Reads and parses all key/value pairs.
    - Converts lists and numbers to the correct types.
    - Validates that the character contains all required fields.
    """
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    # Fail if the save file does not exist
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file for {character_name}")

    # Read file safely
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
    except:
        raise SaveFileCorruptedError("Save file exists but could not be read.")

    character = {}

    # Parse each line into dictionary fields
    try:
        for line in lines:
            # Skip blank lines
            if not line.strip():
                continue
                
            key, value = line.strip().split(": ", 1)

            # Convert lists properly
            if key in ["INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"]:
                # Handle empty lists (empty string should become empty list)
                character[key.lower()] = value.split(",") if value else []

            # Convert numeric fields
            elif key in ["LEVEL", "HEALTH", "MAX_HEALTH", "STRENGTH", "MAGIC", "EXPERIENCE", "GOLD"]:
                character[key.lower()] = int(value)

            # Store everything else as string
            else:
                character[key.lower()] = value
    except:
        raise InvalidSaveDataError("Save file formatting is incorrect.")

    # Verify data integrity
    validate_character_data(character)

    return character


def list_saved_characters(save_directory="data/save_games"):
    """
    Return a list of all saved character names.

    - Checks the save directory (if missing, returns empty list).
    - Collects all filenames ending in '_save.txt'.
    - Removes the suffix to get character names.
    """
    if not os.path.exists(save_directory):
        return []

    files = os.listdir(save_directory)
    characters = []

    for filename in files:
        if filename.endswith("_save.txt"):
            characters.append(filename.replace("_save.txt", ""))

    return characters


def delete_character(character_name, save_directory="data/save_games"):
    """
    Remove a saved character file from the system.

    - Ensures the file exists.
    - Deletes it permanently.
    """
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"{character_name} does not exist.")

    os.remove(filename)
    return True


# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add experience to a character and handle level-ups.

    - Dead characters cannot gain XP.
    - Levels require (level * 100) XP.
    - Leveling restores health and increases stats.
    """
    if character["health"] <= 0:
        raise CharacterDeadError("Character is dead and cannot gain experience.")

    character["experience"] += xp_amount

    # Process possible multiple level-ups
    while character["experience"] >= character["level"] * 100:
        character["experience"] -= (character["level"] * 100)
        character["level"] += 1

        # Increase stats on level-up
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]


def add_gold(character, amount):
    """
    Adjust the character's gold total.

    - Can add or subtract gold.
    - Prevents total gold from becoming negative.
    """
    new_total = character["gold"] + amount

    if new_total < 0:
        raise ValueError("Not enough gold.")

    character["gold"] = new_total
    return new_total


def heal_character(character, amount):
    """
    Restore character health by a certain amount.

    - Health cannot exceed max_health.
    - Returns the number of health points actually restored.
    """
    original = character["health"]
    character["health"] = min(character["max_health"], character["health"] + amount)
    return character["health"] - original


def is_character_dead(character):
    """
    Determine whether the character has 0 or less health.
    """
    return character["health"] <= 0


def revive_character(character):
    """
    Revive a dead character at 50% max health.
    """
    character["health"] = character["max_health"] // 2
    return True


# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Validate that a character dictionary is complete and correctly formatted.

    - Ensures all required fields exist.
    - Confirms numeric fields contain integers.
    - Confirms inventory and quest fields are lists.
    """
    required = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    # Ensure all fields are present
    for key in required:
        if key not in character:
            raise InvalidSaveDataError(f"Missing field: {key}")

    # Ensure numeric fields are proper integers
    numeric_fields = ["level", "health", "max_health", "strength", "magic", "experience", "gold"]

    for key in numeric_fields:
        if not isinstance(character[key], int):
            raise InvalidSaveDataError(f"{key} must be a number.")

    # Ensure list fields are lists
    for key in ["inventory", "active_quests", "completed_quests"]:
        if not isinstance(character[key], list):
            raise InvalidSaveDataError(f"{key} must be a list.")

    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
