from datetime import datetime

import rugby_stats
from league import League
from match import MatchList, Match


# Load up a match, Wales v Scotland Six Nations 2018
WalesVScotland = Match.from_match_id(291689)
print(WalesVScotland)
# print out the tries in the match
for tryEvent in WalesVScotland.matchEventList.get_events_for_type(1):
    print(tryEvent)

# Load the champions cup from the database
championsCup = League.from_league_name('Champions Cup')

# get matches in the range of dates
# in this example these dates encompass Round 2 matches
startDate = datetime(2018, 10, 18)
endDate = datetime(2018, 10, 22)
roundTwoMatches = championsCup.get_matches_in_range(startDate, endDate)

# Get the number of tackles for each player
tackles = rugby_stats.get_players_stats(roundTwoMatches, 'tackles')
print("\nChampions Cup Round Two Top Tacklers")
for player in tackles[:10]:
    print("Player: {0}, Team: {1}, Tackles: {2}".format(*player))

# Get the leaders across the full champions cup season
leagueLeaders = rugby_stats.get_league_leaders_for_stat('Champions Cup', '1819', 'tackles')
print("\nChampions Cup Top Tacklers")
for player in leagueLeaders[:10]:
    print("Player: {0}, Team: {1}, Tackles: {2}".format(*player))

# Now lets dig in and grab some information from the data instead of using the premade functions
# With Connor Murray injured we will see who Munster is playing at scrum half instead
munsterMatches = MatchList.create_for_team('munster', seasons=['1819'])
scrumHalves = {}
for match in munsterMatches:
    # loop through all the players on the munster team
    for player in match.players['munster']:
        # check if the players position in the match is scrumhalf (SH)
        if player.position == "SH":
            if player.name in scrumHalves:
                scrumHalves[player.name] += 1
            else:
                scrumHalves[player.name] = 1
print("\nMunster Starting Scrumhalf")
for scrumHalf in scrumHalves:
    print("Player: {}, Starts: {}".format(scrumHalf, scrumHalves[scrumHalf]))

