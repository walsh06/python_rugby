from datetime import datetime

import rugby_stats
from league import League
from match import MatchList, Match


# Load up a match, Wales v Scotland Six Nations 2018
wales_v_scotland = Match.from_match_id(291689)
print(wales_v_scotland)
# print out the tries in the match
for tryEvent in wales_v_scotland.match_event_list.get_events_for_type(1):
    print(tryEvent)

# Load the champions cup from the database
champions_cup = League.from_league_name('Champions Cup')

# get matches in the range of dates
# in this example these dates encompass Round 2 matches
start_date = datetime(2018, 10, 18)
end_date = datetime(2018, 10, 22)
round_two_matches = champions_cup.get_matches_in_range(start_date, end_date)

# Get the number of tackles for each player
tackles = rugby_stats.get_players_stats(round_two_matches, 'tackles')
print("\nChampions Cup Round Two Top Tacklers")
for player in tackles[:10]:
    print("Player: {0}, Team: {1}, Tackles: {2}".format(*player))

# Get the leaders across the full champions cup season
league_leaders = rugby_stats.get_league_leaders_for_stat(
    'Champions Cup', '1819', 'tackles',
)
print("\nChampions Cup Top Tacklers")
for player in league_leaders[:10]:
    print("Player: {0}, Team: {1}, Tackles: {2}".format(*player))

# Now lets dig in and grab some information from the data instead of using the premade functions
# With Connor Murray injured we will see who Munster is playing at scrum half instead
munster_matches = MatchList.create_for_team('munster', seasons=['1819'])
scrum_halves = {}
for match in munster_matches:
    # loop through all the players on the munster team
    for player in match.players['munster']:
        # check if the players position in the match is scrumhalf (SH)
        if player.position == "SH":
            if player.name in scrum_halves:
                scrum_halves[player.name] += 1
            else:
                scrum_halves[player.name] = 1
print("\nMunster Starting Scrumhalf")
for scrum_half in scrum_halves:
    print("Player: {}, Starts: {}".format(scrum_half, scrum_halves[scrum_half]))
