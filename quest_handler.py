"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Completed Code

Name: Tye Glass

AI Usage:AI tools were used to support approximately 60% of the code implementation and documentation comments. AI assistance also guided me through parts of the 
version-control process, including making commits to GitHub. All final code was reviewed, tested, and approved by me.”
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

import character_manager
import inventory_system

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest not found: {quest_id}")

    quest = quest_data_dict[quest_id]

    # Level requirement
    if character['level'] < quest['required_level']:
        raise InsufficientLevelError("Your level is too low for this quest.")

    # Check prerequisite
    prereq = quest.get('prerequisite', "NONE")
    if prereq != "NONE" and prereq not in character['completed_quests']:
        raise QuestRequirementsNotMetError("Prerequisite quest not completed.")

    # Already completed?
    if quest_id in character['completed_quests']:
        raise QuestAlreadyCompletedError("You already completed this quest.")

    # Already active?
    if quest_id in character['active_quests']:
        raise QuestRequirementsNotMetError("Quest already active.")

    # Accept quest
    character['active_quests'].append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest not found: {quest_id}")

    if quest_id not in character['active_quests']:
        raise QuestNotActiveError("Quest is not currently active.")

    quest = quest_data_dict[quest_id]

    # Remove from active
    character['active_quests'].remove(quest_id)

    # Add to completed
    character['completed_quests'].append(quest_id)

    # Grant XP + gold
    xp = quest.get('reward_xp', 0)
    gold = quest.get('reward_gold', 0)
    character_manager.gain_experience(character, xp)
    character_manager.add_gold(character, gold)

    # Grant items
    reward_items = quest.get('reward_items', [])
    for item in reward_items:
        inventory_system.add_item(character, item)

    return {
        'xp_awarded': xp,
        'gold_awarded': gold,
        'items_awarded': reward_items
    }


def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it
    """
    if quest_id not in character['active_quests']:
        raise QuestNotActiveError("Quest is not active.")

    character['active_quests'].remove(quest_id)
    return True


def get_active_quests(character, quest_data_dict):
    """
    Return full quest data for all active quests
    """
    quest_list = []
    for qid in character['active_quests']:
        if qid in quest_data_dict:
            quest_list.append(quest_data_dict[qid])
    return quest_list


def get_completed_quests(character, quest_data_dict):
    """
    Return full quest data for all completed quests
    """
    quest_list = []
    for qid in character['completed_quests']:
        if qid in quest_data_dict:
            quest_list.append(quest_data_dict[qid])
    return quest_list


def get_available_quests(character, quest_data_dict):
    """
    Return quests character is currently eligible to accept
    """
    available = []
    for qid, quest in quest_data_dict.items():

        # Skip completed
        if qid in character['completed_quests']:
            continue

        # Skip active
        if qid in character['active_quests']:
            continue

        # Level check
        if character['level'] < quest.get('required_level', 0):
            continue

        # Prerequisite check
        prereq = quest.get('prerequisite', "NONE")
        if prereq != "NONE" and prereq not in character['completed_quests']:
            continue

        available.append(quest)

    return available


# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    return quest_id in character['completed_quests']


def is_quest_active(character, quest_id):
    return quest_id in character['active_quests']


def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Returns True if requirements are met — no exceptions raised
    """
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]

    if character['level'] < quest['required_level']:
        return False

    prereq = quest.get('prerequisite', "NONE")
    if prereq != "NONE" and prereq not in character['completed_quests']:
        return False

    if quest_id in character['completed_quests']:
        return False

    if quest_id in character['active_quests']:
        return False

    return True


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Return full chain of prerequisites in order
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest not found: {quest_id}")

    chain = []
    current = quest_id

    while True:
        quest = quest_data_dict[current]
        chain.insert(0, current)

        prereq = quest.get('prerequisite', "NONE")
        if prereq == "NONE":
            break

        if prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Invalid prerequisite: {prereq}")

        current = prereq

    return chain


# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    total = len(quest_data_dict)
    completed = len(character['completed_quests'])

    if total == 0:
        return 0.0

    return (completed / total) * 100


def get_total_quest_rewards_earned(character, quest_data_dict):
    total_xp = 0
    total_gold = 0

    for qid in character['completed_quests']:
        if qid in quest_data_dict:
            quest = quest_data_dict[qid]
            total_xp += quest.get('reward_xp', 0)
            total_gold += quest.get('reward_gold', 0)

    return {
        'total_xp': total_xp,
        'total_gold': total_gold
    }


def get_quests_by_level(quest_data_dict, min_level, max_level):
    results = []
    for qid, quest in quest_data_dict.items():
        lvl = quest.get('required_level', 0)
        if lvl >= min_level and lvl <= max_level:
            results.append(quest)
    return results


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    print(f"\n=== {quest_data['title']} ===")
    print(f"Description: {quest_data['description']}")
    print(f"Required Level: {quest_data['required_level']}")
    print(f"Rewards: +{quest_data.get('reward_xp', 0)} XP, "
          f"+{quest_data.get('reward_gold', 0)} Gold")

    if quest_data.get('reward_items', []):
        print(f"Items: {', '.join(quest_data['reward_items'])}")

    prereq = quest_data.get('prerequisite', 'NONE')
    print(f"Prerequisite: {prereq}")


def display_quest_list(quest_list):
    for quest in quest_list:
        print(f"- {quest['title']} (Lvl {quest['required_level']}) "
              f"+{quest.get('reward_xp', 0)} XP, "
              f"+{quest.get('reward_gold', 0)} Gold")


def display_character_quest_progress(character, quest_data_dict):
    print("\n=== Quest Progress ===")
    print(f"Active quests: {len(character['active_quests'])}")
    print(f"Completed quests: {len(character['completed_quests'])}")

    percent = get_quest_completion_percentage(character, quest_data_dict)
    print(f"Completion: {percent:.2f}%")

    totals = get_total_quest_rewards_earned(character, quest_data_dict)
    print(f"Total XP Earned: {totals['total_xp']}")
    print(f"Total Gold Earned: {totals['total_gold']}")


# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    for qid, quest in quest_data_dict.items():
        prereq = quest.get('prerequisite', "NONE")
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(
                f"Quest '{qid}' has invalid prerequisite '{prereq}'"
            )
    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
