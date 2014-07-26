

PHYSICAL = 1
MAGICAL = 2
PURE = 3

class Handler(object):
    def __init__(self, priority=1):
        self.priority = priority
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
        
class Component(object):
    icon = 0
    def __init__(self):
        pass
    def apply(self, unit):
        pass
        
class AHandlerComponent(object):
    def apply(self, unit):
        unit.add_attack_handler(self)
        self.unit = unit
        
class DHandlerComponent(object):
    def apply(self, unit):
        unit.add_defense_handler(self)
        self.unit = unit
        
class DamageHandler(object):
    def __call__(self, atk):
        pass
    
class Attack(object):
    def __init__(self, source, damage=0, type=PHYSICAL):
        self.source = source
        self.damage = damage
        self.target = None
        self.type = type
        self.handlers = []
    def do_damage(self):
        for h in self.handlers:
            h(self)
        if self.target and self.target.health > 0:
            self.target.health -= self.damage
            if self.target.health <= 0:
                self.target.die()
    def clone(self):
        result = Attack(self.source, self.damage, self.type)
        result.target = self.target
        result.handlers = self.handlers[:]
        return result
    
class Unit(object):
    def __init__(self, owner, name="unit", health=100.0):
        self.attack_handlers = []
        self.defense_handlers = []
        self.health = health
        self.max_health = health
        self.owner = owner
        self.name = name
        self.owner.units.append(self)
        self.components = []
    def get_attack(self, targets):
        atks = [Attack(self)]
        for h in self.attack_handlers:
            newatks = []
            for atk in atks:
                res = h(atk, targets)
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
    def die(self):
        self.owner.units.remove(self)
        for h in self.attack_handlers + self.defense_handlers:
            h.die()
    def finalize(self):
        for h in self.attack_handlers + self.defense_handlers:
            h.finalize()
        
class Player(object):
    def __init__(self, name):
        self.units = []
        self.current_unit = -1
        self.name = name
        self.enemy_units = []
    def make_turn(self, enemy_units):
        if self.units:
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
        for p in self.players:
            if p.units:
                has_units += 1
        return has_units <= 1
    def run(self):
        current_player = 0
        while not self.game_ended() and self.players:
            enemy_units = []
            for i, p in enumerate(self.players):
                if i != current_player:
                    enemy_units.extend(p.units)
            self.players[current_player].make_turn(enemy_units)
            current_player += 1
            current_player %= len(self.players)
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
SPECIAL = 8
DEBUG = 16

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
class BasicPhysicalAttack(AttackHandler, AHandlerComponent):
    name = "BasicPhysicalAttack"
    description = "Does 10 physical damage"
    type = ATTACK
    icon = 395
    def __call__(self, atk, targets):
        atk.damage = 10.0
        atk.type = PHYSICAL
        return atk
        
@component
class BasicMixedAttack(AttackHandler, AHandlerComponent):
    name = "BasicMixedAttack"
    description = "Does 5 physical damage and 5 magical damage (separate damage events)"
    type = ATTACK
    icon = 393
    def __call__(self, atk, targets):
        atk.damage = 5.0
        atk.type = PHYSICAL
        atk2 = atk.clone()
        atk2.type = MAGICAL
        return [atk,atk2]
        
@component
class PhysicalBurstAttack(AttackHandler, AHandlerComponent):
    name = "PhysicalBurstAttack"
    description = "Does 4 bursts of 2,2,2 and 3 physical damage"
    type = ATTACK
    icon = 200
    def __call__(self, atk, targets):
        atk.damage = 2.0
        atk.type = PHYSICAL
        atk2 = atk.clone()
        atk2.damage = 3.0
        return [atk,atk.clone(),atk.clone(),atk2]
        
        
@component
class ImprovingPhysicalAttack(AttackHandler, AHandlerComponent):
    name = "ImprovingPhysicalAttack"
    description = "Does 2 physical attack on the first attack, but doubles damage after every attack"
    type = ATTACK
    icon = 370
    def __init__(self):
        self.priority = 1
        self.dmg = 2.0
    def __call__(self, atk, targets):
        atk.damage = self.dmg
        self.dmg *= 2
        atk.type = PHYSICAL
        return atk
        
@component
class BasicPureAttack(AttackHandler, AHandlerComponent):
    name = "BasicPureAttack"
    description = "Does 8 pure damage"
    type = ATTACK
    icon = 372
    def __call__(self, atk, targets):
        atk.damage = 8.0
        atk.type = PURE
        return atk
        
@component
class BasicMagicalAttack(AttackHandler, AHandlerComponent):
    name = "BasicMagicalAttack"
    description = "Does 10 magical damage"
    type = ATTACK
    icon = 190
    def __call__(self, atk, targets):
        atk.damage = 10.0
        atk.type = MAGICAL
        return atk
        
class LifeLeechHandler(DamageHandler):
    def __init__(self, unit):
        self.unit = unit
    def __call__(self, atk):
        self.unit.health += 0.3*atk.damage
        
        
@component
class LifeLeechPhysicalAttack(AttackHandler, AHandlerComponent):
    name = "LifeLeechPhysicalAttack"
    description = "Does 8 physical damage, and restores health equal to 30% of the resulting damage"
    type = ATTACK
    icon = 267
    def __call__(self, atk, targets):
        atk.damage = 8.0
        atk.type = PHYSICAL
        atk.handlers.append(LifeLeechHandler(self.unit))
        return atk

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
            atk.damage *= 0.9
        return atk
        
@component
class GroupShieldDefense(DefenseHandler, DHandlerComponent):
    name = "GroupShield"
    description = "Reduces physical damage to all allied units by 8% (after reductions)"
    type = DEFENSE
    icon = 44
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
            
class WeakDamageBoost(DefenseHandler, DHandlerComponent):
    def __init__(self, unit):
        self.priority = 2
        self.unit = unit
    def __call__(self, atk, units):
        if atk.type == PHYSICAL:
            atk.damage += 3.0
        return atk
        
@component
class GroupBuff(AttackHandler, AHandlerComponent):
    name = "GroupBuff"
    description = "Adds 3 damage to all physical attacks of allies (before other modifiers), attacks for 5 physical damage (+3 bonus) itself"
    type = ATTACK
    icon = 202
    def __call__(self, atk, units):
        atk.damage = 5
        atk.type = PHYSICAL
        return atk
    def finalize(self):
        self.handlers = []
        for u in self.unit.owner.units:
            h = WeakDamageBoost(u)
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
        unit.add_defense_handler(self)
    def __call__(self, atk, units):
        if atk.type in [PHYSICAL, MAGICAL] and random.random() < 0.97:
            atk.damage = 0
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
        self.priority = 100
    def __call__(self, atk, units):
        atk.damage *= 2
        return atk
        
class Curse(DefenseHandler):
    def __init__(self):
        self.priority = -10
    def __call__(self, atk, units):
        atk.damage += 2.0
        return atk
        
@component 
class CurseSpecial(AttackHandler, AHandlerComponent):
    name = "Curse"
    description = "Each attack curses the target to take 2.0 more damage from all subsequent attacks (before reductions, stacks with itself)"
    type = SPECIAL
    icon = 219
    def __init__(self):
        self.priority = 10
    def __call__(self, atk, units):
        atk.target.add_defense_handler(Curse())
        atk.damage -= 2.0
        return atk
        
class EnergyStorage(AttackHandler):
    def __init__(self):
        self.priority = 100
        self.value = 0.0
    def __call__(self, atk, targets):
        if atk.type in [PHYSICAL, MAGICAL]:
            self.value += atk.damage
            atk.damage = 0
        return atk
        
@component 
class EnergyContainerSpecial(AttackHandler, AHandlerComponent):
    name = "EnergyContainer"
    description = "Each outgoing physical and magical attack's damage is stored in the container instead of being dealt to the target. If this unit is destroyed, the energy is released and dealt as magical damage to all enemy units"
    type = SPECIAL
    icon = 251
    def __init__(self):
        self.priority = 1000
    def apply(self, unit):
        unit.add_defense_handler(self)
        self.storage = EnergyStorage()
        unit.add_attack_handler(self.storage)
        self.unit = unit
    def __call__(self, atk, units):
        if atk.damage > self.unit.health and self.unit.health > 0:
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
            atk1 = Attack(self.unit, 0.2*atk.damage, PHYSICAL)
            atk1.target = atk.source
            atk.source.be_attacked(atk1, None)
        return atk
        
@component
class LuckyArcaneShieldDefense(DefenseHandler, DHandlerComponent):
    name = "LuckyMagicalDefense"
    description = "Randomly prevents all damage of 11% of magical attacks"
    type = DEFENSE
    icon = 15
    def __call__(self, atk, units):
        if atk.type == MAGICAL and random.random() < 0.11:
            atk.damage = 0
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

def make_component(name):
    return components[name]()
        
def make_unit(owner, name, comps, index=None, mk_component=make_component):
    u = Unit(owner, name)
    for c in comps:
        comp = mk_component(c)
        comp.apply(u)
        u.components.append(c)
    u.components.sort(key=lambda c: components[c].type)
    if index is not None:
        u.index = index
    return u
    
def make_player(fname, name, mk_component=make_component):
    p = Player(name)
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


def main(files):
    winrates = {}
    if not files:
        files = ["team1.skv", "team1.skv"]
    for i in xrange(1000):
        players = []
        for i, fname in enumerate(files):
            p = make_player(fname, "player %d"%(i+1))
            players.append(p)
            
        g = Game(players)
        winner = g.run()
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
    
