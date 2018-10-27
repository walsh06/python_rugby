from datetime import datetime

from league import League
from match import MatchList, Match

import rugby_stats

# Load up a match, Wales v Scotland Six Nations 2018
WalesVScotland = Match.fromMatchId(291689)
print WalesVScotland
# print out the tries in the match
for tryEvent in WalesVScotland.matchEventList.getAllEventsForType(1):
    print tryEvent

# Load the champions cup from the database
championsCup = League.fromLeagueName('Champions Cup')

# get matches in the range of dates
# in this example these dates encompass Round 2 matches
startDate = datetime(2018,10,18)
endDate = datetime(2018,10,22)
roundTwoMatches = championsCup.getMatchesInDateRange(startDate, endDate)

# Get the number of tackles for each player
tackles = rugby_stats.getPlayerStatInMatches(roundTwoMatches, 'tackles')
print "\nChampions Cup Round Two Top Tacklers"
for player in tackles[:10]:
    print "Player: {}, Team: {}, Tackles: {}".format(player[0], player[1], player[2])

# Get the leaders across the full champions cup season
leagueLeaders = rugby_stats.getLeagueLeadersForStatTotal('Champions Cup', '1819', 'tackles')
print "\nChampions Cup Top Tacklers"
for player in leagueLeaders[:10]:
    print "Player: {}, Team: {}, Tackles: {}".format(player[0], player[1], player[2])

# Now lets dig in and grab some information from the data instead of using the premade functions
# With Connor Murray injured we will see who Munster is playing at scrum half instead
munsterMatches = MatchList.createMatchListForTeam('munster', seasons=['1819'])
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
print "\nMunster Starting Scrumhalf"
for scrumHalf in scrumHalves:
    print "Player: {}, Starts: {}".format(scrumHalf, scrumHalves[scrumHalf])

