import engine
import random
import sys

def order_teams(teams, last_winner):
    if not last_winner:
        random.shuffle(teams)
        return teams
    if last_winner == teams[0][0]:
        return [teams[1], teams[0]]
    return teams
    
MAX_ITER = 100

def winrate(team1, team2):
    score = [0,0,0]
    last_winner = None
    i = 0
    teams = [team1,team2]
    while i < MAX_ITER:
        i += 1
        try:
            winner = engine.game(map(lambda (name,team): team, teams), mk_player=engine.make_player_from_team)
        except Exception:
            import traceback
            traceback.print_exc()
            print team1, team2
            sys.exit(-1)
        if winner is not None:
            last_winner = teams[winner][0]
            if teams[winner][0] == team1[0]:
                score[0] += 1
            else:
                score[1] += 1
        else:
            last_winner = None
            score[2] += 1
    return score[0]*1.0/MAX_ITER
    
def make_random_team(inventory=None, cnt=5):
    if not inventory:
        inventory = {}
        for c in engine.components:
            inventory[c] = -1
    inventory = inventory.copy()
    result = []
    
    for i in xrange(cnt):
        unit = ['unit%d'%i, random.randint(1,30)]
        for t in [engine.SELECTOR, engine.ATTACK, engine.DEFENSE, engine.SPECIAL]:
            choices = []
            for i in inventory:
                if engine.components[i].type == t and inventory[i] != 0:
                    choices.append(i)
            if choices:
                which = random.choice(choices)
                unit.append(which)
                inventory[which] -= 1
        result.append(unit)
    return result
    
def make_opp_inventory(allowable={}):
    result = {}
    for c in engine.components:
        if engine.components[c].type == engine.SELECTOR:
            result[c] = -1
    result.update({'BasicPhysicalAttack': -1, 'BasicMagicalAttack': -1, 'BasicMagicalDefense': -1, 'BasicPhysicalDefense': -1})
    result.update(allowable)
    return result

    
def make_campaign(initial, progression):
    for i,p in enumerate(progression):
        for j,(item,target_perc,cnt,allowable) in enumerate(p):
            print allowable
            perc = 0.0
            while abs(perc - target_perc) > 0.1:
                pteam = make_random_team(initial)
                oteam = make_random_team(make_opp_inventory(allowable), cnt)
                perc = winrate((0,pteam), (1,oteam))
                print item, perc
            f = open('teams/team_generated_%d_%d.skv'%(i,j), 'w')
            for t in oteam:
                print >>f, ' '.join(map(str,t))
            f.close()
            f = open('levels/level_generated_%d_%d.lvl'%(i,j), 'w')
            print >> f, 'opponent', 'teams/team_generated_%d_%d.skv'%(i,j)
            drops = item + ' 90'
            next = []
            if i < len(progression) - 1:
                drops += ', ' + random.choice(progression[i+1])[0] + ' 9'
                next = ['levels/level_generated_%d_%d.lvl'%(i+1, k) for k in xrange(len(progression[i+1]))]
            if i < len(progression) - 2:
                drops += ', ' + random.choice(progression[i+2])[0] + ' 1'
            print >> f, 'drop', drops
            for n in next:
                print >> f, 'next', n
            print >>f, 'name', item
            f.close()
        for (item,target_perc,cnt,allowable) in p:
            initial[item] = 1
            
initial = make_opp_inventory()

progression = []
componentlevels = {}
f = open('componentlevels.cfg', 'r')
maxlevel = 0
for l in f:
    if l.strip():
        comp, lvl = l.strip().split()
        componentlevels[comp] = int(lvl)
        if int(lvl) > maxlevel:
            maxlevel = int(lvl)
            
def get_comps_at_level(componentlevels, i):
    result = []
    for c in componentlevels:
        if componentlevels[c] == i:
            result.append(c)
    return result
    
def get_comps_upto_level(componentlevels, i):
    result = []
    for c in componentlevels:
        if componentlevels[c] <= i:
            result.append(c)
    return result
    
MAXWINPERC = 0.85
MINWINPERC = 0.5

for i in xrange(maxlevel+1):
    comps = get_comps_at_level(componentlevels, i)
    prog = []
    for c in comps:
        ocomps = get_comps_upto_level(componentlevels, i+1)
        allowed = {}
        for c1 in ocomps:
            if componentlevels[c1] > i:
                allowed[c1] = 1
            else:
                allowed[c1] = -1
        wrate = MAXWINPERC - i*(MAXWINPERC-MINWINPERC)/(maxlevel+1) 
        oteam = 5
        p = (c, wrate, oteam, allowed)
        prog.append(p)
    progression.append(prog)


make_campaign(initial, progression)
#     [[('BasicMixedAttack', 0.8, 4, {'BasicMixedAttack': -1, 'BasicPureAttack': -1, 'DoubleHealth': 1})], 
#      [('BasicPureAttack', 0.8, 5, {'BasicMixedAttack': -1, 'BasicPureAttack': -1, 'DoubleHealth': 1})], 
#      [('LifeLeechPhysicalAttack', 0.7, 5, {})]])

