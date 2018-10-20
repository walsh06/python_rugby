
class Player():
    """
    Player class to store details and stats of a player in a single match
    """

    def __init__(self, playerDict):
        """
        ARGS:
            playerDict (dict) - dict for a player in a match stored in the database
        """     
        self.name = playerDict['name']
        self.id = playerDict['id']
        self.number = playerDict['number']
        self.position = playerDict['position']
        self.isCaptain = playerDict['captain']
        self.subbed = playerDict['subbed']
        self.eventTimes = playerDict['eventTimes']
        self.matchStats = {}
        for key in playerDict.keys():
            if type(playerDict[key]) is dict and key != 'eventTimes':
                stat = playerDict[key]
                self.matchStats[stat['name']] = float(stat['value'])

    def __str__(self):
        return "{}: {}".format(self.number, self.name)

    def getStat(self, stat):
        """
        Get the value of a given stat for the player
        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        if stat in self.matchStats.keys():
            return self.matchStats[stat]
        return None

    def getStatAverage(self, stat):
        """
        Get the average value of a given stat for the player
        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        return self.getStat(stat)

class PlayerSeries():
    """
    Player class to store details and stats of a player in a series of matches
    The player must be the same in all matches otherwise an exception is raised
    """

    def __init__(self, playerDictList):
        """
        ARGS:
            playerDictList ([dict]) - List of player dicts from the database
        """
        checkId = playerDictList[0]['id']
        for playerDict in playerDictList[1:]:
            if lastId != playerDict['id']:
                raise Exception("Player Series must take a list of player dicts of the same player")

        standardInfo = playerDictList[0]
        self.name = standardInfo['name']
        self.id = standardInfo['id']
        self.playerMatches = []
        for playerDict in playerDictList:
            self.playerMatches.append(PlayerMatch(playerDict))

    def __str__(self):
        return self.name

    def getStat(self, stat):
        """
        Get the total value of a given stat for the player in all matches
        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        statTotal = 0
        for match in playerMatches:
            statValue = match.getStat(stat)
            if statValue is None:
                return None
            else:
                statTotal += statValue
        return statTotal
    
    def getStatAverage(self, stat):
        """
        Get the average value of a given stat for the player
        ARGS:
            stat (str) - name of the stat to look for
        RETURNS
            float - stat value, None if stat not found
        """
        statTotal = self.getStat(stat)
        return statTotal/len(playerMatches) if statTotal is not None else None


class PlayerList():

    def __init__(self):
        pass