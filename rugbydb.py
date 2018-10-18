import json
import os

CWD = os.path.dirname(os.path.realpath(__file__))

class RugbyDB():

    def __init__(self):
        self.dbPath = os.path.join(CWD, "rugby_database")
        self.db = {}
        self.loadDb()
    
    def loadDb(self):
        for db in os.listdir(self.dbPath):
            if "backup" not in db:
                with open(os.path.join(self.dbPath, db)) as dbFile:
                    dbContents = dbFile.read()
                leagueDict = json.loads(dbContents)
                self.db[os.path.splitext(db)[0]] = leagueDict

    def _getMatchesDictList(self, ids, leagues=None, years=None):
        matches = []
        if not leagues:
            leagues = self.db.keys()
        for league in leagues:
            if not years:
                yearList = self.db[league].keys()
            else:
                yearList = years

            for year in yearList:
                if year in self.db[league].keys():
                    for match in self.db[league][year].keys():
                        if match == id:
                            matches.append(self.db[league][year][match])
        return matches

    def getMatchById(self, id):
        return self._getMatchesDictList([id])

    def getMatchesForTeam(self, team, leagues=None, years=None):
        matches = []
        if not leagues:
            leagues = self.db.keys()
        for league in leagues:
            if not years:
                yearList = self.db[league].keys()
            else:
                yearList = years

            for year in yearList:
                if year in self.db[league].keys():
                    for match in self.db[league][year].keys():
                        homeTeam = self.db[league][year][match]['gamePackage']['gameStrip']['teams']['home']['name'].lower()
                        awayTeam = self.db[league][year][match]['gamePackage']['gameStrip']['teams']['away']['name'].lower()
                        if team in homeTeam or team in awayTeam:
                            matches.append(self.db[league][year][match])
        return matches