import requests
import json
import glicko2
from matplotlib import pyplot as plt

SCHEDULEURL = 'https://api.overwatchleague.com/schedule'
TEAMSURL = 'https://api.overwatchleague.com/teams'


def eval_match(match, teams):
    winner = match['winner']['name']
    competitors = [c['name'] for c in match['competitors']]
    competitors.remove(winner)
    loser = competitors[0]
    teams[winner]['last_matches'][0].append(teams[loser]['glicko2'].rating)
    teams[winner]['last_matches'][1].append(teams[loser]['glicko2'].rd)
    teams[winner]['last_matches'][2].append(1)
    teams[loser]['last_matches'][0].append(teams[winner]['glicko2'].rating)
    teams[loser]['last_matches'][1].append(teams[winner]['glicko2'].rd)
    teams[loser]['last_matches'][2].append(0)
    return(teams)


def update_teams(teams):
    for name, team in teams.items():
        if not team['last_matches'][0]:  # check if empty
            team['glicko2'].did_not_compete()
        else:
            team['glicko2'].update_player(*team['last_matches'])
        team['rating_hist'].append(team['glicko2'].rating)
        team['rd_hist'].append(team['glicko2'].rd)
        team['last_matches'] = ([], [], [])  # reset last_matches
    return(teams)


def eval_matchlist(matchlist, teams):
    # check if any matches in list concluded
    if matchlist[0]['status'] != 'CONCLUDED':
        return(teams, True)
    current_week = False
    for match in matchlist:
        if match['status'] != 'CONCLUDED':
            current_week = True
            break
        teams = eval_match(match, teams)
    teams = update_teams(teams)
    return(teams, current_week)


def evaluate_schedule(data, teams):
    for stage in data['stages']:
        if stage['slug'] == 'all-star':  # skip all-star matches
            continue
        # open play
        for week in stage['weeks']:
            teams, current_week = eval_matchlist(week['matches'], teams)
            if current_week:
                return(teams)
        # stage playoffs
        teams, current_week = eval_matchlist(stage['matches'][-7:], teams)
        if current_week:
            return(teams)
    return(teams)

# create teams dict
teams_resp = requests.get(TEAMSURL)
teams_data = teams_resp.json()
teams = dict()
for competitor in teams_data['competitors']:
    name = competitor['competitor']['name']
    teams[name] = {'glicko2': glicko2.Player(),
                   'last_matches': ([], [], []),  # opponent's rating, opponent's rd, win/loss
                   'rating_hist': [1500, ],
                   'rd_hist': [350, ],
                   'color': '#'+competitor['competitor']['primaryColor']}
# import match data
resp = requests.get(SCHEDULEURL)
data = resp.json()
data = data['data']
# evaluate all played matches of season 2 so far
teams = evaluate_schedule(data, teams)
# plot ratings for each weak
names = sorted(teams, key=lambda x: teams[x]['glicko2'].rating, reverse=True)
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111)
for name in names:
    plotlist = teams[name]['rating_hist']
    ax.plot(plotlist, '.-', color=teams[name]['color'], label=name)
ax.set(xlim=(-0.1, len(plotlist)*1.3))
ax.legend()
ax.set(ylabel='rating', xlabel='week')
fig.tight_layout()
plt.show()
# plot latest rating and rd as errorbar
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111)
for i, name in enumerate(names):
    ax.errorbar(i, teams[name]['glicko2'].rating,
                yerr=teams[name]['glicko2'].rd,
                color=teams[name]['color'], fmt='o', label=name)
ax.set_xticks([])
ax.set(xlim=(-1, len(names)+6), ylabel='rating')
ax.legend()
fig.tight_layout()
plt.show()
# write latest result to text file
with open('latest_ratings.txt', 'w') as f:
    f.write('Team rating RD\n')
    for name in names:
        f.write('{} {} {}\n'.format(name, teams[name]['glicko2'].rating, teams[name]['glicko2'].rd))