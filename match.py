class MatchList():

    @classmethod
    def createMatchListForTeam(cls, teamName):
        pass

    @classmethod
    def createMatchListForLeague(cls, leagueId):
        pass

    def __init__(self, matchIds):
        self._matches = {}
        self._teams = None
        for id in matchIds:
            self._matches[id] = "Match_{}".format(id)
    
    def __str__(self):
        return "{}".format(self._matches.keys())

    def getMatchIds(self):
        return sorted(self._matches.keys())

    def getAllTeams(self):
        if self._teams is None:
            self._teams = []
            for match in self._matches.items():
                self._teams.append(match.homeTeam)
        return self._teams


class MatchListLite(MatchList):

    def __init__(self, matchIds):
        self._matches = matchIds

    def getMatchIds(self):
        return sorted(self._matches)

    def getAllTeams(self):
        return []
