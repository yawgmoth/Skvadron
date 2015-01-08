

PHYSICAL = 1
MAGICAL = 2
PURE = 3

class Handler(object):
    def __init__(self, priority=1):
        self.priority = priority
        self.active = True
    def __call__(self, atk, targets):
        return atk
    def finalize(self):
        pass
    def die(self):
        pass

class AttackHandler(Handler):
    pass

class DefenseHandler(Handler):
    pass

class StartTurnHandler(object):
    def __init__(self, priority=1):
        self.priority = priority
        self.active = True
    def __call__(self, unit, enemy_units):
        pass
    def finalize(self):
        pass
    def die(self):
        pass
        
class Component(object):
    icon = 0
    def __init__(self):
        pass
    def apply(self, unit):
        self.unit = unit
        
class AHandlerComponent(object):
    def apply(self, unit):
        unit.add_attack_handler(self)
        self.unit = unit
        
class DHandlerComponent(object):
    def apply(self, unit):
        unit.add_defense_handler(self)
        self.unit = unit
        
class AbilityComponent(Component):
    def apply(self, unit):
        unit.add_ability(self)
        self.unit = unit
        
class SHandlerComponent(object):
    def apply(self, unit):
        unit.add_start_turn_handler(self)
        self.unit = unit
        
class AbilityHandlerComponent(object):
    def apply(self, unit):
        unit.add_ability_handler(self)
        self.unit = unit
        
class Ability(object):
    def get_attacks(self, unit, enemy_units):
        return [Attack(unit)]
    def get_targets(self, unit, enemy_units):
        return enemy_units
    def get_mana_cost(self):
        return 0.0
    def finalize(self):
        pass
    def die(self):
        pass
        
class AbilityHandler(Handler):
    def __call__(self, ability, valid_abilities, unit, enemy_units):
        if valid_abilities:
            return valid_abilities[0]
        return None
        
class DamageHandler(object):
    def __call__(self, atk):
        pass
        
class Buff(object):
    def __init__(self, count=0):
        self.count = count
        
ATTACK_KIND = 1
BUFF_KIND = 2
    
class Attack(object):
    def __init__(self, source, damage=0, type=PHYSICAL, kind=ATTACK_KIND, ability=None):
        self.source = source
        self.damage = damage
        self.target = None
        self.type = type
        self.kind = kind
        self.handlers = []
        self.ability=ability
    def do_damage(self):
        for h in self.handlers:
            h(self)
        if self.target and self.target.health > 0:
            self.target.health -= self.damage
            if self.target.health <= 0:
                self.target.die()
    def clone(self):
        result = Attack(self.source, self.damage, self.type, self.kind, self.ability)
        result.target = self.target
        result.handlers = self.handlers[:]
        return result
    
class Unit(object):
    def __init__(self, owner, name="unit", health=100.0, mana=100.0):
        self.attack_handlers = []
        self.defense_handlers = []
        self.start_turn_handlers = []
        self.ability_handlers = []
        self.health = health
        self.max_health = health
        self.mana = mana
        self.max_mana = mana
        self.owner = owner
        self.name = name
        self.owner.units.append(self)
        self.components = []
        self.buffs = []
        self.traits = []
        self.abilities = []
    def start_turn(self, enemy_units):
        for h in self.start_turn_handlers:
            h(self, enemy_units)
    def has_trait(self, trait):
        return trait in self.traits
    def get_attack(self, targets):
        valid_abilities =[]
        for a in self.abilities:
            if a.get_mana_cost() < self.mana:
                valid_abilities.append(a)
        ability = None
        for a in self.ability_handlers:
            ability = a(ability, valid_abilities, self, targets)
        if not ability:
            print "No ability selected o_O"
            return []
        self.mana -= ability.get_mana_cost()
        valid_targets = ability.get_targets(self, targets)
        atks = ability.get_attacks(self, targets)
        for h in self.attack_handlers:
            newatks = []
            for atk in atks:
                res = h(atk, valid_targets)
                if type(res) == list:
                    newatks.extend(res)
                else:
                    newatks.append(res)
            atks = newatks
        
        return atks
    def be_attacked(self, attack, units):
        for h in self.defense_handlers:
            attack = h(attack, units)
        attack.do_damage()
    def add_attack_handler(self, handler):
        self.attack_handlers.append(handler)
        self.attack_handlers.sort(key=lambda h: h.priority)
    def add_defense_handler(self, handler):
        self.defense_handlers.append(handler)
        self.defense_handlers.sort(key=lambda h: h.priority)
    def add_start_turn_handler(self, handler):
        self.start_turn_handlers.append(handler)
        self.start_turn_handlers.sort(key=lambda h: h.priority)
    def add_ability_handler(self, handler):
        self.ability_handlers.append(handler)
        self.ability_handlers.sort(key=lambda h: h.priority)
    def add_ability(self, ability):
        self.abilities.append(ability)
    def add_buff(self, buff):
        found = False
        for b in self.buffs:
            if b.name == buff.name and b.count:
                b.count += buff.count
                found = True
        if not found:
            self.buffs.append(buff)
    def die(self):
        if self in self.owner.units:
            self.owner.units.remove(self)
            for h in self.attack_handlers + self.defense_handlers + self.ability_handlers + self.abilities:
                h.die()
    def finalize(self):
        for h in self.attack_handlers + self.defense_handlers + self.ability_handlers + self.abilities:
            h.finalize()
        if not self.ability_handlers:
            self.ability_handlers.append(RandomAbilitySelector())
        
class Player(object):
    def __init__(self, name, is_human):
        self.units = []
        self.current_unit = -1
        self.name = name
        self.enemy_units = []
        self.is_human = is_human
    def make_turn(self, enemy_units):
        if self.units:
            for u in self.units:
                u.start_turn(enemy_units)
            self.current_unit += 1
            self.current_unit %= len(self.units)
            self.make_attack(self.units[self.current_unit], enemy_units)
    def make_attack(self, unit, enemy_units):
        self.enemy_units = enemy_units
        atks = unit.get_attack(enemy_units)
        for atk in atks:
            if atk.target:
                atk.target.be_attacked(atk, self.units)
    def finalize(self):
        for u in self.units:
            u.finalize()
            

class Game(object):
    def __init__(self, players):
        self.players = players
    def game_ended(self):
        has_units = 0
        if self.turns > 10000:
            print "PANIC MODE, THEY DON'T FINISH!"
            for p in self.players:
                p.units = []
            return True
        for p in self.players:
            if p.units:
                has_units += 1
        return has_units <= 1
    def run(self):
        current_player = 0
        self.turns = 0
        while not self.game_ended() and self.players:
            enemy_units = []
            for i, p in enumerate(self.players):
                if i != current_player:
                    enemy_units.extend(p.units)
            self.players[current_player].make_turn(enemy_units)
            current_player += 1
            current_player %= len(self.players)
            self.turns += 1
        winner = None
        for i,p in enumerate(self.players):
            #print p.name, "has", len(p.units), "units left"
            if p.units:
                winner = i
            #for u in p.units:
            #    print "    ", u.name
        return winner
            
components = {}

def component(cls):
    components[cls.name] = cls
    return cls
    
SELECTOR = 1
ATTACK = 2
DEFENSE = 4
SPECIAL = 256
DEBUG = 16
TRAIT = 32
ABILITY = 64
ABILITY_SELECTOR = 128
BODY = 8

@component
class RoundRobinTargetSelector(AttackHandler,AHandlerComponent):
    name = "RoundRobinTargetSelector"
    description = "Target enemy units one after another"
    type = SELECTOR
    icon = 141
    def __init__(self):
        self.index = -1
        self.priority = 0
    def __call__(self, atk, targets):
        if not targets:
            return atk
        self.index += 1
        self.index %= len(targets)
        atk.target = targets[self.index]
        return atk
     
@component
class WeakestTargetSelector(AttackHandler,AHandlerComponent):
    name = "WeakestTargetSelector"
    description = "Always target the enemy unit with the lowest health"
    type = SELECTOR
    icon = 210
    def __init__(self):
        self.priority = 0
    def __call__(self, atk, targets):
        if not targets:
            return atk
        minh = targets[0].health
        minat = targets[0]
        for t in targets:
            if t.health < minh:
                minh = t.health
                minat = t
        atk.target = minat
        return atk
        
        
import random

@component
class RandomTargetSelector(AttackHandler,AHandlerComponent):
    name = "RandomTargetSelector"
    description = "Always target a random unit"
    type = SELECTOR
    icon = 260
    def __init__(self):
        self.priority = 0
    def __call__(self, atk, targets):
        if not targets:
            return atk
        atk.target = random.choice(targets)
        return atk
        
@component
class RandomAbilitySelector(AbilityHandler,AbilityHandlerComponent):
    name = "RandomAbilitySelector"
    description = "Always select a random available ability"
    type = ABILITY_SELECTOR
    icon = 260
    def __init__(self):
        self.priority = 0
    def __call__(self, ability, valid_abilities, unit, enemy_units):
        return random.choice(valid_abilities)

@component
class BasicPhysicalAttack(Ability, AbilityComponent):
    name = "BasicPhysicalAttack"
    description = "Does 10 physical damage"
    type = ATTACK
    icon = 395
    def get_attacks(self, unit, enemy_units):
        return [Attack(unit, damage=10.0, type=PHYSICAL)]
    
        
@component
class BasicMixedAttack(Ability, AbilityComponent):
    name = "BasicMixedAttack"
    description = "Does 5 physical damage and 5 magical damage (separate damage events)"
    type = ATTACK
    icon = 393
    def get_attacks(self, unit, enemy_units):
        return [Attack(unit, damage=5.0, type=PHYSICAL), Attack(unit,damage=5.0, type=MAGICAL)]
        
@component
class PhysicalBurstAttack(Ability, AbilityComponent):
    name = "PhysicalBurstAttack"
    description = "Does 4 bursts of 2,2,2 and 3 physical damage"
    type = ATTACK
    icon = 200
    def get_attacks(self, unit, enemy_units):
        return [Attack(unit, damage=2.0, type=PHYSICAL), Attack(unit, damage=2.0, type=PHYSICAL),
                Attack(unit, damage=2.0, type=PHYSICAL), Attack(unit,damage=3.0, type=PHYSICAL)]
        
class ImprovingPhysicalAttackBuff(Buff):
    name = "ImprovingPhysicalAttack"
    description = "Unit deals %count damage (increases with stacks)"
    icon = 370
    def __init__(self, count=2):
        self.count = count
        if self.count == 2:
            self.count = 4
        
@component
class ImprovingPhysicalAttack(Ability, AbilityComponent):
    name = "ImprovingPhysicalAttack"
    description = "Does 2 physical attack on the first attack, but doubles damage after every attack. When it would reach 128 damage, it resets to 2 instead"
    type = ATTACK
    icon = 370
    def __init__(self):
        self.priority = 1
        self.dmg = 2.0
    def get_attacks(self, unit, enemy_units):
        dmg = self.dmg
        self.dmg *= 2.0
        unit.add_buff(ImprovingPhysicalAttackBuff(self.dmg - dmg))
        if self.dmg >= 128:
            self.dmg = 2.0
            atk.source.add_buff(ImprovingPhysicalAttackBuff(2.0-self.dmg))
        return [Attack(unit, damage=dmg, type=PHYSICAL)]
        
@component
class BasicPureAttack(Ability, AbilityComponent):
    name = "BasicPureAttack"
    description = "Does 8 pure damage"
    type = ATTACK
    icon = 372
    def get_attacks(self, unit, enemy_units):
        return [Attack(unit, damage=8.0, type=PURE)]
        
@component
class HolySmiteAttack(Ability, AttackHandler, Component):
    name = "HolySmiteAttack"
    description = "Does 9 physical damage; damage against undead units is doubled"
    type = ATTACK
    icon = 376
    def __init__(self):
        self.priority = 1
    def apply(self, unit):
        unit.add_ability(self)
        unit.add_attack_handler(self)
        self.unit = unit
    def __call__(self, atk, targets):
        if atk.ability == self.name and atk.target.has_trait(UNDEAD):
            atk.damage *= 2.0
        return atk
    def get_attacks(self, unit, enemy_units):
        return [Attack(unit, damage=9.0, type=PHYSICAL, ability=self.name)]
        
@component
class BasicMagicalAttack(Ability, AbilityComponent):
    name = "BasicMagicalAttack"
    description = "Does 10 magical damage"
    type = ATTACK
    icon = 190
    def get_attacks(self, unit, enemy_units):
        return [Attack(unit, damage=10.0, type=MAGICAL)]
        
class LifeLeechHandler(DamageHandler):
    def __init__(self, unit, factor):
        self.unit = unit
        self.factor = factor
    def __call__(self, atk):
        self.unit.health += self.factor*atk.damage
        self.unit.health = min(self.unit.health, self.unit.max_health)
        
        
@component
class LifeLeechPhysicalAttack(Ability, AbilityComponent):
    name = "LifeLeechPhysicalAttack"
    description = "Does 8 physical damage, and restores health equal to 30% of the resulting damage"
    type = ATTACK
    icon = 267
    def get_attacks(self, unit, enemy_units):
        atk = Attack(unit, damage=8.0, type=PHYSICAL)
        atk.handlers.append(LifeLeechHandler(unit, 0.3))
        return [atk]

@component        
class BasicShieldDefense(DefenseHandler, DHandlerComponent):
    name = "BasicPhysicalDefense"
    description = "Prevents 10% of physical damage"
    type = DEFENSE
    icon = 53
    def __call__(self, atk, units):
        if atk.type == PHYSICAL:
            atk.damage *= 0.9
        return atk
        
@component        
class EnergyShieldDefense(DefenseHandler, DHandlerComponent):
    name = "EnergyShieldDefense"
    description = "Incoming physical damage is limited to a maximum of 10 (before other reductions)"
    type = DEFENSE
    icon = 24
    def __init__(self):
        self.priority = 0
    def __call__(self, atk, units):
        if atk.type == PHYSICAL and atk.damage > 10:
            atk.damage = 10
        return atk
        
@component        
class SuperHealingDefense(DefenseHandler, DHandlerComponent):
    name = "SuperHealingDefense"
    description = "Incoming physical damage that is less than 5 is completely prevented"
    type = DEFENSE
    icon = 25
    def __init__(self):
        self.priority = 0
    def __call__(self, atk, units):
        if atk.type == PHYSICAL and atk.damage < 5:
            atk.damage = 0
        return atk
        
@component
class ArcaneShieldDefense(DefenseHandler, DHandlerComponent):
    name = "BasicMagicalDefense"
    description = "Reduces all magical damage by 1"
    type = DEFENSE
    icon = 43
    def __call__(self, atk, units):
        if atk.type == MAGICAL:
            atk.damage -= 1
            if atk.damage < 0:
                atk.damage = 0
        return atk
      
class WeakShieldDefense(DefenseHandler, DHandlerComponent):
    def __init__(self, unit):
        self.priority = 2
        self.unit = unit
    def __call__(self, atk, units):
        if atk.type == PHYSICAL:
            atk.damage *= 0.92
        return atk
        
@component
class GroupShieldDefense(DefenseHandler, DHandlerComponent):
    name = "GroupShield"
    description = "Reduces physical damage to all allied units by 8% (after reductions)"
    type = DEFENSE
    icon = 239
    def __call__(self, atk, units):
        return atk
    def finalize(self):
        self.handlers = []
        for u in self.unit.owner.units:
            h = WeakShieldDefense(u)
            u.add_defense_handler(h)
            self.handlers.append(h)
    def die(self):
        for h in self.handlers:
            h.unit.defense_handlers.remove(h)
            
class WeakDamageBoost(DefenseHandler):
    def __init__(self, unit):
        self.priority = 2
        self.unit = unit
    def __call__(self, atk, units):
        if atk.type == PHYSICAL:
            atk.damage += 3.0
        return atk
        
@component
class GroupBuff(Ability, AbilityComponent):
    name = "GroupBuff"
    description = "Adds 3 damage to all physical attacks of allies (before other modifiers), attacks for 5 physical damage (+3 bonus) itself"
    type = ATTACK
    icon = 202
    def get_attacks(self, unit, enemy_units):
        return [Attack(unit, damage=5.0, type=PHYSICAL)]
    def finalize(self):
        self.handlers = []
        for u in self.unit.owner.units:
            h = WeakDamageBoost(u)
            u.add_attack_handler(h)
            self.handlers.append(h)
    def die(self):
        for h in self.handlers:
            h.unit.attack_handlers.remove(h)
            
class BeastDamageBoost(AttackHandler):
    def __init__(self, unit):
        self.priority = 2
        self.unit = unit
    def __call__(self, atk, units):
        if atk.type == PHYSICAL and atk.source.has_trait(BEAST):
            atk.damage *= 1.5
        return atk
            
@component
class BeastMaster(DefenseHandler, DHandlerComponent):
    name = "BeastMaster"
    description = "Increases phyiscal damage of all your beasts by 50%; This unit takes 50% less physical damage from beasts"
    type = SPECIAL
    icon = 199
    def __call__(self, atk, units):
        if atk.source.has_trait(BEAST) and atk.type == PHYSICAL:
            atk.damage *= 0.5
        return atk
    def finalize(self):
        self.handlers = []
        for u in self.unit.owner.units:
            h = BeastDamageBoost(u)
            u.add_attack_handler(h)
            self.handlers.append(h)
    def die(self):
        for h in self.handlers:
            h.unit.attack_handlers.remove(h)

        
@component 
class DoubleHealthSpecial(Component):
    name = "DoubleHealth"
    description = "Doubles the unit's health"
    type = SPECIAL
    icon = 217
    def apply(self, unit):
        unit.health *= 2
        unit.max_health *= 2
        
@component
class AchillesSpecial(DefenseHandler, DHandlerComponent):
    name = "Achilles"
    description = "Unit starts with 1 health, but has a 97% chance to avoid all physical and magical damage"
    type = SPECIAL
    icon = 211
    def apply(self, unit):
        unit.health = 1
        unit.max_health = 1
        unit.add_defense_handler(self)
    def __call__(self, atk, units):
        if atk.type in [PHYSICAL, MAGICAL] and random.random() < 0.97:
            atk.damage = 0
        return atk
        
@component
class ZeusSpecial(AttackHandler, AHandlerComponent):
    name = "Zeus"
    description = "Magical attacks have a 10% chance to turn into a chain lightning, affecting all enemy units"
    type = SPECIAL
    icon = 286
    def __init__(self):
        self.priority = 1000
    def __call__(self, atk, units):
        if atk.type == MAGICAL and random.random() < 0.1:
            result = []
            for u in units:
                a1 = atk.clone()
                a1.target = u
                result.append(a1)
            return result
        return atk
        
@component
class CerberusSpecial(AttackHandler, AHandlerComponent):
    name = "Cerberus"
    description = "All physical attacks attack 2 additional random enemies for 25% physical damage each (primary target may be hit again)"
    type = SPECIAL
    icon = 219
    def __init__(self):
        self.priority = 100
    def __call__(self, atk, units):
        if atk.type == PHYSICAL:
            result = [atk]
            a1 = atk.clone()
            a1.target = random.choice(units)
            a1.damage *= 0.25
            result.append(a1)
            a1 = atk.clone()
            a1.target = random.choice(units)
            a1.damage *= 0.25
            result.append(a1)
            return result
        return atk

@component 
class DoubleAttackSpecial(AttackHandler, AHandlerComponent):
    name = "DoubleAttack"
    description = "Doubles the unit's attacks (happens before target selection)"
    type = SPECIAL
    icon = 197
    def __init__(self):
        self.priority = -10
    def __call__(self, atk, units):
        return [atk.clone(), atk.clone()]
        
@component 
class DoubleDamageSpecial(AttackHandler, AHandlerComponent):
    name = "DoubleDamage"
    description = "Doubles any attack damage (after all other attack modifiers)"
    type = SPECIAL
    icon = 203
    def __init__(self):
        self.priority = 10000
    def __call__(self, atk, units):
        atk.damage *= 2
        return atk
        
class CurseBuff(Buff): 
    name = "Cursed"
    description = "Unit takes %count more damage from each attack"
    icon = 219
    def __init__(self):
        self.count = 1
        
class Curse(DefenseHandler):
    def __init__(self):
        self.priority = -10
    def __call__(self, atk, units):
        atk.damage += 1.0
        return atk
        
@component 
class CurseSpecial(AttackHandler, AHandlerComponent):
    name = "Curse"
    description = "Each attack curses the target to take 1.0 more damage from all subsequent attacks (before reductions, stacks with itself)"
    type = SPECIAL
    icon = 219
    def __init__(self):
        self.priority = 10
    def __call__(self, atk, units):
        atk.target.add_defense_handler(Curse())
        atk.target.add_buff(CurseBuff())
        atk.damage -= 1.0
        return atk
        
class EnergyStorage(AttackHandler):
    def __init__(self):
        self.priority = 100
        self.value = 0.0
    def __call__(self, atk, targets):
        if atk.type in [PHYSICAL, MAGICAL]:
            self.value += atk.damage
            atk.source.add_buff(EnergyContainerBuff(atk.damage))
            atk.damage = 0
        return atk
        
class EnergyContainerBuff(Buff):
    name = "EnergyContainer"
    description = "When this unit is destroyed, it deals damage equal to the amount stored to all enemy units"
    icon = 251
        
@component 
class EnergyContainerSpecial(AttackHandler, AHandlerComponent):
    name = "EnergyContainer"
    description = "Each outgoing physical and magical attack's damage is stored in the container instead of being dealt to the target. If this unit is destroyed, the energy is released and dealt as magical damage to all enemy units"
    type = SPECIAL
    icon = 251
    def __init__(self):
        self.priority = 1000
        self.exploded = False
    def apply(self, unit):
        unit.add_defense_handler(self)
        self.storage = EnergyStorage()
        unit.add_attack_handler(self.storage)
        self.unit = unit
    def __call__(self, atk, units):
        if atk.damage > self.unit.health and self.unit.health > 0 and not self.exploded:
            self.exploded = True
            for u in self.unit.owner.enemy_units:
                atk1 = Attack(self.unit, self.storage.value, MAGICAL)
                atk1.target = u
                u.be_attacked(atk1, None)
        return atk
        
@component 
class ThornsSpecial(DefenseHandler, DHandlerComponent):
    name = "Thorns"
    description = "20% of all physical damage taken by this unit is reflected back on the attacker"
    type = SPECIAL
    icon = 44
    def __init__(self):
        self.priority = 1000
    def __call__(self, atk, units):
        if atk.type == PHYSICAL and atk.target:
            atk1 = Attack(self.unit, 0.2*atk.damage, MAGICAL)
            atk1.target = atk.source
            atk.source.be_attacked(atk1, None)
        return atk
        
@component
class LuckyArcaneShieldDefense(DefenseHandler, DHandlerComponent):
    name = "LuckyMagicalDefense"
    description = "Has an 11% chance to prevent damage of any magical attacks"
    type = DEFENSE
    icon = 15
    def __call__(self, atk, units):
        if atk.type == MAGICAL and random.random() < 0.11:
            atk.damage = 0
        return atk
        
@component 
class Purifier(AttackHandler, AHandlerComponent):
    name = "Purifier"
    description = "All physical and magical damage dealt by this unit is converted to pure damage"
    type = SPECIAL
    icon = 273
    def __init__(self):
        self.priority = 1000
    def __call__(self, atk, units):
        if atk.type == PHYSICAL or atk.type == MAGICAL:
            atk.type = PURE
        return atk

@component
class ConsoleLogDefense(DefenseHandler, DHandlerComponent):
    name = "ConsoleLog"
    description = "Logs damage events to the console"
    type = DEBUG
    icon = 0
    def __init__(self):
        self.priority = -1000
    def __call__(self, atk, units):
        if atk.target:
            print atk.target.owner.name, atk.target.name, "takes", atk.damage, "(%.2f -> %.2f)"%(atk.target.health, atk.target.health - atk.damage), "by", atk.source.owner.name, atk.source.name
        return atk
        
UNDEAD = 1
BEAST = 2
HUMAN = 4
WIZARD = 8

@component
class SkeletonTrait(DefenseHandler, DHandlerComponent): 
    name = "SkeletonTrait"
    description = "If unit would die from physical damage, there is a 20% chance it will be restored to 30% health instead; Unit is undead"
    type = TRAIT
    icon = 42
    def __init__(self):
        self.priority = 100
    def apply(self, unit):
        self.unit = unit
        self.unit.add_defense_handler(self)
        self.unit.traits.append(UNDEAD)
    def __call__(self, atk, units):
        if atk.type == PHYSICAL and atk.damage > self.unit.health:
            r = random.random()
            if r < 0.2:
                atk.damage = 0
                self.unit.health = 0.3 * self.unit.max_health
        return atk
        
class ZombifyHandler(DamageHandler):
    def __call__(self, atk):
        if atk.type == PHYSICAL and atk.damage > 0 and not atk.target.has_trait(UNDEAD):
            atk.target.traits.append(UNDEAD)
        
@component
class ZombieTrait(AttackHandler, AHandlerComponent): 
    name = "ZombieTrait"
    description = "If unit deals physical damage to another unit, that unit will become undead; Unit is undead"
    type = TRAIT
    icon = 218
    def __init__(self):
        self.priority = 100
    def apply(self, unit):
        self.unit = unit
        self.unit.add_attack_handler(self)
        self.unit.traits.append(UNDEAD)
    def __call__(self, atk, units):
        if atk.type == PHYSICAL:
            atk.add_handler(ZombifyHandler)
        return atk
        
@component
class SavageBeastTrait(AttackHandler, AHandlerComponent): 
    name = "SavageBeastTrait"
    description = "Unit deals 20% extra physical damage to units under 30%; Unit is a beast"
    type = TRAIT
    icon = 360
    def __init__(self):
        self.priority = 1000
    def apply(self, unit):
        self.unit = unit
        self.unit.add_defense_handler(self)
        self.unit.traits.append(BEAST)
    def __call__(self, atk, units):
        if atk.type == PHYSICAL and atk.target.health < 0.3 *atk.target.max_health:
            atk.damage *= 1.2
        return atk
        
@component
class HunterTrait(AttackHandler, AHandlerComponent): 
    name = "HunterTrait"
    description = "Physical damage dealt by this unit is increased by 1 for each beast the enemy has; Unit is a human"
    type = TRAIT
    icon = 325
    def __init__(self):
        self.priority = 1000
    def apply(self, unit):
        self.unit = unit
        self.unit.add_defense_handler(self)
        self.unit.traits.append(HUMAN)
    def __call__(self, atk, units):
        if atk.type == PHYSICAL:
            for u in units:
                if u.has_trait(BEAST):
                    atk.damage += 1
        return atk
        
@component
class WarlockTrait(AttackHandler, AHandlerComponent): 
    name = "WarlockTrait"
    description = "Magical damage dealt to undead unit heals this unit for 75% of the damage dealt; Unit is a human wizard"
    type = TRAIT
    icon = 325
    def __init__(self):
        self.priority = 100
    def apply(self, unit):
        self.unit = unit
        self.unit.add_defense_handler(self)
        self.unit.traits.append(HUMAN)
        self.unit.traits.append(WIZARD)
    def __call__(self, atk, units):
        if atk.type == MAGICAL and atk.target.has_trait(UNDEAD):
            atk.handlers.append(LifeLeechHandler(self.unit, 0.75))
        return atk

@component
class TameBeastTrait(StartTurnHandler, SHandlerComponent): 
    name = "TameBeastTrait"
    description = "Unit heals 3 health at the start of every turn; Unit is a beast"
    type = TRAIT
    icon = 262
    def apply(self, unit):
        self.unit = unit
        self.unit.add_defense_handler(self)
        self.unit.traits.append(BEAST)
    def __call__(self, unit, enemy_units):
        unit.health += 3.0
        unit.health = min(unit.health, unit.max_health)

def make_component(name):
    return components[name]()

def make_unit(owner, name, comps, index=None, mk_component=make_component):
    u = Unit(owner, name)
    compobjs = []
    for c in comps:
        comp = mk_component(c)
        compobjs.append((c,comp))
    # small hack to make sure specials are applied last (to make DoubleHealth work with bodies)
    compobjs.sort(key=lambda (_,c): c.type)
    for (c,comp) in compobjs:
        comp.apply(u)
        u.components.append(c)
    u.components.sort(key=lambda c: components[c].type)
    if index is not None:
        u.index = index
    return u
    
def make_player(fname, name, mk_component=make_component, is_human=False):
    p = Player(name, is_human)
    f = open(fname, "r")
    for l in f:
        if l.strip():
            tokens = map(lambda s: s.strip(), l.split())
            index = None
            comps = tokens[1:]
            try:
                index = int(tokens[1])
                comps = tokens[2:]
            except Exception:
                pass
            make_unit(p, tokens[0], comps, index=index, mk_component=mk_component)
    p.finalize()
    return p
    
def make_player_from_team(team, name, mk_component=make_component, is_human=False):
    p = Player(name, is_human)
    for tokens in team:
        index = None
        comps = tokens[1:]
        try:
            index = int(tokens[1])
            comps = tokens[2:]
        except Exception:
            pass
        make_unit(p, tokens[0], comps, index=index, mk_component=mk_component)
    p.finalize()
    return p

def game(teams, mk_player=make_player):
    players = []
    for i, fname in enumerate(teams):
        p = mk_player(fname, "player %d"%(i+1))
        players.append(p)
        
    g = Game(players)
    winner = g.run()
    return winner

def main(files):
    winrates = {}
    if not files:
        files = ["team1.skv", "team1.skv"]
    for i in xrange(1000):
        winner = game(files)
        if winner not in winrates:
            winrates[winner] = 0
        winrates[winner] += 1
    total = sum(winrates.values())
    for w in winrates:
        if w is not None:
            print "player", w+1, ": ", (100.0*winrates[w])/total
        else:
            print "draw: ", (100.0*winrates[w])/total

import sys
        
if __name__ == "__main__":
    main(sys.argv[1:])
    
