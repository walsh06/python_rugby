from match import MatchList

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

    def __init__(self, id, name, matchIdDict, initMatches=False):
        self.id = id
        self.name = name
        self.matchIds = matchIdDict
        self._matchesLoaded = False
        self.teams = []
        if initMatches:
            self.loadMatches()
        else:
            self.matches = None
            

    def getMatchIds(self, season=None):
        if season:
            matchIdList = self.matchIds[season]
        else:
            matchIdList = []
            for season in self.matchIds.keys():
                matchIdList.extend(self.matchIds[season])
        return matchIdList

    def loadMatches(self):
        self.matches = MatchList(self.getMatchIds())

    def containsTeam(self, team):
        return team in self.teams
