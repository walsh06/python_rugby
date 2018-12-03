from datetime import datetime

from match import MatchList, MatchListLite
from variables import MATCH_IDS


class LeagueList:  # TODO: rename to LeagueDict
    """
    Class to hold a collection of League objects that can be 
    accessed and manipulated
    """

    def __init__(self, league_dict):
        """
        ARGS:
            league_dict (dict) - dictionary for a league to load up in the form
            {
              leagueId: {
                'name': 'leagueName',
                'matchIds': {
                  'season': [int(matchId), int(matchId)]
                }
              }
            }
        """
        self._leagues = {}
        self._league_names = {}
        for league_id, league in league_dict.items():
            instance = League(league_id, league['name'], league['matchIds'])
            self._leagues[league_id] = instance
            self._league_names[league['name'].lower()] = league_id

    def get_by_name(self, league_name):
        """
        Return a league from the list by the league name.

        ARGS:
            league_name (str) - league name to search for
        RETURNS:
            League (obj) - League object or None if not found
        """
        if league_name.lower() in self._league_names:
            return self._leagues.get(self._league_names[league_name.lower()])

    def get_by_id(self, league_id):
        """
        Return a league from the list by the league id.

        ARGS:
            league_id (int) - league id to search for
        RETURNS:
            League (obj) - League object or None if not found
        """
        return self._leagues.get(league_id)


class League:
    """
    League class to store and manipulate data relating to a league.

    Contains a match dictionary where each key is the season and value
    is a MatchList. To speed up performance MatchListLite can be used 
    instead to avoid loading up all matches from the database.
    """

    @classmethod
    def from_league_name(cls, name, init_matches=True):
        """
        Create a League with the league name, returns None if league name not found.

        ARGS:
            name (str) - name of the league
            init_matches (bool) - True = Load all match data into MatchList,
                                 False = Only store match ids in MatchList
        """
        for league in MATCH_IDS:
            if MATCH_IDS[league]['name'].lower() == name.lower():
                return cls(league, name, init_matches=init_matches)
        return None

    def __init__(self, id, name, match_dict=None, init_matches=True):
        """
        ARGS:
            id (str) - id of the league
            name (str) - name of the league
            match_dict (dict) - dictionary in the form
                                 {'season': [int(matchId), int(matchId)]},
                                 loads from default if None
            init_matches (bool) - True = Load all match data into MatchList,
                                 False = Only store match ids in MatchList
        """
        self.id = id
        self.name = name
        self._matchesLoaded = False
        self._matches = {}
        if not match_dict:
            match_dict = MATCH_IDS[self.id]['matchIds']
        self.load_matches(match_dict, init_matches)

    def load_matches(self, match_dict, full=False):
        """
        Load match dictionary for the league where each key is a season and each item is a MatchList

        ARGS:
            match_dict (dict) - dictionary in the form
                                 {'season': [int(matchId), int(matchId)]}
            full (bool) - True = Load all match data into MatchList,
                          False = Only store match ids in MatchList.
        """
        match_list_class = MatchList if full else MatchListLite
        
        for season in match_dict:
            self._matches[season] = match_list_class(match_dict[season])

    def _get_season_ids(self, season=None):
        """
        Internal function to return a list with only single season id
        or return all seasons.

        ARGS:
            season (str) - season name string, if None returns all seasons
        RETURNS
            [str] - list of season names
        """
        if season:
            return [season]

        return sorted(self._matches)
    
    def get_match_ids(self, season=None):
        """
        Return a list of match ids for the league, either for a specific season or all seasons

        ARGS:
            season (str) - season name string, if None returns all seasons
        RETURNS
            [str] - list of match ids
        """
        matchIdList = []
        for s_id in self._get_season_ids(season):
            matchIdList.extend(self._matches[s_id].get_match_ids())
        return matchIdList

    def contains_team(self, team, season=None):
        """
        Check if a team plays in a league.

        ARGS:
            team (str) - team name to search for
            season (str) - season name string to search, if None searches all seasons
        RETURNS:
            bool - True if team is in the league, False if team is not in the league
        """
        teams = set()
        for s_id in self._get_season_ids(season):
            teams |= set(self._matches[s_id].get_all_teams())
        return team.lower() in teams

    def get_matches_in_range(self,
                             start_date=datetime.min,
                             end_date=datetime.max):
        """
        Filter matches in the league for a given date range, returns a new MatchList.

        ARGS:
            start_date (datetime) - start date in range to search, default to datetime.min
            end_date (datetime) - end date in range to search, default to datetime.max
        RETURNS:
            MatchList (obj) - return new MatchList object with matches in date range
        """
        merged_match_list = MatchList(match_ids=[])
        for season_id in self._get_season_ids():
            merged_match_list += self._matches[season_id].get_matches_in_range(start_date, end_date)
        return merged_match_list
