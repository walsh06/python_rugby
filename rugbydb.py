import json
import os
import re
import requests
import datetime

import variables

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

class RugbyDB(object):
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
                        if team.lower() == homeTeam or team.lower() == awayTeam:
                            matches[match] = self.db[league][year][match]
        return matches

    def getMatchesForLeague(self, league):
        pass


class RugbyDBReadWrite(RugbyDB):

    def __init__(self):
        super(RugbyDBReadWrite, self).__init__()
        timestamp = datetime.datetime.now()
        self.dbWritePath = os.path.join(CWD, "rugby_database_{}".format(str(timestamp.date())))

    def writeDbFile(self, league):
        """
        Write a league database file out
        ARGS:
            league (int) - league id to write file
        """
        if not os.path.exists(self.dbWritePath):
            os.makedirs(self.dbWritePath)
        dbPath = os.path.join(self.dbWritePath, "{}.db".format(league))
        try:
            with open(dbPath, "w") as dbFile:
                dbFile.write(json.dumps(self.db[league], indent=4, sort_keys=True))
        except Exception as e:
            print(e)
            print("Failed to update Database")

    def writeMatchDb(self):
        """
        Write the full database to file
        """
        if not os.path.exists(self.dbWritePath):
            os.makedirs(self.dbWritePath)
        for league in self.db.keys():
            self.writeDbFile(league)

    def addToDb(self, leagueId, year, gameId, matchStr):
        """
        Add a new match to the database
        ARGS:
            leagueId (str) - id of the league of the match
            year (str) - year/season string of the match
            gameId (int) - id of the new match
            matchStr (str) - full match dictionary string read from file or online
        RETURNS:
            bool - True if match added to database, False for failure to add to database
        """
        matchStr = matchStr[:-1].replace('          window.__INITIAL_STATE__ = ', '')
        try:
            matchDict = json.loads(matchStr)
        except:
            print("Error getting game online - game id: {}, league id: {}".format(gameId, leagueId))
            print(url)
            print(matchStr)
            return False
        if leagueId not in self.db.keys():
            self.db[leagueId] = {}
        if year not in self.db[leagueId].keys():
            self.db[leagueId][year] = {}
        self.db[leagueId][year][gameId] = matchDict
        self.writeDbFile(leagueId)
        homeTeam = matchDict['gamePackage']['gameStrip']['teams']['home'] 
        awayTeam = matchDict['gamePackage']['gameStrip']['teams']['away']
        date = matchDict['gamePackage']['gameStrip']['isoDate']
        print("Added: {} v {} - {}".format(homeTeam['name'], awayTeam['name'], date))
        return True

    
    def updateDbFromWeb(self, leagueId, year, force=False):
        """
        Update the database for a league by pulling stats from the internet
        ARGS:
            leagueId (str) - id of the league to update
            year (str) - year/season string to update
            force (bool) - True update the database for every match
                           False only update if the match is not in the database
        """
        for id in variables.MATCH_IDS[leagueId]['matchIds'][year]:
            if force or leagueId not in self.db.keys() or year not in self.db[leagueId].keys() or str(id) not in self.db[leagueId][year].keys():
                gameId = str(id)
                url = "http://www.espn.com/rugby/match?gameId={}&league={}".format(gameId, leagueId)
                response = requests.get(url)
                matchStr = ''
                for line in response.text.splitlines():
                    if 'window.__INITIAL_STATE__ =' in line:
                        matchStr = re.sub(r'[^\x00-\x7f]',r' ',line)
                        break
                if matchStr:
                    success = self.addToDb(leagueId, year, id, matchStr)
                else:
                    print("Failed to get match dict from {}".format(url))
                    return False
