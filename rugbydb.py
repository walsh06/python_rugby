import json
import os

CWD = os.path.dirname(os.path.realpath(__file__))

RUGBY_DB = None

def CachedDB():
    """
    Use the cached database to avoid reloading the database multiple times
    RETURNS:  
        RugbyDB (obj) - RugbyDB object  
    """
    global RUGBY_DB
    if RUGBY_DB is None:
        RUGBY_DB = RugbyDB()
    return RUGBY_DB

class RugbyDB():
    """
    Class to load and manipulate the raw data
    """

    def __init__(self):
        """
        Init and load the database
        """
        self.dbPath = os.path.join(CWD, "rugby_database")
        self.db = {}
        self.loadDb()
    
    def loadDb(self):
        """
        Load the database into memory
        """
        for db in os.listdir(self.dbPath):
            if "backup" not in db:
                with open(os.path.join(self.dbPath, db)) as dbFile:
                    dbContents = dbFile.read()
                leagueDict = json.loads(dbContents)
                self.db[os.path.splitext(db)[0]] = leagueDict

    def _getMatchesDictList(self, ids, leagues=None, seasons=None):
        """
        Returns list of match dicts for the given parameters
        ARGS:
            ids ([str]) - list of match ids to search for
            leagues ([str]) - list of league ids to search, default all leagues
            seasons ([str]) - list of seasons to search, default all seasons
        RETURNS
            [str] - list of match dictionaries
        """
        matches = []
        ids = [str(id) for id in ids]
        if not leagues:
            leagues = self.db.keys()
        for league in leagues:
            if not seasons:
                yearList = self.db[league].keys()
            else:
                yearList = seasons

            for year in yearList:
                if year in self.db[league].keys():
                    for match in self.db[league][year].keys():
                        if match in ids:
                            ids.remove(match)
                            matches.append(self.db[league][year][match])
                        if ids == []:
                            return matches
        return matches

    def getMatchById(self, id):
        """
        Get a match dictionary for a given id
        ARGS:
            id (str) - match id to search for
        RETURNS:
            matchDict - match dictionary if found else None
        """
        match = self._getMatchesDictList([id])
        return match[0] if len(match) == 1 else None

    def getMatchesForTeam(self, team, leagues=None, seasons=None):
        """
        Return a list of match dictionaries for a given team name
        ARGS:
            team ([str]) - list of team names to search for
            leagues ([str]) - list of league ids to search, default all leagues
            seasons ([str]) - list of seasons to search, default all seasons
        RETURNS
            {matchDict} - dictionary of match dictionaries, in the form {matchId: matchDict}
        """
        matches = {}
        if not leagues:
            leagues = self.db.keys()
        for league in leagues:
            if not seasons:
                yearList = self.db[league].keys()
            else:
                yearList = seasons

            for year in yearList:
                if year in self.db[league].keys():
                    for match in self.db[league][year].keys():
                        homeTeam = self.db[league][year][match]['gamePackage']['gameStrip']['teams']['home']['name'].lower()
                        awayTeam = self.db[league][year][match]['gamePackage']['gameStrip']['teams']['away']['name'].lower()
                        if team in homeTeam or team in awayTeam:
                            matches[match] = self.db[league][year][match]
        return matches

    def getMatchesForLeague(self, league):
        pass
