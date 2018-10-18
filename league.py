from match import MatchList, MatchListLite

from variables import MATCH_IDS

class LeagueList():

    def __init__(self, leagueDict):
        self._leagues = {}
        for league in leagueDict:
            self._leagues[league] = League(league, leagueDict[league]['name'], leagueDict[league]['matches'])

    def getLeagueByName(self, leagueName):
        for league in self._leagues.items():
            if league.name == leagueName:
                return league
        return None

    def getLeagueById(self, leagueId):
        if leagueId in self._leagues.keys():
            return self._leagues[leagueId]
        else:
            return None

class League():

    def __init__(self, id, name, matchIdDict=None, initMatches=False):
        self.id = id
        self.name = name
        self._matchesLoaded = False
        self._matches = {}
        if matchIdDict is None:
            matchIdDict = MATCH_IDS[self.id]['matchIds']
        self.loadMatches(matchIdDict, initMatches)

    def loadMatches(self, matchIdDict, full=False):
        if full:
            matchListClass = MatchList
        else:
            matchListClass = MatchListLite
        
        for season in matchIdDict:
            self._matches[season] = matchListClass(matchIdDict[season])

    def _getSeasonList(self, season=None):
        if season:
            return [season]
        else:
            return self._matches.keys()
    
    def getMatchIds(self, season=None):
        seasons = self._getSeasonList(season)
        matchIdList = []
        for season in seasons:
            matchIdList.extend(self._matches[season].getMatchIds())
        return matchIdList

    def containsTeam(self, team, season=None):
        seasons = self._getSeasonList(season)
        teams = []
        for season in seasons:
            teams.extend(self._matches[season].getAllTeams())
        return team in teams
