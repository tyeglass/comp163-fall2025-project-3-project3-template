"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Your Name Here]

AI Usage: ChatGPT helped implement missing logic for all functions.

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size allowed for a character.
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory
    """
    # Check if inventory is already at the maximum capacity
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    # Add the new item to the end of the inventory list
    character["inventory"].append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    """
    # Ensure the item exists before attempting removal
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} is not in inventory.")

    # Remove only one occurrence of the item
    character["inventory"].remove(item_id)
    return True


def has_item(character, item_id):
    """
    Check if character has a specific item
    """
    # Returns True/False depending on if the item is in inventory
    return item_id in character["inventory"]


def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    """
    # Uses list.count() to determine quantity
    return character["inventory"].count(item_id)


def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    """
    # Remaining space = max size minus current number of items
    return MAX_INVENTORY_SIZE - len(character["inventory"])


def clear_inventory(character):
    """
    Remove all items from inventory
    """
    # Store a copy of items removed so caller knows what was cleared
    removed = list(character["inventory"])

    # Completely clear the inventory list
    character["inventory"].clear()
    return removed


# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item (like potion)
    """
    # Item must exist in inventory to be used
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    # Only consumable items can be used
    if item_data["type"] != "consumable":
        raise InvalidItemTypeError("Item is not a consumable.")

    # Convert effect string (ex: "health:20") into components
    stat_name, value = parse_item_effect(item_data["effect"])

    # Apply the stat increase to the character
    apply_stat_effect(character, stat_name, value)

    # Remove the consumed item
    remove_item_from_inventory(character, item_id)

    return f"Used {item_id}. {stat_name} increased by {value}."


def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    """
    # Character must own the item before equipping it
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    # Item must be weapon type
    if item_data["type"] != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    # If another weapon is equipped, remove its stats first
    if "equipped_weapon" in character and character["equipped_weapon"] is not None:
        unequip_weapon(character)

    # Apply the weapon's stats to the character
    stat_name, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat_name, value)

    # Mark the weapon as equipped and remove it from inventory
    character["equipped_weapon"] = item_id
    remove_item_from_inventory(character, item_id)

    return f"Equipped weapon: {item_id}"


def equip_armor(character, item_id, item_data):
    """
    Equip armor
    """
    # Must own the armor to equip it
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    # Ensure the item is armor type
    if item_data["type"] != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    # Remove any previously equipped armor first
    if "equipped_armor" in character and character["equipped_armor"] is not None:
        unequip_armor(character)

    # Apply armor's effect to character stats
    stat_name, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat_name, value)

    # Set new armor equipped
    character["equipped_armor"] = item_id
    remove_item_from_inventory(character, item_id)

    return f"Equipped armor: {item_id}"


def unequip_weapon(character):
    """
    Remove weapon and return it to inventory
    """
    # If no weapon is currently equipped, nothing to unequip
    if character.get("equipped_weapon") is None:
        return None

    item_id = character["equipped_weapon"]

    # Reverse the stat effects of the equipped weapon
    stat_name, value = parse_item_effect(character["item_data"][item_id]["effect"])
    apply_stat_effect(character, stat_name, -value)

    # Make sure there is space to store weapon back in inventory
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    # Put the weapon back into the inventory
    character["inventory"].append(item_id)
    character["equipped_weapon"] = None
    return item_id


def unequip_armor(character):
    """
    Remove armor and return it to inventory
    """
    # If no armor equipped, nothing to remove
    if character.get("equipped_armor") is None:
        return None

    item_id = character["equipped_armor"]

    # Reverse armor's stat effects
    stat_name, value = parse_item_effect(character["item_data"][item_id]["effect"])
    apply_stat_effect(character, stat_name, -value)

    # Ensure space in inventory before returning armor
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    # Add armor back to inventory
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

    # Check if user can afford the item
    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold.")

    # Ensure there is space to store the newly bought item
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    # Deduct gold and add item
    character["gold"] -= cost
    character["inventory"].append(item_id)
    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item for half its cost
    """
    # Must own item to sell it
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    # Determine gold received for sale
    sell_value = item_data["cost"] // 2

    # Remove item from inventory and add gold to character
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
    # Split the effect string into stat name and value
    stat_name, value = effect_string.split(":")
    return stat_name, int(value)


def apply_stat_effect(character, stat_name, value):
    """
    Apply changes to character stats
    """
    # Increase or decrease the specified stat
    character[stat_name] += value

    # Clamp health so it never exceeds max health
    if stat_name == "health":
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]


def display_inventory(character, item_data_dict):
    """
    Show inventory nicely formatted
    """
    print("\n=== INVENTORY ===")

    # If no items, show empty message
    if len(character["inventory"]) == 0:
        print("Inventory is empty.")
        return

    # Dictionary to count item quantities
    counted = {}

    # Count occurrences of each item ID
    for item in character["inventory"]:
        counted[item] = counted.get(item, 0) + 1

    # Display each unique item with its type and count
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
