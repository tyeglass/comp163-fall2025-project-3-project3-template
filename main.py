"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Completed

Name: Tye Glass

AI Usage: AI tools were used to support approximately 60% of the code implementation and documentation comments. 
AI assistance also guided me through parts of the version-control process, including making commits to GitHub. 
All final code was reviewed, tested, and approved by me.
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

# These global variables store all persistent game information
current_character = None        # Holds the currently loaded character dictionary
all_quests = {}                 # Stores all quest data loaded from files
all_items = {}                 # Stores all item definitions (weapons, armor, consumables)
game_running = False           # Controls the main game loop execution

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """
    Display the main menu and return the player's selection.
    Loops until the player enters a valid number.
    """
    print("\n=== MAIN MENU ===")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")

    # Input loop ensures user does not break the menu with invalid input
    while True:
        choice = input("Choose an option (1-3): ").strip()
        if choice in ("1", "2", "3"):
            return int(choice)
        print("Invalid choice. Enter 1, 2, or 3.")


def new_game():
    """
    Start a new game by creating a new character.
    Handles naming, class selection, and saving the new character.
    """
    global current_character

    print("\n=== NEW GAME ===")
    name = input("Enter character name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    # Allowed class list is defined in character_manager
    print("Choose a class: Warrior, Mage, Rogue, Cleric")
    chosen = input("Class: ").strip().title()

    try:
        # Attempt character creation through module function
        char = character_manager.create_character(name, chosen)
    except InvalidCharacterClassError as e:
        # Raised when given class is not one of the valid ones
        print(f"Invalid class: {e}")
        return

    # Ensure character always has these equipment fields
    char.setdefault("equipped_weapon", None)
    char.setdefault("equipped_armor", None)

    # Attempt saving new character to file
    try:
        character_manager.save_character(char)
        current_character = char  # Store in global state
        print(f"Character created and saved: {name} the {chosen}")
        game_loop()  # Enter the main gameplay loop
    except Exception as e:
        print(f"Error saving character: {e}")


def load_game():
    """
    Loads an existing saved character.
    Shows saved names, validates selection, and loads the chosen file.
    """
    global current_character

    print("\n=== LOAD GAME ===")
    saves = character_manager.list_saved_characters()

    if not saves:
        # No save files found
        print("No saved characters found.")
        return

    # Display files with numbered list
    print("Saved characters:")
    for idx, s in enumerate(saves, start=1):
        print(f"{idx}. {s}")

    while True:
        # User chooses by number or backs out
        choice = input(f"Select (1-{len(saves)}) or 'b' to go back: ").strip()

        if choice.lower() == 'b':
            return

        if choice.isdigit():
            i = int(choice)
            if 1 <= i <= len(saves):
                selected = saves[i - 1]
                try:
                    loaded = character_manager.load_character(selected)

                    # Guarantee the equipment keys exist
                    loaded.setdefault("equipped_weapon", None)
                    loaded.setdefault("equipped_armor", None)

                    current_character = loaded
                    print(f"Loaded character: {loaded['name']}")
                    game_loop()  # Enter game loop with loaded character
                    return

                # Catch specific errors related to save system
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
    Main gameplay loop.
    Runs until player chooses to save & quit.
    Every iteration shows the game menu and routes to the correct feature.
    """
    global game_running, current_character, all_items, all_quests

    if current_character is None:
        # Safety check—should never happen unless new/load failed
        print("No current character. Return to main menu.")
        return

    game_running = True
    print(f"\nEntering world as {current_character['name']} the {current_character['class']}...\n")

    while game_running:
        choice = game_menu()

        # Map menu choice to game actions
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
            # Attempt to save on quit
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
    Shows the core actions available during gameplay.
    Returns integer selection after validation.
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
    Displays character attributes and sends quest progress display
    to quest_handler for formatting.
    """
    global current_character, all_quests

    c = current_character
    print("\n=== CHARACTER STATS ===")
    # Print basic core stats
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

    # Show quest progress
    quest_handler.display_character_quest_progress(c, all_quests)


def view_inventory():
    """
    Main inventory menu.
    Allows user to use, equip, or drop items.
    All logic is handled by inventory_system — this function only routes input.
    """
    global current_character, all_items

    while True:
        print("\n=== INVENTORY MENU ===")

        # Show all items currently held
        inventory_system.display_inventory(current_character, all_items)

        print("Options:")
        print("1. Use Item")
        print("2. Equip Weapon")
        print("3. Equip Armor")
        print("4. Drop Item")
        print("5. Back")

        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            # Use consumable item
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
            # Equip a weapon from inventory
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
            # Drop item entirely from inventory
            iid = input("Enter item id to drop: ").strip()
            try:
                inventory_system.remove_item_from_inventory(current_character, iid)
                print(f"Dropped {iid}.")
            except ItemNotFoundError:
                print("You don't have that item.")

        elif choice == "5":
            return  # Exit inventory menu

        else:
            print("Invalid choice.")


def quest_menu():
    """
    Menu that handles viewing and managing quests.
    Delegates all heavy logic to quest_handler.
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

        # Show active quests
        if choice == "1":
            active = quest_handler.get_active_quests(current_character, all_quests)
            if not active:
                print("No active quests.")
            else:
                quest_handler.display_quest_list(active)

        # Show quests the player is eligible to start
        elif choice == "2":
            available = quest_handler.get_available_quests(current_character, all_quests)
            if not available:
                print("No available quests.")
            else:
                quest_handler.display_quest_list(available)

        # Show quests the player finished
        elif choice == "3":
            completed = quest_handler.get_completed_quests(current_character, all_quests)
            if not completed:
                print("No completed quests.")
            else:
                quest_handler.display_quest_list(completed)

        # Accept a new quest
        elif choice == "4":
            qid = input("Enter quest id to accept: ").strip()
            try:
                quest_handler.accept_quest(current_character, qid, all_quests)
                print("Quest accepted.")
            except QuestNotFoundError:
                print("Quest does not exist.")
            except QuestAlreadyActiveError:
                print("Quest already active.")
            except QuestRequirementsNotMetError:
                print("Requirements not met.")

        # Abandon an active quest
        elif choice == "5":
            qid = input("Enter quest id to abandon: ").strip()
            try:
                quest_handler.abandon_quest(current_character, qid)
                print("Quest abandoned.")
            except QuestNotActiveError:
                print("Quest is not active.")

        # Debug/test only: instantly complete quest
        elif choice == "6":
            qid = input("Enter quest id to mark complete: ").strip()
            try:
                rewards = quest_handler.complete_quest(current_character, qid, all_quests)
                print(f"Quest completed. Rewards: {rewards}")
            except QuestNotFoundError:
                print("Quest not found.")
            except QuestNotActiveError:
                print("Ques
