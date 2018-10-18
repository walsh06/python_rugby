from matchlist import MatchList

class LeagueList():

    def __init__(self):
        leagues = {}

    def getLeague(self, leagueName):
        pass


class League():

    def __init__(self, id, name, matchIdDict, loadMatches=False):
        self.id = id
        self.name = name
        self.matchIds = matchIdDict
        if loadMatches:
            self.matches = MatchList(self.getMatchIds())

    def getMatchIds(self, season=None):
        if season:
            matchIdList = self.matchIds[season]
        else:
            matchIdList = []
            for season in self.matchIds.keys():
                matchIdList.extend(self.matchIds[season])
        return matchIdList
