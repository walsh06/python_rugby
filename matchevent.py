class MatchEvent():

    @classmethod
    def fromMatchEventDict(cls, matchEventDict):
        """
        Create a Match Event from the dictionary in a Match
        ARGS:
            matchEventDict (dict) - dictionary for a single match event read from a match dictionary
        RETURNS:
            MatchEvent (obj) - new MatchEvent object
        """
        return cls(matchEventDict['type'], matchEventDict['time'], matchEventDict['text'], matchEventDict['homeScore'], matchEventDict['awayScore'])

    def __init__(self, type, time, text="", homeScore=None, awayScore=None):
        """
        ARGS:
            type (int) - type of the event
            time (str) - minute of the time in the match
            text (str) - text of the event
            homeScore (int) - score for the home team after the event
            awayScore (int) - score for the away team after the event
        """
        self.typeStrings = {1: 'Try',
                            2: 'Conversion',
                            3: 'Penalty',
                            4: 'Drop Goal',
                            5: 'Yellow Card',
                            6: 'Red Card',
                            7: 'Sub Off',
                            8: 'Sub On',
                            9: 'Game Start',
                            10: 'End of first half',
                            11: 'Start of Second Half',
                            12: 'End of game',
                            9999: 'Text Event'}
        self.type = type
        time = time.replace("'", "")
        if '+' in time:
            self.time = int(time.split('+')[0])
            self.addedTime =int(time.split('+')[1])
        else:
            self.time = int(time)
            self.addedTime = 0
        self.text = text
        self.homeScore = homeScore
        self.awayScore = awayScore

    def __str__(self):
        """
        String representation for a Match Event
        """
        score = ", {}-{}".format(self.homeScore, self.awayScore) if self.homeScore is not None else ""
        return "{}: {}, {} {}".format(self.time, self.typeString, self.text, score)

    @property
    def typeString(self):
        """
        Return the string name for a match event type
        """
        return self.typeStrings[self.type] if self.type in self.typeStrings else self.type

    def isTry(self):
        return self.type == 1

    def isConversion(self):
        return self.type == 2

    def isPenalty(self):
        return self.type == 3

    def isDropGoal(self):
        return self.type == 4

    def isYellowCard(self):
        return self.type == 5

    def isRedCard(self):
        return self.type == 6

    def isSubOff(self):
        return self.type == 7

    def isSubOn(self):
        return self.type == 8

    def isStartOfGame(self):
        return self.type == 9

    def isEndOfFirstHalf(self):
        return self.type == 10

    def isStartOfSecondHalf(self):
        return self.type == 11

    def isEndOfGame(self):
        return self.type == 12

    def isTextEvent(self):
        return self.type == 9999


class MatchEventList():

    @classmethod
    def fromPlayerEventDict(cls, playerEventDict):
        """
        Create a Match Event list for a player events in a match
        ARGS:
            playerEventDict (dict) - dict of events for a player in the form 
                                     {eventType: ["timeOne", "timeTwo"]}, e.g.
                                     {u'1': [u"59'"], u'3': [u"34'"], u'2': [u"50'", u"77'"]}
        RETURNS
            MatchEventList (obj) - list of match events for a player
        """
        events = []
        for type in playerEventDict.keys():
            for event in playerEventDict[type]:
                events.append(MatchEvent(int(type), event))
        return cls(events)

    def __init__(self, matchEvents=[]):
        """
        ARGS:
            matchEvents ([MatchEvent]) - list of MatchEvents to store in the list
        """
        self.matchEvents = matchEvents
    
    def __len__(self):
        """
        len implementation for MatchEventList
        """
        return len(self.matchEvents)

    def __iter__(self):
        """
        Iterator implementation for MatchEventList
        """
        self.currentIndex = -1
        return self

    def next(self):
        """
        Iterator implementation for MatchEventList
        RETURNS:
            MatchEvent (obj) - returns next MatchEvent object in list
        """
        if self.currentIndex >= len(self.matchEvents) - 1:
            raise StopIteration
        else:
            self.currentIndex += 1
            return self.matchEvents[self.currentIndex]

    def addMatchEvent(self, MatchEvent):
        """
        Add a new match event to the list
        ARGS:
            MatchEvent (obj) - new MatchEvent to add
        """
        self.matchEvents.append(MatchEvent)

    def getAllEventsForType(self, type):
        """
        Return a new MatchEventList filtered by type
        ARGS:
            type (int) - type to filter the list by
        RETURNS:
            MatchEventList - list with filtered MatchEvents
        """
        matchEvents = MatchEventList(matchEvents=[])
        for matchEvent in self.matchEvents:
            if matchEvent.type == type:
                matchEvents.addMatchEvent(matchEvent)
        return matchEvents
