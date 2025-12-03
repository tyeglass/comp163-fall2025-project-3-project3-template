Quest Chronicles - RPG Adventure Game
Student: Tye Glass
Course: COMP 163 - Fall 2025
Project: 3 - Modular RPG System

📋 Project Overview
Quest Chronicles is a text-based RPG demonstrating mastery of Python modules and exception handling. Players create characters, complete quests, battle enemies, and manage inventory through a modular codebase.

🏗️ Module Architecture
Module Organization
My project is split into 6 functional modules that each handle one responsibility:

1. custom_exceptions.py - All custom exception classes (provided)
Exception hierarchy: GameError → category errors → specific errors
Prevents circular imports since every module needs exceptions

2. game_data.py - Loads and validates quest/item data from files
load_quests(), load_items() - Parse text files
validate_quest_data(), validate_item_data() - Ensure correct format
Separates data loading from game logic

3. character_manager.py - Character creation, saving, loading, leveling
create_character(), save_character(), load_character()
gain_experience(), add_gold(), heal_character()
Uses simple KEY: value text file format for saves

4. inventory_system.py - Item management, equipment, shop
add_item_to_inventory(), use_item(), equip_weapon(), equip_armor()
purchase_item(), sell_item()
Max inventory size: 20 items

5. quest_handler.py - Quest acceptance, completion, prerequisites
accept_quest(), complete_quest(), abandon_quest()
get_active_quests(), get_available_quests()
Validates level requirements and prerequisites


6. combat_system.py - Turn-based battle system
create_enemy() - Factory for goblin, orc, dragon
SimpleBattle class - Manages combat loop
get_victory_rewards() - Extracts XP and gold from enemies

7. main.py - Game launcher, menus, ties everything together
Handles user input and menus
Delegates all logic to other modules
Catches exceptions and displays user-friendly messages
Module Dependencies
main.py → all other modules
quest_handler → character_manager, inventory_system
combat_system → character_manager
Everything → custom_exceptions

Dependencies flow one direction to avoid circular imports.

🚨 Exception Strategy
Philosophy: "Raise Early, Catch Late"
I raise exceptions immediately when errors occur in modules, but catch them at the top level (main.py) where I can show user messages.
When/Why I Raise Specific Exceptions
Data Errors (game_data.py):

MissingDataFileError - File doesn't exist → lets main.py create defaults or exit

InvalidDataFormatError - File has wrong format → tells user data is corrupted

CorruptedDataError - File can't be read → indicates permission/encoding issues

Character Errors (character_manager.py):

InvalidCharacterClassError - Invalid class name → prevents creating broken characters

CharacterNotFoundError - Save file missing → lets user create new or choose different save

CharacterDeadError - Actions on dead character → prevents gaining XP when dead

Quest Errors (quest_handler.py):

QuestNotFoundError - Invalid quest ID → tells user quest doesn't exist

InsufficientLevelError - Level too low → explains why they can't accept

QuestRequirementsNotMetError - Prerequisite not done → shows what's needed first

QuestAlreadyCompletedError - Already completed → prevents re-doing quests

Inventory Errors (inventory_system.py):

InventoryFullError - At 20 item limit → prompts user to sell/drop items

ItemNotFoundError - Item not in inventory → prevents using items you don't have

InsufficientResourcesError - Not enough gold → tells user they can't afford it

Combat Errors (combat_system.py):

InvalidTargetError - Enemy type doesn't exist → catches typos in enemy names

CombatNotActiveError - Combat action outside battle → prevents invalid states

Exception Catching Pattern
# In main.py
try:
    quest_handler.accept_quest(char, quest_id, quests)
    print("Quest accepted!")
except QuestNotFoundError:
    print("That quest doesn't exist.")
except InsufficientLevelError:
    print("Your level is too low.")
except QuestRequirementsNotMetError:
    print("Complete the prerequisite quest first.")

Why catch in main.py? Only the UI layer knows how to tell the user what happened. Modules focus on logic, main.py handles user interaction.

🎯 Design Choices
1. Simple Text File Format for Saves
Choice: KEY: value format instead of JSON
Why: Assignment required text file practice. Easy to debug (can open in Notepad). No external libraries needed.

2. Dictionaries for Everything
Choice: Characters, quests, items are all dictionaries
Why: Flexible (easy to add fields), simple (no classes needed), maps directly to file format.

3. SimpleBattle as a Class
Choice: Only class in the project
Why: Combat has state (combat_active, turn_counter) that needs to persist across method calls. Functions work fine for stateless operations (create character, add item).

4. Module Import Strategy
Full module imports: import character_manager (clear where functions come from)
Import all exceptions: from custom_exceptions import * (many exceptions, readability)

5. Character Class Balance
Warrior: 120 HP, 15 STR, 5 MAG - tank
Mage: 80 HP, 8 STR, 20 MAG - glass cannon
Rogue: 90 HP, 12 STR, 10 MAG - balanced
Cleric: 100 HP, 10 STR, 15 MAG - support/healer
Why: Different playstyles without any class being strictly better.

🤖 AI Usage
What AI Helped With:

Completing missing function implementations - I had function stubs, AI helped fill in logic for parsing quest/item data files
Fixing save file bug - AI identified that blank lines in save files caused ValueError: not enough values to unpack. Solution: skip blank lines with if not line.strip(): continue
Completing combat_system.py - File was cut off. AI completed attempt_escape(), use_special_ability(), and added missing get_victory_rewards() function
Fixing main.py syntax error - Line 399 had unterminated string. AI completed the file and added missing save_game() and load_game_data() functions
Exception handling patterns - AI suggested try-except structures and when to raise vs catch exceptions

What I Did Independently:

Designed module architecture and decided what goes in each module
Chose character stats, enemy stats, item effects
Created save file format structure
Integrated modules through imports
Ran tests, interpreted errors, applied fixes
Debugged module interactions

How I Used AI:

AI was a coding assistant for implementation details and debugging, not a complete solution generator. I understood every line before including it and modified suggestions to fit my design. I also used it to generate this README file

🎮 How to Play
Installation

Clone repository:
git clone [your-repo-url]
cd comp163-fall2025-project-3

Run game:

python main.py
Quick Start
Main Menu:
New Game - Create character (choose name + class: Warrior, Mage, Rogue, Cleric)
Load Game - Select saved character
Exit

Game Menu:

View Character Stats - See your level, HP, gold, quest progress
View Inventory - Use items, equip weapons/armor, drop items
Quest Menu - Accept, complete, or abandon quests
Explore - Fight random enemies (earn XP and gold)
Shop - Buy/sell items
Save and Quit - Saves to data/save_games/YourName_save.txt
Combat System
When exploring, you encounter enemies:
Option 1: Basic Attack
Option 2: Special Ability (class-specific)
Option 3: Try to Run (50% chance)
Win battles to earn XP and gold. Level up to get stronger!
Quest System
Accept quests from Quest Menu. Some require:
Minimum level (e.g., level 5 required)
Prerequisites (complete quest A before quest B)
Complete quests for XP, gold, and item rewards.
Tips
Start with quest first_steps
Fight goblins at low levels, orcs at mid levels, dragons at high levels
Buy health potions early (10 gold each)
Save frequently!

📊 Testing

Run automated tests:

python -m pytest tests/ -v
Test Coverage:
Module structure tests (all modules import correctly)
Exception handling tests (exceptions raised appropriately)
Integration tests (modules work together)
Current Status: 44/44 tests passing ✅

📝 Project Stats
Lines of Code: ~1500
Modules: 7
Custom Exceptions: 16
Functions: 60+
Character Classes: 4
Enemy Types: 3
Test Cases: 44


















# COMP 163: Project 3 - Quest Chronicles

**AI Usage: Free Use (with explanation requirement)**

## Overview

Build a complete modular RPG adventure game demonstrating mastery of **exceptions and modules**.

## Getting Started

### Step 1: Accept Assignment
1. Click the assignment link provided in Blackboard
2. Accept the assignment - this creates your personal repository
3. Clone your repository to your local machine:
```bash
git clone [your-personal-repo-url]
cd [repository-name]
```

### Step 2: Understand the Project Structure

Your repository contains:

```
quest_chronicles/
├── main.py                     # Game launcher (COMPLETE THIS)
├── character_manager.py        # Character creation/management (COMPLETE THIS)
├── inventory_system.py         # Item and equipment management (COMPLETE THIS)
├── quest_handler.py            # Quest system (COMPLETE THIS)
├── combat_system.py            # Battle mechanics (COMPLETE THIS)
├── game_data.py                # Data loading and validation (COMPLETE THIS)
├── custom_exceptions.py        # Exception definitions (PROVIDED)
├── data/
│   ├── quests.txt             # Quest definitions (PROVIDED)
│   ├── items.txt              # Item database (PROVIDED)
│   └── save_games/            # Player save files (created automatically)
├── tests/
│   ├── test_module_structure.py       # Module organization tests
│   ├── test_exception_handling.py     # Exception handling tests
│   └── test_game_integration.py       # Integration tests
└── README.md                   # This file
```

### Step 3: Development Workflow

```bash
# Work on one module at a time
# Test your code frequently

# Commit and push to see test results
git add .
git commit -m "Implement character_manager module"
git push origin main

# Check GitHub for test results (green checkmarks = passed!, red xs = at least 1 failed test case. Click the checkmark or x and then "Details" to see what test cases passed/failed)
```

## Core Requirements (60 Points)

### Critical Constraint
You may **only** use concepts covered through the **Exceptions and Modules** chapters. 

### 🎨 Creativity and Customization

This project encourages creativity! Here's what you can customize:

**✅ FULLY CUSTOMIZABLE:**
- **Character stats** - Adjust health, strength, magic for balance
- **Enemy stats** - Make enemies easier or harder
- **Special abilities** - Design unique abilities for each class
- **Additional enemies** - Add your own enemy types beyond the required three
- **Game mechanics** - Add status effects, combos, critical hits, etc.
- **Quest rewards** - Adjust XP and gold amounts
- **Item effects** - Create unique items with creative effects

**⚠️ REQUIRED (for testing):**
- **4 Character classes:** Warrior, Mage, Rogue, Cleric (names must match exactly)
- **3 Enemy types:** "goblin", "orc", "dragon" (must exist, stats flexible)
- **All module functions** - Must have the specified function signatures
- **Exception handling** - Must raise appropriate exceptions

**💡 CREATIVITY TIPS:**
1. Start with required features working
2. Add creative elements incrementally
3. Test after each addition
4. Be ready to explain your design choices in the interview
5. Bonus interview points for thoughtful, balanced customization!

**Example Creative Additions:**
- Vampire enemy that heals when attacking
- Warrior "Last Stand" ability that activates when health is low
- Poison status effect that deals damage over time
- Critical hit system based on character stats
- Rare "legendary" weapons with special effects

### Module 1: custom_exceptions.py (PROVIDED - 0 points to implement)

**This module is provided complete.** It defines all custom exceptions you'll use throughout the project.

### Module 2: game_data.py (10 points)

### Module 3: character_manager.py (15 points)

### Module 4: inventory_system.py (10 points)

### Module 5: quest_handler.py (10 points)

### Module 6: combat_system.py (10 points)

### Module 7: main.py (5 points)

## Automated Testing & Validation (60 Points)

## Interview Component (40 Points)

**Creativity Bonus** (up to 5 extra points on interview):
- Added 2+ custom enemy types beyond required three
- Designed unique and balanced special abilities
- Implemented creative game mechanics (status effects, advanced combat, etc.)
- Thoughtful stat balancing with clear reasoning

**Note:** Creativity is encouraged, but functionality comes first! A working game with required features scores higher than a broken game with lots of extras.

### Update README.md

Document your project with:

1. **Module Architecture:** Explain your module organization
2. **Exception Strategy:** Describe when/why you raise specific exceptions
3. **Design Choices:** Justify major decisions
4. **AI Usage:** Detail what AI assistance you used
5. **How to Play:** Instructions for running the game

### What to Submit:

1. **GitHub Repository:** Your completed multi-module project
2. **Interview:** Complete 10-minute explanation session
3. **README:** Updated documentation

## Protected Files Warning

⚠️ **IMPORTANT: Test Integrity**

Test files are provided for your learning but are protected. Modifying test files constitutes academic dishonesty and will result in:

- Automatic zero on the project
- Academic integrity investigation

You can view tests to understand requirements, but any modifications will be automatically detected.
