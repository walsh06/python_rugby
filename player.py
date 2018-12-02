from matchevent import MatchEventList


class Player:
    """
    Player class to store details and stats of a player in a single match.
    """

    def __init__(self, playerDict, matchEventList=None):
        """
        ARGS:
            playerDict (dict) - dict for a player in a match stored in the database
            matchEventList (MatchEventList) - MatchEventList object used to get minutes played
        """     
        self.name = playerDict['name']
        self.id = playerDict['id']
        self.number = playerDict['number']
        self.position = playerDict['position']
        self.isCaptain = playerDict['captain']
        self.subbed = playerDict['subbed']
        self.eventTimes = playerDict['eventTimes']
        self.matchStats = {}
        for key in playerDict:
            if isinstance(playerDict[key], dict) and key != 'eventTimes':
                stat = playerDict[key]
                self.matchStats[stat['name'].lower()] = float(stat['value'])

        if 'missed tackles' in self.matchStats and self.matchStats['tackles'] >= self.matchStats['missed tackles']:
            # adjust tackles to be completed tackles
            self.matchStats['tackles'] = self.matchStats['tackles'] - self.matchStats['missed tackles']
        self.matchEvents = MatchEventList.fromPlayerEventDict(playerDict['eventTimes'])
        self.minutesPlayed = None
        if matchEventList is not None:
            subEvents = []
            for event in matchEventList:
                if (event.type in {7, 8}) and self.name in event.text:
                    subEvents.append((event.time, event.type))
            subOnTime = 0
            self.minutesPlayed = 0
            for event in sorted(subEvents):
                if event[1] == 7:
                    self.minutesPlayed += event[0] - subOnTime
                    subOnTime = -1
                elif event[1] == 8:
                    subOnTime = event[0]
            if not (int(self.number) > 15 and subOnTime == 0) and subOnTime != -1:
                self.minutesPlayed += 80 - subOnTime  

    def __str__(self):
        return "{}: {}".format(self.number, self.name)

    def getStat(self, stat):
        """
        Get the value of a given stat for the player.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        return self.matchStats.get(stat.lower())

    def getStatAverage(self, stat):
        """
        Get the average value of a given stat for the player.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        return self.getStat(stat)

    def getStatPerEighty(self, stat):
        """
        Get the value of a given stat for the player, normalized for 80 mins.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        statValue = self.getStat(stat)
        if statValue:
            statValue = statValue * (80.0 / self.minutesPlayed)
        return statValue


class PlayerList:

    def __init__(self, playerDictList, matchEventList=None):
        """
        ARGS:
            playerDictList ([dict]) - List of player dicts from the database
            matchEventList (MatchEventList) - MatchEventList object used to get minutes played
        """
        self.players = [Player(playerDict, matchEventList)
                        for playerDict in playerDictList]

    def __len__(self):
        """
        Len representation of PlayerList.
        """
        return len(self.players)

    def __add__(self, bPlayerList):
        """
        Override add operator to add two PlayerLists together
        """
        for bPlayer in bPlayerList:
            self.addPlayer(bPlayer)
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

    def getPlayer(self, index):
        """
        Return player at index in player list.

        ARGS:
            index (int) - index in list, None if index is not in list
        """
        if -1 < index < len(self.players):
            return self.players[index]
        else:
            return None

    def addPlayer(self, player):
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

    def __init__(self, playerDictList):
        """
        ARGS:
            playerDictList ([dict]) - List of player dicts from the database
        """
        if playerDictList:
            ids = [player['id'] for player in playerDictList]
            if len(list(set(ids))) > 1:
                raise Exception("Player Series must take a list of player dicts of the same player")

            standardInfo = playerDictList[0]
            self.name = standardInfo['name']
            self.id = standardInfo['id']

        self.players = [Player(playerDict) for playerDict in playerDictList]

    def __str__(self):
        return self.name

    def getStat(self, stat):
        """
        Get the total value of a given stat for the player in all matches.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        statTotal = 0
        for match in self.players:
            statValue = match.getStat(stat)
            if statValue is None:
                return None
            else:
                statTotal += statValue
        return statTotal
    
    def getStatAverage(self, stat):
        """
        Get the average value of a given stat for the player.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        statTotal = self.getStat(stat)
        return statTotal / len(self.players) if statTotal is not None else None

    def getStatPerEighty(self, stat):
        """
        Get the value of a given stat for the player, normalized for 80 mins.

        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value per 80 mins, None if stat not found
        """
        sumStats = 0
        for match in self.players:
            statValue = match.getStatPerEighty(stat)
            if statValue is None:
                return None
            else:
                sumStats += statValue
        return sumStats / float(len(self.players))

    def addPlayer(self, player):
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
