"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Completed Code

Name: Tye Glass

AI Usage: AI tools were used to support approximately 60% of the code implementation and documentation comments. 
AI assistance also guided me through parts of the version-control process, including making commits to GitHub. All final code was reviewed, tested, and approved by me.
"""

import random

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

import character_manager


# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Build and return an enemy definition dictionary based on the requested type.

    Each enemy profile contains combat statistics (health, strength, magic)
    and reward values (XP and gold) used when the player wins.
    """
    enemy_type = enemy_type.lower()

    # Enemy templates containing predefined stats
    if enemy_type == "goblin":
        return {
            'name': 'Goblin',
            'health': 50,
            'max_health': 50,
            'strength': 8,
            'magic': 2,
            'xp_reward': 25,
            'gold_reward': 10
        }

    elif enemy_type == "orc":
        return {
            'name': 'Orc',
            'health': 80,
            'max_health': 80,
            'strength': 12,
            'magic': 5,
            'xp_reward': 50,
            'gold_reward': 25
        }

    elif enemy_type == "dragon":
        return {
            'name': 'Dragon',
            'health': 200,
            'max_health': 200,
            'strength': 25,
            'magic': 15,
            'xp_reward': 200,
            'gold_reward': 100
        }

    # Unsupported or misspelled enemy types trigger an error
    raise InvalidTargetError(f"Unrecognized enemy type: {enemy_type}")


def get_random_enemy_for_level(character_level):
    """
    Select an appropriate enemy category based on the player's level.

    This function scales encounter difficulty as the character progresses.
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")


def get_victory_rewards(enemy):
    """
    Extract XP and gold rewards from a defeated enemy.
    
    Returns a dictionary with 'xp' and 'gold' keys.
    """
    return {
        'xp': enemy.get('xp_reward', 0),
        'gold': enemy.get('gold_reward', 0)
    }


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Core class managing a turn-based encounter between a player and an enemy.

    Handles turn flow, action execution, health management, escape attempts,
    and determination of battle outcome.
    """

    def __init__(self, character, enemy):
        self.character = character     # Player's data dictionary
        self.enemy = enemy             # Enemy's data dictionary
        self.combat_active = True      # Tracks whether combat is ongoing
        self.turn_counter = 0          # Optional turn counter for extension

    def start_battle(self):
        """
        Execute the battle loop until one side wins or the player escapes.

        This function manages the full encounter sequence and ensures
        all end-of-battle results are processed before returning.
        """
        # Prevent running combat with characters already at 0 HP
        if self.character['health'] <= 0:
            raise CharacterDeadError("Character is already dead.")

        # Main alternating turn loop
        while self.combat_active:

            # Display health bars before each round
            display_combat_stats(self.character, self.enemy)

            # --- PLAYER TURN ---
            self.player_turn()

            # Determine whether the enemy died after the player's action
            result = self.check_battle_end()
            if result is not None:
                self.combat_active = False
                return self._finalize_battle(result)

            # --- ENEMY TURN ---
            self.enemy_turn()

            # Determine whether the player died after enemy's action
            result = self.check_battle_end()
            if result is not None:
                self.combat_active = False
                return self._finalize_battle(result)

        # Occurs only when combat ends via a successful escape
        return {
            'winner': 'escaped',
            'xp_gained': 0,
            'gold_gained': 0
        }

    def _finalize_battle(self, winner):
        """
        Process post-battle rewards and return a structured outcome summary.

        When the player wins, XP and gold are added through character_manager.
        Losses provide no rewards.
        """
        if winner == 'player':
            rewards = get_victory_rewards(self.enemy)
            character_manager.gain_experience(self.character, rewards['xp'])
            character_manager.add_gold(self.character, rewards['gold'])
            return {
                'winner': 'player',
                'xp_gained': rewards['xp'],
                'gold_gained': rewards['gold']
            }

        # Player defeat → no rewards
        return {
            'winner': 'enemy',
            'xp_gained': 0,
            'gold_gained': 0
        }

    def player_turn(self):
        """
        Allow the player to choose between attacking, using a special ability,
        or attempting to escape. Handles invalid menu inputs safely.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")

        print("\nYour turn!")
        print("1. Basic Attack")
        print("2. Special Ability")
        print("3. Try to Run")

        choice = input("Choose action: ").strip()

        # Basic attack logic
        if choice == "1":
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            display_battle_log(f"You hit the {self.enemy['name']} for {damage} damage!")

        # Trigger class-specific special ability
        elif choice == "2":
            result = use_special_ability(self.character, self.enemy)
            display_battle_log(result)

        # Attempt to flee combat with a 50% success chance
        elif choice == "3":
            if self.attempt_escape():
                display_battle_log("You escaped successfully!")
                self.combat_active = False
            else:
                display_battle_log("Escape failed!")

        # Any other input is treated as a misplay
        else:
            display_battle_log("Invalid choice. You lose your turn!")

    def enemy_turn(self):
        """
        Execute the enemy's automatic attack phase.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")

        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"{self.enemy['name']} hits you for {damage} damage!")

    def calculate_damage(self, attacker, defender):
        """
        Compute damage based on a simplified formula:
        attacker strength minus a quarter of the defender's strength.

        Ensures damage never drops below 1 to avoid stalemates.
        """
        damage = attacker['strength'] - (defender['strength'] // 4)
        if damage < 1:
            damage = 1
        return damage

    def apply_damage(self, target, damage):
        """
        Apply damage to the target's health and clamp the value at zero
        to prevent negative HP states.
        """
        target['health'] -= damage
        if target['health'] < 0:
            target['health'] = 0

    def check_battle_end(self):
        """
        Determine whether either combatant has reached 0 HP.

        Returns:
            'player' if the enemy dies,
            'enemy' if the player dies,
            None if combat continues.
        """
        if self.enemy['health'] <= 0:
            return 'player'
        if self.character['health'] <= 0:
            return 'enemy'
        return None

    def attempt_escape(self):
        """
        Attempt to flee combat with 50% success chance.
        """
        return random.random() < 0.5


# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Trigger class-specific special ability.
    """
    char_class = character.get('class', '').lower()

    if char_class == 'warrior':
        damage = character['strength'] * 2
        enemy['health'] -= damage
        if enemy['health'] < 0:
            enemy['health'] = 0
        return f"Warrior uses Power Strike for {damage} damage!"

    elif char_class == 'mage':
        damage = character['magic'] * 2
        enemy['health'] -= damage
        if enemy['health'] < 0:
            enemy['health'] = 0
        return f"Mage casts Fireball for {damage} damage!"

    elif char_class == 'rogue':
        damage = character['strength'] + character['magic']
        enemy['health'] -= damage
        if enemy['health'] < 0:
            enemy['health'] = 0
        return f"Rogue uses Sneak Attack for {damage} damage!"

    elif char_class == 'cleric':
        heal = character['magic']
        character['health'] = min(character['max_health'], character['health'] + heal)
        return f"Cleric uses Healing Prayer, restoring {heal} health!"

    else:
        return "No special ability available."


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_combat_stats(character, enemy):
    """
    Show health bars for both combatants.
    """
    print(f"\n{character['name']}: {character['health']}/{character['max_health']} HP")
    print(f"{enemy['name']}: {enemy['health']}/{enemy['max_health']} HP")


def display_battle_log(message):
    """
    Print combat action messages.
    """
    print(f">>> {message}")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
