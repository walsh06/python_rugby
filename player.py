from matchevent import MatchEventList


class Player:
    """
    Player class to store details and stats of a player in a single match.
    """

    def __init__(self, player_dict, match_event_list=None):
        """
        ARGS:
            player_dict (dict) - dict for a player in a match stored in the database
            match_event_list (MatchEventList) - MatchEventList object used to get minutes played
        """     
        self.name = player_dict['name']
        self.id = player_dict['id']
        self.number = player_dict['number']
        self.position = player_dict['position']
        self.is_captain = player_dict['captain']
        self.subbed = player_dict['subbed']
        self.event_times = player_dict['eventTimes']
        self.match_stats = {}
        for key in player_dict:
            if isinstance(player_dict[key], dict) and key != 'eventTimes':
                stat = player_dict[key]
                self.match_stats[stat['name'].lower()] = float(stat['value'])

        missed_tck = self.match_stats.get('missed tackles', 0)
        if self.match_stats['tackles'] >= missed_tck:
            # adjust tackles to be completed tackles
            self.match_stats['tackles'] -= missed_tck
        self.match_events = MatchEventList.from_dict(player_dict['eventTimes'])
        self.minutes_played = None
        if match_event_list is not None:
            sub_events = []
            for event in match_event_list:
                if (event.type in {7, 8}) and self.name in event.text:
                    sub_events.append((event.time, event.type))
            sub_on_time = 0
            self.minutes_played = 0
            for event in sorted(sub_events):
                if event[1] == 7:
                    self.minutes_played += event[0] - sub_on_time
                    sub_on_time = -1
                elif event[1] == 8:
                    sub_on_time = event[0]
            if not (int(self.number) > 15 and sub_on_time == 0) and sub_on_time != -1:
                self.minutes_played += 80 - sub_on_time

    def __str__(self):
        return "{}: {}".format(self.number, self.name)

    def get_stat(self, stat):
        """
        Get the value of a given stat for the player.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        return self.match_stats.get(stat.lower())

    def get_stat_average(self, stat):
        """
        Get the average value of a given stat for the player.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        return self.get_stat(stat)

    def get_stat_per_eighty(self, stat):
        """
        Get the value of a given stat for the player, normalized for 80 mins.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        stat_value = self.get_stat(stat)
        if stat_value:
            stat_value = stat_value * (80.0 / self.minutes_played)
        return stat_value


class PlayerList:

    def __init__(self, player_dict_list, match_event_list=None):
        """
        ARGS:
            player_dict_list ([dict]) - List of player dicts from the database
            match_event_list (MatchEventList) - MatchEventList object used to get minutes played
        """
        self.players = [Player(p, match_event_list) for p in player_dict_list]

    def __len__(self):
        """
        Len representation of PlayerList.
        """
        return len(self.players)

    def __add__(self, another_list):
        """
        Override add operator to add two PlayerLists together
        """
        for player in another_list:
            self.add_player(player)
        return self
    
    def __iter__(self):
        """
        Iterator implementation for MatchList.
        """
        self.currentIndex = -1
        return self

    def __next__(self):
        """
        Iterator implementation for PlayerList.

        RETURNS:
            Player (obj) - returns next player object in list
        """
        if self.currentIndex >= len(self.players) - 1:
            raise StopIteration
        else:
            self.currentIndex += 1
            return self.players[self.currentIndex]

    def get_player(self, index):
        """
        Return player at index in player list.

        ARGS:
            index (int) - index in list, None if index is not in list
        """
        if -1 < index < len(self.players):
            return self.players[index]
        else:
            return None

    def add_player(self, player):
        """
        Add a player to the list.

        ARGS:
            player (Player) - add a player object to the list
        """
        self.players.append(player)


class PlayerSeries(PlayerList):
    """
    Player class to store details and stats of a player in a series of matches.

    The player must be the same in all matches otherwise an exception is raised.
    """

    def __init__(self, player_dict_list):
        """
        ARGS:
            player_dict_list ([dict]) - List of player dicts from the database
        """
        if player_dict_list:
            ids = [player['id'] for player in player_dict_list]
            if len(list(set(ids))) > 1:
                msg = "Player Series must take a list of player dicts of the same player"
                raise Exception(msg)

            standard_info = player_dict_list[0]
            self.name = standard_info['name']
            self.id = standard_info['id']

        self.players = [Player(p) for p in player_dict_list]

    def __str__(self):
        return self.name

    def get_stat(self, stat):
        """
        Get the total value of a given stat for the player in all matches.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        stat_total = 0
        for match in self.players:
            stat_value = match.get_stat(stat)
            if stat_value is None:
                return None
            else:
                stat_total += stat_value
        return stat_total
    
    def get_stat_average(self, stat):
        """
        Get the average value of a given stat for the player.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        stat_total = self.get_stat(stat)
        return stat_total / len(self.players) if stat_total is not None else None

    def get_stat_per_eighty(self, stat):
        """
        Get the value of a given stat for the player, normalized for 80 mins.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value per 80 mins, None if stat not found
        """
        sum_stats = 0
        for match in self.players:
            stat_value = match.get_stat_per_eighty(stat)
            if stat_value is None:
                return None
            else:
                sum_stats += stat_value
        return sum_stats / float(len(self.players))

    def add_player(self, player):
        """
        Add a player to the list.

        ARGS:
            player (Player) - add a player object to the list
        """
        if self.players and player.id != self.id:
            raise Exception("Player Series must be for the same player")

        self.name = player.name
        self.id = player.id
        self.players.append(player)
