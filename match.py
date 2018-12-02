from datetime import datetime

from matchevent import MatchEvent, MatchEventList
from player import PlayerList
from rugbydb import CachedDB


class MatchList:
    """
    Class to store and manipulate Match objects
    """

    @classmethod
    def createMatchListForTeam(cls, team_name, leagues=None, seasons=None):
        """
        Create a match list for a specific team, filter by league or seasons.

        ARGS:
            team_name (str) - name of the team
            leagues ([int]) - list of league ids to filter by, search all leagues if None
            seasons ([str]) - list of seasons to filter by, search all seasons if None
        RETURNS
            MatchList - MatchList object
        """
        db = CachedDB()
        match_ids = db.getMatchesForTeam(team_name.lower(),
                                         leagues=leagues,
                                         seasons=seasons)
        return cls(match_ids)

    @classmethod
    def createMatchListForLeague(cls, league_id):
        pass

    def __init__(self, match_ids):
        """
        ARGS:
            matchIds [int] - list of match ids to load into the matchlist
        """
        self._matches = {}
        self._teams = None
        db = CachedDB()
        for id_ in match_ids:
            newMatch = Match.fromMatchId(id_)
            if newMatch is not None:
                self._matches[id_] = newMatch
    
    def __str__(self):
        """
        String representation of MatchList
        """
        return "{}".format(self._matches.keys())

    def __len__(self):
        """
        Len representation of MatchList
        """
        return len(self._matches)

    def __add__(self, another_list):
        """
        Override add operator to add two matchlists together.
        """
        for match_id in another_list.matches:
            self.addMatch(match_id, another_list.matches[match_id])
        return self

    @property
    def matches(self):
        return self._matches

    def getMatchIds(self):
        """
        Return all match ids in the MatchList.

        RETURNS:
            [int] - list of match ids
        """
        return sorted(self._matches)

    def getAllTeams(self):
        """
        Return list of teams that play in the MatchListю

        RETURNS:
            [str] - list of team names
        """
        if self._teams is None:
            self._teams = []
            for match in self._matches.items():
                self._teams.append(match.homeTeam)
        return self._teams

    def __iter__(self):
        """
        Iterator implementation for MatchList.
        """
        self.currentMatchIndex = -1
        return self

    def __next__(self):
        """
        Iterator implementation for MatchList.

        RETURNS:
            Match (obj) - returns next match object in list
        """
        matchIds = self.getMatchIds()
        if self.currentMatchIndex >= len(matchIds) - 1:
            raise StopIteration
        else:
            self.currentMatchIndex += 1
            return self._matches[matchIds[self.currentMatchIndex]]
    
    def addMatch(self, id, match):
        """
        Add a new match to the matchlist.

        ARGS:
            id (int) - match id of the new match
            match (Match) - match to add
        """
        self._matches[id] = match

    def getMatchesInDateRange(self,
                              start_date=datetime.min,
                              end_date=datetime.max):
        """
        Filter MatchList for a given date range, returns a new MatchList.

        ARGS:
            start_date (datetime) - start date in range to search, default to datetime.min
            end_date (datetime) - end date in range to search, default to datetime.max
        RETURNS:
            MatchList (obj) - return new MatchList object with matches in date range
        """
        matches = MatchList(match_ids=[])
        for id_, match in self._matches.items():
            if end_date > match.date > start_date:
                matches.addMatch(id_, match)
        return matches


class MatchListLite(MatchList):
    """
    Lite version of MatchList which doesnt load all matches.

    Used to store matchIds only and overrides functionality 
    that accessed Match object data.
    """
    def __init__(self, match_ids):
        """
        ARGS:
            matchIds [int] - list of match ids to load into the matchlist
        """
        self._matches = {el: None for el in match_ids}

    def getAllTeams(self):
        """
        Returns an empty list as MatchListLite doesn't have access to Match data.

        RETURNS:
            [] - empty list
        """
        return []

    def __next__(self):
        """
        Iterator implementation for MatchList.

        RETURNS:
            int - returns next match id in list
        """
        matchIds = self.getMatchIds()
        if self.currentMatchIndex >= len(matchIds) - 1:
            raise StopIteration
        else:
            self.currentMatchIndex += 1
            return matchIds[self.currentMatchIndex]

    def getMatchesInDateRange(self, start_date=None, end_date=None):
        """
        Not implemented for MatchListLite.

        ARGS:
            start_date (datetime) - start date in range to search
            end_date (datetime) - end date in range to search
        RETURNS:
            None - not implemented
        """
        return None


class Match:

    @classmethod
    def fromMatchId(cls, match_id):
        """
        Create a Match object from match id.

        ARGS:
            match_id (int) - id for a match to create object for
        RETURNS
            Match (obj) - Match object
        """
        matchDict = CachedDB().getMatchById(match_id)
        return cls(matchDict) if matchDict else None

    def __init__(self, match_dict):
        """
        ARGS:
            match_dict (dict) - dictionary storing match information from database
        """
        game = match_dict['gamePackage']
        homeTeam = game['gameStrip']['teams']['home']
        awayTeam = game['gameStrip']['teams']['away']
        date = game['gameStrip']['isoDate']
        dataVis = game['matchStats']['dataVis']
        table = game['matchStats']['table']
        scores = game['matchEvents']['col'][0][0]['data']
        attacking = game['matchEvents']['col'][1][1]['data']
        discipline = game['matchDiscipline']['col'][1][0]['data']
        penalties = game['matchDiscipline']['col'][0][0]['data']
        matchAttacking = game['matchAttacking']['col'][1][0]['data']
        matchDefending = game['matchDefending']['col'][0]
        players = game['matchLineUp']
        matchEvents = game['matchCommentary']['events']

        self.matchStats = {}
        self.players = {}
        self.matchEventList = MatchEventList([])

        try:
            dateParts = date[:10].split('-')
            timeParts = date[11:-1].split(':')
            self.date = datetime(int(dateParts[0]),
                                 int(dateParts[1]),
                                 int(dateParts[2]),
                                 int(timeParts[0]),
                                 int(timeParts[1]))
            self.homeTeam = {
                'name': homeTeam['name'].lower(),
                'abbrev': homeTeam['abbrev'],
                'score': homeTeam['score'],
            }
            self.awayTeam = {
                'name': awayTeam['name'].lower(),
                'abbrev': awayTeam['abbrev'],
                'score': awayTeam['score'],
            }
            self.matchStats = {
                'points': {
                    'homeValue': float(homeTeam['score']),
                    'awayValue': float(awayTeam['score']),
                }
            }

            for item in dataVis + table + discipline + scores + attacking:
                try:
                    homeValue = float(item['homeValue'])
                    awayValue = float(item['awayValue'])
                except:
                    homeValue = float(item['homeValue'][:-1])
                    awayValue = float(item['awayValue'][:-1])
                self.matchStats[item['text'].lower()] = {
                    'homeValue': homeValue,
                    'awayValue': awayValue,
                }
            self.matchStats['penalties conceded'] = {
                'homeValue': float(penalties['homeTotal']),
                'awayValue': float(penalties['awayTotal']),
            }
            
            # adjust tackles to remove missed tackles from the total
            for value in ('homeValue', 'awayValue'):
                self.matchStats['tackles'][value] = self.matchStats['tackles'][value] - self.matchStats['missed tackles'][value]
            
            for stat in matchAttacking:
                if "/" in stat['homeValue']:
                    if "Won" in stat['text']:
                        statName = stat['text'].split(' ')[0].lower()
                        homeStat = stat['homeValue'].split(' ')
                        awayStat = stat['awayValue'].split(' ') 
                        self.matchStats["{} won".format(statName)] = {
                            'homeValue': homeStat[0],
                            'awayValue': awayStat[0],
                        }
                        self.matchStats["{} total".format(statName)] = {
                            'homeValue': homeStat[2],
                            'awayValue': awayStat[2],
                        }
                    else:
                        statName = stat['text'].split(' ')[0].lower()
                        statSubText = stat['text'].split(' ')[1].split('/')

                        homeStat = stat['homeValue'].split(' / ')
                        awayStat = stat['awayValue'].split(' / ') 
                        self.matchStats["{} {}".format(statName, statSubText[0].lower())] = {
                            'homeValue': homeStat[0][:-1],
                            'awayValue': awayStat[0][:-1],
                        }
                        self.matchStats["{} {}".format(statName, statSubText[1].lower())] = {
                            'homeValue': homeStat[1][:-1],
                            'awayValue': awayStat[1][:-1],
                        }
                else:
                    try:
                        homeValue = float(stat['homeValue'])
                        awayValue = float(stat['awayValue'])
                    except:
                        homeValue = float(stat['homeValue'][:-1])
                        awayValue = float(stat['awayValue'][:-1])
                    self.matchStats[stat['text'].lower()] = {
                        'homeValue': homeValue,
                        'awayValue': awayValue,
                    }
            
            for stat in matchDefending:
                setPiece = stat['data']
                statName = setPiece['text'].split(' ')[0].lower()
                self.matchStats["{} won".format(statName)] = {
                    'homeValue': setPiece['homeWon'],
                    'awayValue': setPiece['awayWon'],
                }
                self.matchStats["{} total".format(statName)] = {
                    'homeValue': setPiece['homeTotal'],
                    'awayValue': setPiece['awayTotal'],
                }
            
            for event in matchEvents:
                self.matchEventList.addMatchEvent(MatchEvent.fromMatchEventDict(event))
            
            self.players[self.homeTeam['name']] = PlayerList(
                players['home']['team'] + players['home']['reserves'],
                self.matchEventList,
            )
            self.players[self.awayTeam['name']] = PlayerList(
                players['away']['team'] + players['away']['reserves'],
                self.matchEventList,
            )
        except Exception as e:
            print("Skipping {}".format(self))
            print(str(e))
    
    def __str__(self):
        """
        String representation of a match.
        """
        return "{} v {} - {}".format(self.homeTeam['name'].capitalize(),
                                     self.awayTeam['name'].capitalize(),
                                     self.date)

    def getAllStatHeaders(self):
        """
        Return all possibles stats for the match.

        RETURNS:
            [str] - list of stat headers for the match
        """
        return sorted(self.matchStats)

    def getHomeAwayValue(self, team):
        """
        Return homeValue or awayValue depending on whether the team is home or away.

        ARGS:
            team (str) - team name
        RETURNS:
            str - homeValue/awayValue for the team or None if team is not in the match
        """
        if team.lower() == self.homeTeam['name']:
            return 'homeValue'
        elif team.lower() == self.awayTeam['name']:
            return 'awayValue'
        return None

    def isTeamPlaying(self, team):
        """
        Check if a given team is playing in this match.

        ARGS:
            team (str) - team name to check
        RETURNS:
            bool - True = team is playing in the match
                   False = team is not playing in the match
        """
        return bool(self.getHomeAwayValue(team))

    def getOpposition(self, team):
        """
        Get the team name of the opposition to the team provided.

        ARGS:
            team (str) - team name to find their opposition in the match
        RETURNS:
            str - team name of the opposition
                  or None if the team argument is not found in the match
        """
        if team.lower() == self.homeTeam['name']:
            return self.awayTeam['name']
        elif team.lower() == self.awayTeam['name']:
            return self.homeTeam['name']
        return None
    
    def getStatForOpposition(self, team, stat):
        """
        Get the stat for the opposition of the team provided.

        ARGS:
            team (str) - team to look for their opposition
            stat (str) - name of the stat value to get
        RETURNS:
            float - value of the stat or None if not found
        """
        return self.getStatForTeam(self.getOpposition(team), stat)

    def getStatForTeam(self, team, stat):
        """
        Return a stats value for a given team if they played in the match.
        ARGS:
            team (str) - team name
            stat (str) - stat name to get
        RETURNS:
            float - value for stat or None if not found
        """
        if stat.lower() in self.matchStats:
            value = self.getHomeAwayValue(team)
            return self.matchStats[stat.lower()][value] if value is not None else None
        return None

    def isPlayerInGame(self, player_name):
        """
        Check if a player is playing in the match.

        ARGS:
            player_name (str) - name of the player to search for
        RETURNS:
            bool, str - bool whether the player is found or not
                        str for the team name if found, None if not found
        """
        for team, players in self.players.items():
            for player in players:
                if player_name == player.name:
                    return True, team
        return False, None

    def getPlayer(self, player_name, team=None):
        """
        Get a player object from the match.

        ARGS:
            player_name (str) - name of the player to search for
            team (str) - name of the team to limit search for,
                         returns None if team not in match
        RETURNS:
            Player (obj) - player object from the match, None if not found
        """
        if team is None:
            teams = list(self.players)
        elif team.lower() in self.players:
            teams = [team.lower()]
        else:
            return None
    
        for team in teams:
            for player in self.players[team]:
                if player_name == player.name:
                    return player
        return None
