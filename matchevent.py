class MatchEvent:

    @classmethod
    def fromMatchEventDict(cls, match_event_dict):
        """
        Create a Match Event from the dictionary in a Match.

        ARGS:
            match_event_dict (dict) - dictionary for a single match event
                                      read from a match dictionary
        RETURNS:
            MatchEvent (obj) - new MatchEvent object
        """
        return cls(match_event_dict['type'],
                   match_event_dict['time'],
                   match_event_dict['text'],
                   match_event_dict['homeScore'],
                   match_event_dict['awayScore'])

    def __init__(self, type_, time, text="", home_score=None, away_score=None):
        """
        ARGS:
            type_ (int) - type of the event
            time (str) - minute of the time in the match
            text (str) - text of the event
            home_score (int) - score for the home team after the event
            away_score (int) - score for the away team after the event
        """
        self.typeStrings = {
            1: 'Try',
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
            9999: 'Text Event'
        }
        self.type = type_
        time = time.replace("'", "")
        if '+' in time:
            self.time = int(time.split('+')[0])
            self.addedTime = int(time.split('+')[1])
        else:
            self.time = int(time)
            self.addedTime = 0
        self.text = text
        self.homeScore = home_score
        self.awayScore = away_score

    def __str__(self):
        """
        String representation for a Match Event.
        """
        score = ", {}-{}".format(self.homeScore, self.awayScore) if self.homeScore else ""
        return "{}: {}, {} {}".format(self.time, self.typeString, self.text, score)

    @property
    def typeString(self):
        """
        Return the string name for a match event type.
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


class MatchEventList:

    @classmethod
    def fromPlayerEventDict(cls, player_event_dict):
        """
        Create a Match Event list for a player events in a match.

        ARGS:
            player_event_dict (dict) - dict of events for a player in the form
                                       {eventType: ["timeOne", "timeTwo"]}, e.g.
                                       {
                                         '1': ["59'"],
                                         '3': ["34'"],
                                         '2': ["50'", "77'"],
                                       }
        RETURNS
            MatchEventList (obj) - list of match events for a player
        """
        events = []
        for type_ in player_event_dict:
            events.extend([MatchEvent(int(type_), event)
                           for event in player_event_dict[type_]])
        return cls(events)

    def __init__(self, match_events=None):
        """
        ARGS:
            match_events ([MatchEvent]) - list of MatchEvents to store in the list
        """
        self.matchEvents = match_events or []
    
    def __len__(self):
        """
        len implementation for MatchEventList.
        """
        return len(self.matchEvents)

    def __iter__(self):
        """
        Iterator implementation for MatchEventList.
        """
        self.currentIndex = -1
        return self

    def __next__(self):
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

    def addMatchEvent(self, match_event):
        """
        Add a new match event to the list.

        ARGS:
            match_event (obj) - new MatchEvent to add
        """
        self.matchEvents.append(match_event)

    def getAllEventsForType(self, type_):
        """
        Return a new MatchEventList filtered by type.
        
        ARGS:
            type_ (int) - type to filter the list by
        RETURNS:
            MatchEventList - list with filtered MatchEvents
        """
        matchEvents = MatchEventList()
        for matchEvent in self.matchEvents:
            if matchEvent.type == type_:
                matchEvents.addMatchEvent(matchEvent)
        return matchEvents
