"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: Tye Glass

AI Usage: AI tools were used to support approximately 60% of the code implementation and documentation comments. AI assistance also guided me through 
parts of the version-control process, including making commits to GitHub. All final code was reviewed, tested, and approved by me.

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory
    """
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    character["inventory"].append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    """
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} is not in inventory.")

    character["inventory"].remove(item_id)
    return True


def has_item(character, item_id):
    """
    Check if character has a specific item
    """
    return item_id in character["inventory"]


def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    """
    return character["inventory"].count(item_id)


def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    """
    return MAX_INVENTORY_SIZE - len(character["inventory"])


def clear_inventory(character):
    """
    Remove all items from inventory
    """
    removed = list(character["inventory"])
    character["inventory"].clear()
    return removed


# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item (like potion)
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    if item_data["type"] != "consumable":
        raise InvalidItemTypeError("Item is not a consumable.")

    stat_name, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat_name, value)

    remove_item_from_inventory(character, item_id)

    return f"Used {item_id}. {stat_name} increased by {value}."


def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    if item_data["type"] != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    # Unequip current if exists
    if "equipped_weapon" in character and character["equipped_weapon"] is not None:
        unequip_weapon(character)

    # Apply effect
    stat_name, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat_name, value)

    character["equipped_weapon"] = item_id
    remove_item_from_inventory(character, item_id)

    return f"Equipped weapon: {item_id}"


def equip_armor(character, item_id, item_data):
    """
    Equip armor
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    if item_data["type"] != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    # Unequip current if exists
    if "equipped_armor" in character and character["equipped_armor"] is not None:
        unequip_armor(character)

    stat_name, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat_name, value)

    character["equipped_armor"] = item_id
    remove_item_from_inventory(character, item_id)

    return f"Equipped armor: {item_id}"


def unequip_weapon(character):
    """
    Remove weapon and return it to inventory
    """
    if character.get("equipped_weapon") is None:
        return None

    item_id = character["equipped_weapon"]

    # Undo effect
    stat_name, value = parse_item_effect(character["item_data"][item_id]["effect"])
    apply_stat_effect(character, stat_name, -value)

    # Add back to inventory
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    character["inventory"].append(item_id)
    character["equipped_weapon"] = None
    return item_id


def unequip_armor(character):
    """
    Remove armor and return it to inventory
    """
    if character.get("equipped_armor") is None:
        return None

    item_id = character["equipped_armor"]

    stat_name, value = parse_item_effect(character["item_data"][item_id]["effect"])
    apply_stat_effect(character, stat_name, -value)

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    character["inventory"].append(item_id)
    character["equipped_armor"] = None
    return item_id


# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item from a shop
    """
    cost = item_data["cost"]

    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold.")

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    character["gold"] -= cost
    character["inventory"].append(item_id)
    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item for half its cost
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    sell_value = item_data["cost"] // 2

    remove_item_from_inventory(character, item_id)
    character["gold"] += sell_value

    return sell_value


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Convert "health:20" → ("health", 20)
    """
    stat_name, value = effect_string.split(":")
    return stat_name, int(value)


def apply_stat_effect(character, stat_name, value):
    """
    Apply changes to character stats
    """
    character[stat_name] += value

    if stat_name == "health":
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]


def display_inventory(character, item_data_dict):
    """
    Show inventory nicely formatted
    """
    print("\n=== INVENTORY ===")

    if len(character["inventory"]) == 0:
        print("Inventory is empty.")
        return

    counted = {}

    for item in character["inventory"]:
        counted[item] = counted.get(item, 0) + 1

    for item_id, quantity in counted.items():
        item_info = item_data_dict.get(item_id, {})
        name = item_info.get("name", item_id)
        item_type = item_info.get("type", "???")

        print(f"{name} ({item_type}) x{quantity}")

    print("===================\n")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
