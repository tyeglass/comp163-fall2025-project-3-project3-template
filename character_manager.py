"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code
Name: Tye Glass
Date: 11/20/2025
AI Usage: ChatGPT AI assistance was used for approximately 50% of this project, specifically to help clarify inheritance structure,
#refine method overriding logic, generate explanatory comments, and verify behavior against GitHub test cases.


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
    Create a new character with stats based on class

    Valid classes: Warrior, Mage, Rogue, Cleric
    """

    valid_classes = ["Warrior", "Mage", "Rogue", "Cleric"]

    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"{character_class} is not a valid character class!")

    # Base stats
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

    # Standard character fields
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
    Save character to file
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

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
        f.write("INVENTORY: " + ",".join(character["inventory"]) + "\n")
        f.write("ACTIVE_QUESTS: " + ",".join(character["active_quests"]) + "\n")
        f.write("COMPLETED_QUESTS: " + ",".join(character["completed_quests"]) + "\n")

    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file
    """
    filename = os.path.join(save_directory, f"{character_name}_save.txt")

    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file for {character_name}")

    try:
        with open(filename, "r") as f:
            lines = f.readlines()
    except:
        raise SaveFileCorruptedError("Save file exists but could not be read.")

    character = {}

    try:
        for line in lines:
            key, value = line.strip().split(": ")

            if key in ["INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"]:
                character[key.lower()] = value.split(",") if value else []
            elif key in ["LEVEL", "HEALTH", "MAX_HEALTH", "STRENGTH", "MAGIC", "EXPERIENCE", "GOLD"]:
                character[key.lower()] = int(value)
            else:
                character[key.lower()] = value
    except:
        raise InvalidSaveDataError("Save file formatting is incorrect.")

    validate_character_data(character)

    return character


def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
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
    Delete a character's save file
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
    Add experience and level up if needed
    """
    if character["health"] <= 0:
        raise CharacterDeadError("Character is dead and cannot gain experience.")

    character["experience"] += xp_amount

    while character["experience"] >= character["level"] * 100:
        character["experience"] -= (character["level"] * 100)
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]


def add_gold(character, amount):
    """
    Add gold (negative allowed for spending)
    """
    new_total = character["gold"] + amount

    if new_total < 0:
        raise ValueError("Not enough gold.")

    character["gold"] = new_total
    return new_total


def heal_character(character, amount):
    """
    Heal character up to max health
    """
    original = character["health"]
    character["health"] = min(character["max_health"], character["health"] + amount)
    return character["health"] - original


def is_character_dead(character):
    """
    Check if character is dead
    """
    return character["health"] <= 0


def revive_character(character):
    """
    Revive character at 50% health
    """
    character["health"] = character["max_health"] // 2
    return True


# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Ensure character dict contains required fields
    """
    required = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for key in required:
        if key not in character:
            raise InvalidSaveDataError(f"Missing field: {key}")

    numeric_fields = ["level", "health", "max_health", "strength", "magic", "experience", "gold"]

    for key in numeric_fields:
        if not isinstance(character[key], int):
            raise InvalidSaveDataError(f"{key} must be a number.")

    for key in ["inventory", "active_quests", "completed_quests"]:
        if not isinstance(character[key], list):
            raise InvalidSaveDataError(f"{key} must be a list.")

    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
