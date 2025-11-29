"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Completed Code

Name: Tye Glass

AI Usage: AI tools were used to support approximately 60% of the code implementation and documentation comments. AI assistance also guided me through parts of the version-control process, 
including making commits to GitHub. All final code was reviewed, tested, and approved by me. I also used AI to fill in missing logic safely and cleanly.
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
    Create and return an enemy dictionary based on the given enemy type.
    Includes stats such as health, strength, magic, and rewards.
    """
    enemy_type = enemy_type.lower()

    # Predefined enemy templates
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

    # Error if type does not match any known enemy
    raise InvalidTargetError(f"Unrecognized enemy type: {enemy_type}")


def get_random_enemy_for_level(character_level):
    """
    Return a suitable enemy depending on the player's level.
    Scales difficulty as level increases.
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Main turn-based combat handler.
    Controls turns, damage application, escaping, and battle resolution.
    """

    def __init__(self, character, enemy):
        self.character = character     # Player stats dictionary
        self.enemy = enemy             # Enemy stats dictionary
        self.combat_active = True      # Determines if battle continues
        self.turn_counter = 0          # Optional turn tracking

    def start_battle(self):
        """
        Runs the full battle loop until one side wins or the player escapes.
        """
        # Prevent starting combat with a dead character
        if self.character['health'] <= 0:
            raise CharacterDeadError("Character is already dead.")

        # Main combat loop
        while self.combat_active:

            # Show current HP values
            display_combat_stats(self.character, self.enemy)

            # --- PLAYER TURN ---
            self.player_turn()

            # Check if enemy died
            result = self.check_battle_end()
            if result is not None:
                self.combat_active = False
                return self._finalize_battle(result)

            # --- ENEMY TURN ---
            self.enemy_turn()

            # Check if player died
            result = self.check_battle_end()
            if result is not None:
                self.combat_active = False
                return self._finalize_battle(result)

        # If combat loop ends because of escape
        return {
            'winner': 'escaped',
            'xp_gained': 0,
            'gold_gained': 0
        }

    def _finalize_battle(self, winner):
        """
        Handles reward distribution or defeat outcome.
        """
        # Player victory → award XP and gold
        if winner == 'player':
            rewards = get_victory_rewards(self.enemy)
            character_manager.gain_experience(self.character, rewards['xp'])
            character_manager.add_gold(self.character, rewards['gold'])
            return {
                'winner': 'player',
                'xp_gained': rewards['xp'],
                'gold_gained': rewards['gold']
            }

        # Enemy victory → no rewards
        return {
            'winner': 'enemy',
            'xp_gained': 0,
            'gold_gained': 0
        }

    def player_turn(self):
        """
        Player chooses an action: attack, ability, or escape attempt.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")

        print("\nYour turn!")
        print("1. Basic Attack")
        print("2. Special Ability")
        print("3. Try to Run")

        choice = input("Choose action: ").strip()

        # Basic attack
        if choice == "1":
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            display_battle_log(f"You hit the {self.enemy['name']} for {damage} damage!")

        # Use class special ability
        elif choice == "2":
            result = use_special_ability(self.character, self.enemy)
            display_battle_log(result)

        # Escape attempt
        elif choice == "3":
            if self.attempt_escape():
                display_battle_log("You escaped successfully!")
                self.combat_active = False
            else:
                display_battle_log("Escape failed!")

        # Invalid menu input
        else:
            display_battle_log("Invalid choice. You lose your turn!")

    def enemy_turn(self):
        """
        Enemy attacks the player automatically each turn.
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")

        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"{self.enemy['name']} hits you for {damage} damage!")

    def calculate_damage(self, attacker, defender):
        """
        Basic damage formula:
        strength minus a small portion of defender's strength.
        Ensures minimum damage of 1.
        """
        damage = attacker['strength'] - (defender['strength'] // 4)
        if damage < 1:
            damage = 1
        return damage

    def apply_damage(self, target, damage):
        """
        Subtract damage from target HP and prevent negative values.
        """
        target['health'] -= damage
        if target['health'] < 0:
            target['health'] = 0

    def check_battle_end(self):
        """
        Check whether the player or enemy has reached 0 HP.
        Returns 'player', 'enemy', or None.
        """
        if self.enemy['health'] <= 0:
            return 'player'
        if self.character['health'] <= 0:
            return 'enemy'
        return None

    def attempt_escape(self):
        """
        50% chance to flee combat.
        """
        chance = random.randint(1, 100)
        if chance <= 50:
            self.combat_active = False
            return True
        return False


# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Routes ability use based on character class.
    """
    cclass = character.get('class', '').lower()

    if cclass == "warrior":
        return warrior_power_strike(character, enemy)
    elif cclass == "mage":
        return mage_fireball(character, enemy)
    elif cclass == "rogue":
        return rogue_critical_strike(character, enemy)
    elif cclass == "cleric":
        return cleric_heal(character)
    else:
        return "No special ability for your class."


def warrior_power_strike(character, enemy):
    """
    Warrior: heavy physical attack dealing double strength.
    """
    damage = character['strength'] * 2
    enemy['health'] -= damage
    if enemy['health'] < 0:
        enemy['health'] = 0
    return f"Warrior Power Strike hits for {damage} damage!"


def mage_fireball(character, enemy):
    """
    Mage: magic attack dealing double magic stat.
    """
    damage = character['magic'] * 2
    enemy['health'] -= damage
    if enemy['health'] < 0:
        enemy['health'] = 0
    return f"Mage Fireball burns for {damage} damage!"


def rogue_critical_strike(character, enemy):
    """
    Rogue: 50% chance to deal triple strength damage.
    """
    chance = random.randint(1, 100)
    if chance <= 50:
        damage = character['strength'] * 3
        enemy['health'] -= damage
        if enemy['health'] < 0:
            enemy['health'] = 0
        return f"Rogue Critical Strike lands for {damage} damage!"
    else:
        return "Rogue Critical Strike missed!"


def cleric_heal(character):
    """
    Cleric: heals 30 HP, cannot exceed max health.
    """
    character['health'] += 30
    if character['health'] > character['max_health']:
        character['health'] = character['max_health']
    return "Cleric Heal restores 30 HP!"


# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check whether the character still has health to fight.
    """
    return character['health'] > 0


def get_victory_rewards(enemy):
    """
    Return XP and gold rewards based on enemy definition.
    """
    return {
        'xp': enemy.get('xp_reward', 0),
        'gold': enemy.get('gold_reward', 0)
    }


def display_combat_stats(character, enemy):
    """
    Print HP status for both the player and enemy.
    """
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")


def display_battle_log(message):
    """
    Format and print a message from the combat system.
    """
    print(f">>> {message}")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
