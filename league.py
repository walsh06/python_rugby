from datetime import datetime

from match import MatchList, MatchListLite
from variables import MATCH_IDS


class LeagueList:
    """
    Class to hold a collection of League objects that can be 
    accessed and manipulated
    """

    def __init__(self, leagueDict):
        """
        ARGS:
            leagueDict (dict) - dictionary for a league to load up in the form
                                {leagueId: {'name': 'leagueName', 'matchIds': {'season': [int(matchId), int(matchId)]}}}
        """
        self._leagues = {}
        for league in leagueDict:
            self._leagues[league] = League(league, leagueDict[league]['name'], leagueDict[league]['matchIds'])

    def getLeagueByName(self, leagueName):
        """
        Return a league from the list by the league name
        ARGS:
            leagueName (str) - league name to search for
        RETURNS:
            League (obj) - League object or None if not found
        """
        for league in self._leagues.items():
            if league.name.lower() == leagueName.lower():
                return league
        return None

    def getLeagueById(self, leagueId):
        """
        Return a league from the list by the league id
        ARGS:
            leagueId (int) - league id to search for
        RETURNS:
            League (obj) - League object or None if not found
        """
        if leagueId in self._leagues:
            return self._leagues[leagueId]
        else:
            return None


class League:
    """
    League class to store and manipulate data relating to a league
    Contains a match dictionary where each key is the season and item 
    is a MatchList. To speed up performance MatchListLite can be used 
    instead to avoid loading up all matches from the database
    """

    @classmethod
    def fromLeagueName(cls, name, initMatches=True):
        """
        Create a League with the league name, returns None if league name not found
        ARGS:
            name (str) - name of the league
            initMatches (bool) - True = Load all match data into MatchList, False = Only store match ids in MatchList
        """
        for league in MATCH_IDS:
            if MATCH_IDS[league]['name'].lower() == name.lower():
                return cls(league, name, initMatches=initMatches)
        return None

    def __init__(self, id, name, matchIdDict=None, initMatches=True):
        """
        ARGS:
            id (str) - id of the league
            name (str) - name of the league
            matchIdDict (dict) - dictionary in the form {'season': [int(matchId), int(matchId)]}, loads from default if None
            initMatches (bool) - True = Load all match data into MatchList, False = Only store match ids in MatchList
        """
        self.id = id
        self.name = name
        self._matchesLoaded = False
        self._matches = {}
        if matchIdDict is None:
            matchIdDict = MATCH_IDS[self.id]['matchIds']
        self.loadMatches(matchIdDict, initMatches)

    def loadMatches(self, matchIdDict, full=False):
        """
        Load match dictionary for the league where each key is a season and each item is a MatchList
        ARGS:
            matchIdDict (dict) - dictionary in the form {'season': [int(matchId), int(matchId)]}
            full (bool) - True = Load all match data into MatchList, False = Only store match ids in MatchList
        """
        if full:
            matchListClass = MatchList
        else:
            matchListClass = MatchListLite
        
        for season in matchIdDict:
            self._matches[season] = matchListClass(matchIdDict[season])

    def _getSeasonList(self, season=None):
        """
        Internal function to add a single season id to a list or return all seasons
        ARGS:
            season (str) - season name string, if None returns all seasons
        RETURNS
            [str] - list of season names
        """
        if season:
            return [season]
        else:
            return sorted(self._matches)
    
    def getMatchIds(self, season=None):
        """
        Return a list of match ids for the league, either for a specific season or all seasons
        ARGS:
            season (str) - season name string, if None returns all seasons
        RETURNS
            [str] - list of match ids
        """
        matchIdList = []
        for s_id in self._getSeasonList(season):
            matchIdList.extend(self._matches[s_id].getMatchIds())
        return matchIdList

    def containsTeam(self, team, season=None):
        """
        Check if a team plays in a league
        ARGS:
            team (str) - team name to search for
            season (str) - season name string to search, if None searches all seasons
        RETURNS:
            bool - True if team is in the league, False if team is not in the league
        """
        teams = []
        for s_id in self._getSeasonList(season):
            teams.extend(self._matches[s_id].getAllTeams())
        return team.lower() in teams

    def getMatchesInDateRange(self, startDate=datetime.min, endDate=datetime.max):
        """
        Filter matches in the league for a given date range, returns a new MatchList
        ARGS:
            startDate (datetime) - start date in range to search, default to datetime.min
            endDate (datetime) - end date in range to search, default to datetime.max
        RETURNS:
            MatchList (obj) - return new MatchList object with matches in date range
        """
        mergedMatchList = MatchList(matchIds=[])
        for season in self._getSeasonList(None):
            mergedMatchList += self._matches[season].getMatchesInDateRange(startDate, endDate)
        return mergedMatchList
