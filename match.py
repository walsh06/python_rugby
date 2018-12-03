from datetime import datetime

from matchevent import MatchEvent, MatchEventList
from player import PlayerList
from rugbydb import CachedDB


class MatchList:
    """
    Class to store and manipulate Match objects
    """

    @classmethod
    def create_for_team(cls, team_name, leagues=None, seasons=None):
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
        match_ids = db.get_matches_for_team(team_name.lower(),
                                            leagues=leagues,
                                            seasons=seasons)
        return cls(match_ids)

    @classmethod
    def create_for_league(cls, league_id):
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
            new_match = Match.from_match_id(id_)
            if new_match is not None:
                self._matches[id_] = new_match
    
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
            self.add_match(match_id, another_list.matches[match_id])
        return self

    @property
    def matches(self):
        return self._matches

    def get_match_ids(self):
        """
        Return all match ids in the MatchList.

        RETURNS:
            [int] - list of match ids
        """
        return sorted(self._matches)

    def get_all_teams(self):
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
        match_ids = self.get_match_ids()
        if self.currentMatchIndex >= len(match_ids) - 1:
            raise StopIteration
        else:
            self.currentMatchIndex += 1
            return self._matches[match_ids[self.currentMatchIndex]]
    
    def add_match(self, id, match):
        """
        Add a new match to the matchlist.

        ARGS:
            id (int) - match id of the new match
            match (Match) - match to add
        """
        self._matches[id] = match

    def get_matches_in_range(self,
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
                matches.add_match(id_, match)
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

    def get_all_teams(self):
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
        match_ids = self.get_match_ids()
        if self.currentMatchIndex >= len(match_ids) - 1:
            raise StopIteration
        else:
            self.currentMatchIndex += 1
            return match_ids[self.currentMatchIndex]

    def get_matches_in_range(self, start_date=None, end_date=None):
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
    def from_match_id(cls, match_id):
        """
        Create a Match object from match id.

        ARGS:
            match_id (int) - id for a match to create object for
        RETURNS
            Match (obj) - Match object
        """
        match_dict = CachedDB().get_match_by_id(match_id)
        return cls(match_dict) if match_dict else None

    def __init__(self, match_dict):
        """
        ARGS:
            match_dict (dict) - dictionary storing match information from database
        """
        game = match_dict['gamePackage']
        home_team = game['gameStrip']['teams']['home']
        away_team = game['gameStrip']['teams']['away']
        date = game['gameStrip']['isoDate']
        data_vis = game['matchStats']['dataVis']
        table = game['matchStats']['table']
        scores = game['matchEvents']['col'][0][0]['data']
        attacking = game['matchEvents']['col'][1][1]['data']
        discipline = game['matchDiscipline']['col'][1][0]['data']
        penalties = game['matchDiscipline']['col'][0][0]['data']
        match_attacking = game['matchAttacking']['col'][1][0]['data']
        match_defending = game['matchDefending']['col'][0]
        players = game['matchLineUp']
        match_events = game['matchCommentary']['events']

        self.matchStats = {}
        self.players = {}
        self.matchEventList = MatchEventList([])

        try:
            date_parts = date[:10].split('-')
            time_parts = date[11:-1].split(':')
            self.date = datetime(int(date_parts[0]),
                                 int(date_parts[1]),
                                 int(date_parts[2]),
                                 int(time_parts[0]),
                                 int(time_parts[1]))
            self.homeTeam = {
                'name': home_team['name'].lower(),
                'abbrev': home_team['abbrev'],
                'score': home_team['score'],
            }
            self.awayTeam = {
                'name': away_team['name'].lower(),
                'abbrev': away_team['abbrev'],
                'score': away_team['score'],
            }
            self.matchStats = {
                'points': {
                    'homeValue': float(home_team['score']),
                    'awayValue': float(away_team['score']),
                }
            }

            for item in data_vis + table + discipline + scores + attacking:
                try:
                    home_value = float(item['homeValue'])
                    away_value = float(item['awayValue'])
                except:
                    home_value = float(item['homeValue'][:-1])
                    away_value = float(item['awayValue'][:-1])
                self.matchStats[item['text'].lower()] = {
                    'homeValue': home_value,
                    'awayValue': away_value,
                }
            self.matchStats['penalties conceded'] = {
                'homeValue': float(penalties['homeTotal']),
                'awayValue': float(penalties['awayTotal']),
            }
            
            # adjust tackles to remove missed tackles from the total
            for value in ('homeValue', 'awayValue'):
                self.matchStats['tackles'][value] = self.matchStats['tackles'][value] - self.matchStats['missed tackles'][value]
            
            for stat in match_attacking:
                if "/" in stat['homeValue']:
                    if "Won" in stat['text']:
                        stat_name = stat['text'].split(' ')[0].lower()
                        home_stat = stat['homeValue'].split(' ')
                        away_stat = stat['awayValue'].split(' ')
                        self.matchStats["{} won".format(stat_name)] = {
                            'homeValue': home_stat[0],
                            'awayValue': away_stat[0],
                        }
                        self.matchStats["{} total".format(stat_name)] = {
                            'homeValue': home_stat[2],
                            'awayValue': away_stat[2],
                        }
                    else:
                        stat_name = stat['text'].split(' ')[0].lower()
                        stat_sub_text = stat['text'].split(' ')[1].split('/')

                        home_stat = stat['homeValue'].split(' / ')
                        away_stat = stat['awayValue'].split(' / ')
                        self.matchStats["{} {}".format(stat_name, stat_sub_text[0].lower())] = {
                            'homeValue': home_stat[0][:-1],
                            'awayValue': away_stat[0][:-1],
                        }
                        self.matchStats["{} {}".format(stat_name, stat_sub_text[1].lower())] = {
                            'homeValue': home_stat[1][:-1],
                            'awayValue': away_stat[1][:-1],
                        }
                else:
                    try:
                        home_value = float(stat['homeValue'])
                        away_value = float(stat['awayValue'])
                    except:
                        home_value = float(stat['homeValue'][:-1])
                        away_value = float(stat['awayValue'][:-1])
                    self.matchStats[stat['text'].lower()] = {
                        'homeValue': home_value,
                        'awayValue': away_value,
                    }
            
            for stat in match_defending:
                set_piece = stat['data']
                stat_name = set_piece['text'].split(' ')[0].lower()
                self.matchStats["{} won".format(stat_name)] = {
                    'homeValue': set_piece['homeWon'],
                    'awayValue': set_piece['awayWon'],
                }
                self.matchStats["{} total".format(stat_name)] = {
                    'homeValue': set_piece['homeTotal'],
                    'awayValue': set_piece['awayTotal'],
                }
            
            for event in match_events:
                self.matchEventList.add_match_event(MatchEvent.from_dict(event))
            
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

    def get_stat_headers(self):
        """
        Return all possibles stats for the match.

        RETURNS:
            [str] - list of stat headers for the match
        """
        return sorted(self.matchStats)

    def get_home_away_value(self, team):
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

    def is_team_playing(self, team):
        """
        Check if a given team is playing in this match.

        ARGS:
            team (str) - team name to check
        RETURNS:
            bool - True = team is playing in the match
                   False = team is not playing in the match
        """
        return bool(self.get_home_away_value(team))

    def get_opposition(self, team):
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
    
    def get_stat_for_opposition(self, team, stat):
        """
        Get the stat for the opposition of the team provided.

        ARGS:
            team (str) - team to look for their opposition
            stat (str) - name of the stat value to get
        RETURNS:
            float - value of the stat or None if not found
        """
        return self.get_stat_for_team(self.get_opposition(team), stat)

    def get_stat_for_team(self, team, stat):
        """
        Return a stats value for a given team if they played in the match.
        ARGS:
            team (str) - team name
            stat (str) - stat name to get
        RETURNS:
            float - value for stat or None if not found
        """
        if stat.lower() in self.matchStats:
            value = self.get_home_away_value(team)
            return self.matchStats[stat.lower()][value] if value is not None else None
        return None

    def is_player_in_game(self, player_name):
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

    def get_player(self, player_name, team=None):
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
