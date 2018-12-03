import datetime
import json
import os
import re
import requests

from variables import MATCH_IDS

CWD = os.path.dirname(os.path.realpath(__file__))

RUGBY_DB = None
MATCH_RE = re.compile(r'[^\x00-\x7f]')


def CachedDB():
    """
    Use the cached database to avoid reloading the database multiple times.

    RETURNS:  
        RugbyDB (obj) - RugbyDB object  
    """
    global RUGBY_DB
    if RUGBY_DB is None:
        RUGBY_DB = RugbyDB()
    return RUGBY_DB


class RugbyDB:
    """
    Class to load and manipulate the raw data.
    """

    def __init__(self):
        """
        Init and load the database
        """
        self.dbPath = os.path.join(CWD, "rugby_database")
        self.db = {}
        self.load_db()
    
    def load_db(self):
        """
        Load the database into memory.
        """
        for db in os.listdir(self.dbPath):
            if "backup" not in db:
                with open(os.path.join(self.dbPath, db)) as dbFile:
                    db_contents = dbFile.read()
                league_dict = json.loads(db_contents)
                self.db[os.path.splitext(db)[0]] = league_dict

    def _get_matches_dict_list(self, ids, leagues=None, seasons=None):
        """
        Returns list of match dicts for the given parameters.

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
            leagues = list(self.db)
        for league in leagues:
            if not seasons:
                year_list = self.db[league]
            else:
                year_list = seasons

            for year in year_list:
                if year in self.db[league]:
                    for match in self.db[league][year]:
                        if match in ids:
                            ids.remove(match)
                            matches.append(self.db[league][year][match])
                        if not ids:
                            return matches
        return matches

    def get_match_by_id(self, id):
        """
        Get a match dictionary for a given id.

        ARGS:
            id (str) - match id to search for
        RETURNS:
            matchDict - match dictionary if found else None
        """
        match = self._get_matches_dict_list([id])
        return match[0] if len(match) == 1 else None

    def get_matches_for_team(self, team, leagues=None, seasons=None):
        """
        Return a list of match dictionaries for a given team name.

        ARGS:
            team ([str]) - list of team names to search for
            leagues ([str]) - list of league ids to search, default all leagues
            seasons ([str]) - list of seasons to search, default all seasons
        RETURNS
            {matchDict} - dictionary of match dictionaries, in the form {matchId: matchDict}
        """
        matches = {}
        if not leagues:
            leagues = list(self.db)
        for league in leagues:
            year_list = self.db[league].keys()
            if seasons:
                year_list |= set(seasons)

            for year in year_list:
                for match_id, match in self.db[league][year].items():
                    teams_dict = match['gamePackage']['gameStrip']['teams']
                    home_team = teams_dict['home']['name'].lower()
                    away_team = teams_dict['away']['name'].lower()
                    if team.lower() in {home_team, away_team}:
                        matches[match_id] = match
        return matches

    def get_matches_for_league(self, league):
        pass


class RugbyDBReadWrite(RugbyDB):

    BASE_URL = "http://www.espn.com/rugby/match?gameId={game}&league={league}"

    def __init__(self):
        super(RugbyDBReadWrite, self).__init__()
        today = datetime.date.today()
        self.dbWritePath = os.path.join(CWD, "rugby_database_{}".format(today))
        if not os.path.exists(self.dbWritePath):
            os.makedirs(self.dbWritePath)

    def _write_file(self, league):
        """
        Write a league database file out.

        ARGS:
            league (int) - league id to write file
        """
        db_path = os.path.join(self.dbWritePath, "{}.db".format(league))
        try:
            with open(db_path, "w") as db_file:
                db_file.write(json.dumps(self.db[league], indent=4, sort_keys=True))
        except Exception as e:
            print(e)
            print("Failed to update Database")

    def write_db(self):
        """
        Write the full database to file.
        """
        for league in self.db:
            self._write_file(league)

    def add_to_db(self, league_id, year, game_id, match_str):
        """
        Add a new match to the database.

        ARGS:
            league_id (str) - id of the league of the match
            year (str) - year/season string of the match
            game_id (int) - id of the new match
            match_str (str) - full match dictionary string read from file or online
        RETURNS:
            bool - True if match added to database, False for failure to add to database
        """
        match_str = match_str[:-1].replace('          window.__INITIAL_STATE__ = ', '')
        try:
            match_dict = json.loads(match_str)
        except:
            print(("Error getting game online - game id: {}, league id: {}".format(game_id, league_id)))
            print(match_str)
            return False
        if league_id not in self.db:
            self.db[league_id] = {}
        if year not in self.db[league_id]:
            self.db[league_id][year] = {}
        self.db[league_id][year][game_id] = match_dict
        self._write_file(league_id)
        game = match_dict['gamePackage']['gameStrip']
        home_team = game['teams']['home']
        away_team = game['teams']['away']
        date = game['isoDate']
        print("Added: {} v {} - {}".format(home_team['name'], away_team['name'], date))
        return True
    
    def update_from_web(self, league_id, year, force=False):
        """
        Update the database for a league by pulling stats from the internet.

        ARGS:
            league_id (str) - id of the league to update
            year (str) - year/season string to update
            force (bool) - True update the database for every match
                           False only update if the match is not in the database
        """
        for match_id in MATCH_IDS[league_id]['matchIds'][year]:
            if any((force
                    or league_id not in self.db
                    or year not in self.db[league_id]
                    or str(match_id) not in self.db[league_id][year])):
                success = False
                url = self.BASE_URL.format(game=match_id, league=league_id)
                response = requests.get(url)
                match_str = ''
                for line in response.text.splitlines():
                    if 'window.__INITIAL_STATE__ =' in line:
                        match_str = MATCH_RE.sub(r' ', line)
                        break
                if match_str:
                    success = self.add_to_db(league_id, year, match_id, match_str)
                else:
                    print("Failed to get match dict from {}".format(url))
                return success
