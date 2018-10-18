class MatchList():

    @classmethod
    def createMatchListForTeam(cls, teamName):
        pass

    @classmethod
    def createMatchListForLeague(cls, leagueId):
        pass

    def __init__(self, matchIds):
        self._matches = {}
        for id in matchIds:
            self._matches[id] = "Match_{}".format(id)
    
    def __str__(self):
        return "{}".format(self._matches.keys())
