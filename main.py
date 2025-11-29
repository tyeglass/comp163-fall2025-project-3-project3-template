"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Completed

Name: Tye Glass
AI Usage: AI tools were used to support approximately 60% of the code implementation and documentation comments.
AI assistance also guided me through parts of the version-control process, including making commits to GitHub. All final code was reviewed, tested, and approved by me.
"""

# Import core modules and all custom subsystems
import os
import random

import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables maintaining currently loaded character and game resources
current_character = None        # Dict containing character data
all_quests = {}                 # Quest definitions loaded from data files
all_items = {}                  # Item definitions loaded from data files
game_running = False           # Controls the main gameplay loop

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """
    Display the main menu and return the player's selection.
    Ensures user only enters valid numeric options.
    """
    print("\n=== MAIN MENU ===")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")

    while True:
        choice = input("Choose an option (1-3): ").strip()
        if choice in ("1", "2", "3"):
            return int(choice)
        print("Invalid choice. Enter 1, 2, or 3.")


def new_game():
    """
    Start a new game by creating a new character.
    Handles character creation, validation, and saving.
    """
    global current_character

    print("\n=== NEW GAME ===")
    name = input("Enter character name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    # Player chooses one of the predefined valid classes
    print("Choose a class: Warrior, Mage, Rogue, Cleric")
    chosen = input("Class: ").strip().title()

    try:
        # Create a new character using character_manager module
        char = character_manager.create_character(name, chosen)
    except InvalidCharacterClassError as e:
        print(f"Invalid class: {e}")
        return

    # Ensure required inventory-equipment fields exist
    char.setdefault("equipped_weapon", None)
    char.setdefault("equipped_armor", None)

    # Save the new character to storage
    try:
        character_manager.save_character(char)
        current_character = char
        print(f"Character created and saved: {name} the {chosen}")
        game_loop()   # Begin game
    except Exception as e:
        print(f"Error saving character: {e}")


def load_game():
    """
    Load an existing saved character from the saved files list.
    Allows player to choose an existing save and loads it into memory.
    """
    global current_character

    print("\n=== LOAD GAME ===")
    saves = character_manager.list_saved_characters()

    # No save files found
    if not saves:
        print("No saved characters found.")
        return

    # Display available characters
    print("Saved characters:")
    for idx, s in enumerate(saves, start=1):
        print(f"{idx}. {s}")

    while True:
        choice = input(f"Select (1-{len(saves)}) or 'b' to go back: ").strip()

        # Allow backing out
        if choice.lower() == 'b':
            return

        # Validate numeric selection
        if choice.isdigit():
            i = int(choice)
            if 1 <= i <= len(saves):
                selected = saves[i - 1]
                try:
                    loaded = character_manager.load_character(selected)

                    # Ensure inventory equipment fields exist
                    loaded.setdefault("equipped_weapon", None)
                    loaded.setdefault("equipped_armor", None)

                    current_character = loaded
                    print(f"Loaded character: {loaded['name']}")
                    game_loop()
                    return

                # Handle specific save errors
                except CharacterNotFoundError:
                    print("Character save not found.")
                    return
                except SaveFileCorruptedError:
                    print("Save file corrupted.")
                    return
                except InvalidSaveDataError as e:
                    print(f"Invalid save data: {e}")
                    return

        print("Invalid selection.")

# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    """
    Primary gameplay loop.
    Displays the main in-game options and processes each player action
    until the player chooses to quit.
    """
    global game_running, current_character, all_items, all_quests

    if current_character is None:
        print("No current character. Return to main menu.")
        return

    game_running = True
    print(f"\nEntering world as {current_character['name']} the {current_character['class']}...\n")

    while game_running:
        choice = game_menu()

        # Route selection to proper game action
        if choice == 1:
            view_character_stats()
        elif choice == 2:
            view_inventory()
        elif choice == 3:
            quest_menu()
        elif choice == 4:
            explore()
        elif choice == 5:
            shop()
        elif choice == 6:
            try:
                save_game()
                print("Game saved. Quitting to main menu.")
            except Exception as e:
                print(f"Save failed: {e}")
            game_running = False
        else:
            print("Invalid choice.")


def game_menu():
    """
    Display the in-game action menu and return chosen option.
    """
    print("\n=== GAME MENU ===")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore (Find Battles)")
    print("5. Shop")
    print("6. Save and Quit")

    while True:
        choice = input("Choose (1-6): ").strip()
        if choice in ("1","2","3","4","5","6"):
            return int(choice)
        print("Invalid choice.")

# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    """
    Print character attributes and quest progress.
    Pulls quest progress display from quest_handler.
    """
    global current_character, all_quests

    c = current_character
    print("\n=== CHARACTER STATS ===")
    print(f"Name: {c.get('name')}")
    print(f"Class: {c.get('class')}")
    print(f"Level: {c.get('level')}")
    print(f"XP: {c.get('experience')}")
    print(f"Health: {c.get('health')}/{c.get('max_health')}")
    print(f"Strength: {c.get('strength')}")
    print(f"Magic: {c.get('magic')}")
    print(f"Gold: {c.get('gold')}")
    print(f"Equipped Weapon: {c.get('equipped_weapon')}")
    print(f"Equipped Armor: {c.get('equipped_armor')}")

    # Delegate quest progress display
    quest_handler.display_character_quest_progress(c, all_quests)


def view_inventory():
    """
    Display inventory contents and let the player use, equip, or drop items.
    Calls inventory_system functions for actual logic.
    """
    global current_character, all_items

    while True:
        print("\n=== INVENTORY MENU ===")

        # Show inventory contents
        inventory_system.display_inventory(current_character, all_items)

        print("Options:")
        print("1. Use Item")
        print("2. Equip Weapon")
        print("3. Equip Armor")
        print("4. Drop Item")
        print("5. Back")

        choice = input("Choose (1-5): ").strip()

        # Delegate item operations based on selection
        if choice == "1":
            iid = input("Enter item id to use: ").strip()
            if iid == "":
                continue
            item_info = all_items.get(iid)
            try:
                result = inventory_system.use_item(current_character, iid, item_info)
                print(result)
            except ItemNotFoundError:
                print("You don't have that item.")
            except InvalidItemTypeError:
                print("That item cannot be used.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            # Equip weapon
            iid = input("Enter weapon id to equip: ").strip()
            item_info = all_items.get(iid)
            try:
                result = inventory_system.equip_weapon(current_character, iid, item_info)
                print(result)
            except ItemNotFoundError:
                print("You don't have that weapon.")
            except InvalidItemTypeError:
                print("That item is not a weapon.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            # Equip armor
            iid = input("Enter armor id to equip: ").strip()
            item_info = all_items.get(iid)
            try:
                result = inventory_system.equip_armor(current_character, iid, item_info)
                print(result)
            except ItemNotFoundError:
                print("You don't have that armor.")
            except InvalidItemTypeError:
                print("That item is not armor.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":
            # Drop item
            iid = input("Enter item id to drop: ").strip()
            try:
                inventory_system.remove_item_from_inventory(current_character, iid)
                print(f"Dropped {iid}.")
            except ItemNotFoundError:
                print("You don't have that item.")

        elif choice == "5":
            return

        else:
            print("Invalid choice.")


def quest_menu():
    """
    Menu for viewing, accepting, abandoning, and force-completing quests.
    Uses quest_handler for all logic.
    """
    global current_character, all_quests

    while True:
        print("\n=== QUEST MENU ===")
        print("1. View Active Quests")
        print("2. View Available Quests")
        print("3. View Completed Quests")
        print("4. Accept Quest")
        print("5. Abandon Quest")
        print("6. Complete Quest (for testing)")
        print("7. Back")

        choice = input("Choose (1-7): ").strip()

        # View lists
        if choice == "1":
            active = quest_handler.get_active_quests(current_character, all_quests)
            if not active:
                print("No active quests.")
            else:
                quest_handler.display_quest_list(active)

        elif choice == "2":
            available = quest_handler.get_available_quests(current_character, all_quests)
            if not available:
                print("No available quests.")
            else:
                quest_handler.display_quest_list(available)

        elif choice == "3":
            completed = quest_handler.get_c
