# character_manager.py
"""
Character Manager Module for COMP 163 - Project 3: Quest Chronicles

Responsibilities:
- Create new characters with class-specific base stats
- Save / load character save files
- Basic character operations (gain XP, level up, add gold, heal, revive)
- Validate loaded save data
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================#
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================#

def create_character(name, character_class):
    """
    Create and return a new character dictionary configured for the given class.

    Valid classes: "Warrior", "Mage", "Rogue", "Cleric"

    Raises:
        InvalidCharacterClassError if the class is not recognized.

    Returns:
        dict: fully initialized character dict
    """
    valid_classes = ["Warrior", "Mage", "Rogue", "Cleric"]

    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"{character_class} is not a valid character class!")

    # Assign class-specific base stats
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
    Persist a character to a human-readable text file.
    Returns True on success.
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    filename = os.path.join(save_directory, f"{character['name']}_save.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"NAME: {character['name']}\n")
        f.write(f"CLASS: {character['class']}\n")
        f.write(f"LEVEL: {character['level']}\n")
        f.write(f"HEALTH: {character['health']}\n")
        f.write(f"MAX_HEALTH: {character['max_health']}\n")
        f.write(f"STRENGTH: {character['strength']}\n")
        f.write(f"MAGIC: {character['magic']}\n")
        f.write(f"EXPERIENCE: {character['experience']}\n")
        f.write(f"GOLD: {character['gold']}\n")
        # Join lists by comma, empty lists wr
