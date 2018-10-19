from rugbydb import RugbyDB, CachedDB

class MatchList():
    """
    Class to store and manipulate Match objects
    """

    @classmethod
    def createMatchListForTeam(cls, teamName, leagues=None, seasons=None):
        """
        Create a match list for a specific team, filter by league or seasons
        ARGS:
            teamName (str) - name of the team
            leagues ([int]) - list of league ids to filter by, search all leagues if None
            seasons ([str]) - list of seasons to filter by, search all seasons if None
        RETURNS
            MatchList - MatchList object
        """
        db = CachedDB()
        matchIds = db.getMatchesForTeam(teamName.lower(), leagues=leagues, seasons=seasons)
        return cls(matchIds)

    @classmethod
    def createMatchListForLeague(cls, leagueId):
        pass

    def __init__(self, matchIds):
        """
        ARGS:
            matchIds [int] - list of match ids to load into the matchlist
        """
        self._matches = {}
        self._teams = None
        db = CachedDB()
        for id in matchIds:
            self._matches[id] = Match.fromMatchDict(db.getMatchById(id))
    
    def __str__(self):
        """
        String representation of MatchList
        """
        return "{}".format(self._matches.keys())

    def __len__(self):
        """
        Len representation of MatchList
        """
        return len(self._matches.keys())

    def getMatchIds(self):
        """
        Return all match ids in the MatchList
        RETURNS:
            [int] - list of match ids
        """
        return sorted(self._matches.keys())

    def getAllTeams(self):
        """
        Return list of teams that play in the MatchList
        RETURNS:
            [str] - list of team names
        """
        if self._teams is None:
            self._teams = []
            for match in self._matches.items():
                self._teams.append(match.homeTeam)
        return self._teams


class MatchListLite(MatchList):
    """
    Lite version of MatchList which doesnt load all matches
    Used to store matchIds only and overrides functionality 
    that accessed Match object data
    """
    def __init__(self, matchIds):
        """
        ARGS:
            matchIds [int] - list of match ids to load into the matchlist
        """
        self._matches = {el: None for el in matchIds}

    def getAllTeams(self):
        """
        Returns an empty list as MatchListLite does not have access to Match data
        RETURNS:
            [] - empty list
        """
        return []


class Match():

    @classmethod
    def fromMatchDict(cls, matchDict):
        """
        Create a Match object from match dict loaded from the database
        ARGS:
            matchDict (dict) - full dictionary of a match loaded from the database
        RETURNS
            Match (obj) - Match object
        """
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
        """
        String representation of a match
        """
        return "{} v {} - {}".format(self.homeTeam['name'], self.awayTeam['name'], self.date)

    def getAllStatHeaders(self):
        """
        Return all possibles stats for the match
        RETURNS:
            [str] - list of stat headers for the match
        """
        return self.matchStats.keys()