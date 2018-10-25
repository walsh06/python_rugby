class MatchEvent():

    @classmethod
    def fromMatchEventDict(cls, matchEventDict):
        return cls(matchEventDict['type'], matchEventDict['time'], matchEventDict['text'], matchEventDict['homeScore'], matchEventDict['awayScore'])

    def __init__(self, type, time, text="", homeScore=None, awayScore=None):
        self.typeStrings = ['Try', 'Conversion', 'Penalty', 'Drop Goal', 'Yellow Card', 'Red Card', 'Sub Off', 'Sub On']
        self.type = type
        self.time = int(time.replace("'", ""))
        self.text = text
        self.homeScore = homeScore
        self.awayScore = awayScore

    def __str__(self):
        score = ", {}-{}".format(self.homeScore, self.awayScore) if self.homeScore is not None else ""
        return "{}: {}, {} {}".format(self.time, self.getTypeString(), self.text, score)

    def getTypeString(self):
        return self.typeStrings[self.type]

    def isTry(self):
        return self.type == 1

    def isConversion(self):
        return self.type == 2

    def isPenalty(self):
        return self.type == 3

class MatchEventList():

    def fromPlayerEventDict(cls, playerEventDict):
        pass

    def __init__(self):
        pass

    def __iter__(self):
        pass

    def next(self):
        pass
