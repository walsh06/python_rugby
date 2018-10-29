from match import MatchList
from league import League

def getAveragePointsScored(team, seasons=None):
    """
    Get average points scored by a team, limit it by season
    ARGS:
        team (str) - team name
        seasons (str) - season string to limit search, None is all seasons
    RETURNS:
        float - average points scored
    """
    return getAverageStatForTeam('points', team, seasons)


def getAverageStatForTeam(stat, team, seasons=None):
    """
    Get average of a stat for a team, limit it by season
    ARGS:
        stat (str) - name of stat to search for
        team (str) - team name
        seasons (str) - season string to limit search, None is all seasons
    RETURNS:
        float - average of stats
    """
    matchList = MatchList.createMatchListForTeam(team, seasons=seasons)
    statTotal = 0
    matches = 0
    for match in matchList:
        statTotal += match.getStatForTeam(team, stat)
        matches += 1
    return float(statTotal)/float(matches)


def getPlayerStatInMatches(matchList, stat):
    """
    Get a list of all players in the list of matches and their total for the stat
    in each match
    ARGS:
        matchList (MatchList) - list of matches to search
        stat (str) - name of the stat to get for each player
    RETURNS:
        [(str, str, float),] - list of tuples sorted by value, in the form (playerName, teamName, statValue)
    """
    playerStats = []
    for match in matchList:
        for team in match.players.keys():
            for player in match.players[team]:
                playerStats.append((player.name, team, player.getStat(stat)))
    return sorted(playerStats, key=lambda tup: tup[2], reverse=True)


def getTeamStatInMatches(matchList, stat):
    """
    Get a list of all teams in the list of matches and their total for the stat
    in each match
    ARGS:
        matchList (MatchList) - list of matches to search
        stat (str) - name of the stat to get for each player
    RETURNS:
        [(str, float),] - list of tuples sorted by value, in the form (teamName, statValue)
    """
    teamStats = []
    for match in matchList:
        for team in match.players.keys():
            teamStats.append((team, match.getStatForTeam(team,stat)))
    return sorted(teamStats, key=lambda tup: tup[1], reverse=True)

def getLeagueLeadersForStatTotal(leagueName, season, stat):
    """
    Get the league leaders for a given stat in a season
    ARGS:
        leagueName (str) - name of the league
        season (str) - seasons string to search
        stat (str) - stat name to get leaders for
    RETURNS:
        [(str, str, float),] - list of tuples sorted by value, in the form (playerName, teamName, statValue)
    """
    leagueLeadersDict = {}
    league = League.fromLeagueName(leagueName)
    if league is not None:
        seasonMatchList = league._matches[season]
        for match in seasonMatchList:
            for team in match.players.keys():
                for player in match.players[team]:
                    if player.id in leagueLeadersDict:
                        leagueLeadersDict[player.id][2] += player.getStat(stat)
                    else:
                        leagueLeadersDict[player.id] = [player.name, team, player.getStat(stat)]
    return sorted(leagueLeadersDict.values(), key=lambda tup: tup[2], reverse=True)
    

