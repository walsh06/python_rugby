from rugbydb import RugbyDB, CachedDB

class MatchList():

    @classmethod
    def createMatchListForTeam(cls, teamName, leagues=None, seasons=None):
        db = CachedDB()
        matchIds = db.getMatchesForTeam(teamName.lower(), leagues=leagues, seasons=seasons)
        return cls(matchIds)

    @classmethod
    def createMatchListForLeague(cls, leagueId):
        pass

    def __init__(self, matchIds):
        self._matches = {}
        self._teams = None
        db = CachedDB()
        for id in matchIds:
            self._matches[id] = Match.fromMatchDict(db.getMatchById(id))
    
    def __str__(self):
        return "{}".format(self._matches.keys())

    def __len__(self):
        return len(self._matches.keys())

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
        self._matches = {el: None for el in matchIds}

    def getAllTeams(self):
        return []


class Match():

    @classmethod
    def fromMatchDict(cls, matchDict):
        return cls(matchDict['gamePackage']['gameStrip']['teams']['home'], 
                  matchDict['gamePackage']['gameStrip']['teams']['away'],
                  matchDict['gamePackage']['gameStrip']['isoDate'],
                  matchDict['gamePackage']['matchStats']['dataVis'],
                  matchDict['gamePackage']['matchStats']['table'],
                  matchDict['gamePackage']['matchEvents']['col'][0][0]['data'],
                  matchDict['gamePackage']['matchEvents']['col'][1][1]['data'],
                  matchDict['gamePackage']['matchDiscipline']['col'][1][0]['data'],
                  matchDict['gamePackage']['matchDiscipline']['col'][0][0]['data'],
                  matchDict['gamePackage']['matchLineUp'])

    def __init__(self, homeTeam, awayTeam, date, dataVis, table, scores, attacking, disicpline, penalties, players):
        self.date = "{} {}".format(date[:10], date[11:-1])

        self.homeTeam = {'name': homeTeam['name'], 'abbrev': homeTeam['abbrev'], 'score': homeTeam['score']}
        self.awayTeam = {'name': awayTeam['name'], 'abbrev': awayTeam['abbrev'], 'score': awayTeam['score']}
        self.matchStats = {'Points': {'homeValue': homeTeam['score'], 'awayValue': awayTeam['score']}}

        for item in dataVis + table + disicpline + scores + attacking:
            self.matchStats[item['text']] = {'homeValue': item['homeValue'], 'awayValue': item['awayValue']}
        self.matchStats['Penalties Conceded'] = {'homeValue': penalties['homeTotal'], 'awayValue': penalties['awayTotal']}
        self.players = {'home': [], 'away': []}
        for team in self.players.keys():
            pass
            # for player in players[team]['team']:
            #     self.players[team].append(Player.fromPlayerDict(player))
    
    def __str__(self):
        return "{} v {} - {}".format(self.homeTeam['name'], self.awayTeam['name'], self.date)

    def getAllStatHeaders(self):
        return self.matchStats.keys()