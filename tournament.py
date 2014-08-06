import engine
import os
import sys
import random

def order_teams(teams, last_winner):
    if not last_winner:
        random.shuffle(teams)
        return teams
    if last_winner == teams[0]:
        return [teams[1], teams[0]]
    return teams

def makefname(t):
    return os.path.join(sys.argv[1], t)    
    
def match(team1, team2):
    score = [0,0,0]
    last_winner = None
    while score[0] < 3 and score[1] < 3 and score[2] < 10:
        teams = order_teams([team1, team2], last_winner)
        try:
            winner = engine.game(map(makefname, teams))
        except Exception:
            import traceback
            traceback.print_exc()
            print team1, team2
            sys.exit(-1)
        if winner:
            last_winner = teams[winner]
            if teams[winner] == team1:
                score[0] += 1
            else:
                score[1] += 1
        else:
            last_winner = None
            score[2] += 1
    print team1, "vs.", team2, "%d - %d - %d"%(score[0], score[1], score[2])
    if score[0] > score[1]:
        return team1
    if score[1] > score[2]:
        return team2
    return random.choice([team1, team2])
        
            

def round(teams):
    random.shuffle(teams)
    newteams = []
    at = 0
    for i in xrange(len(teams)/2):
        winner = match(teams[at], teams[at+1])
        print winner, "won"
        newteams.append(winner)
        at += 2
    if at < len(teams) -1:
        newteams.append(teams[-1])
    return newteams

def main(d):
    teams = []
    for f in os.listdir(d):
        if f.endswith('.skv'):
            teams.append(f)
    i = 1
    while len(teams) > 1:
        print 'round', i
        teams = round(teams)
        i += 1
        
if __name__ == '__main__':
    main(sys.argv[1])