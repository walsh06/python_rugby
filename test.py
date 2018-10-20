import time
import datetime

from league import League
from match import MatchList, Match
from rugbydb import RugbyDB

class Timer():

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        end = time.time()
        print "Timer: {} - {}s".format(self.name, (end - self.start))


def checkResult(testName, func, args, expectedResult):
    try:
        result = func(*args)
    except Exception as e:
        print "Exception caught while running > {}".format(testName)
        print ">>> Execption: {}".format(repr(e))
        return False
    
    if result == expectedResult:
        success = True
        message = "{}: Success".format(testName)
    else:
        success = False
        message = "{}: Fail\nExpected Result: {}\nResult: {}".format(testName, expectedResult, result)
    print message
    return success

def testLeague():
    l = League(1234, 'leagueOne', {'1819': [1,2,3,4], '1718': [5,6,7,8]}, False)

    checkResult("All Match ids", l.getMatchIds, [], [5,6,7,8,1,2,3,4])
    checkResult("1819 Match ids", l.getMatchIds, ['1819'], [1,2,3,4])

    with Timer('League Load') as t:
        l = League('180659', 'Six Nations', initMatches=True)
    print l.getMatchIds('2017')

def testMatchList():
    with Timer('Create Match List for Team'):
        matchList = MatchList.createMatchListForTeam('munster')
    
    startDate = datetime.datetime(2018, 10, 12)
    endDate = datetime.datetime(2018, 10, 15)
    filteredMatchList = matchList.getMatchesinDateRange(startDate, endDate)
    checkResult('MatchList - Test date range', len, [filteredMatchList], 1)

def testMatch():
    db = RugbyDB()
    m = Match.fromMatchId('133782')
    checkResult("Match - get stat for team", m.getStatForTeam, ['Ireland', 'Points'], 30)
    checkResult("Match - get wrong stat for team", m.getStatForTeam, ['Ireland', 'FakeStat'], None)
    checkResult("Match - get stat for wrong team", m.getStatForTeam, ['FakeTeam', 'FakeStat'], None)

def testDB():
    with Timer('Database Load') as t:
        db = RugbyDB()
    with Timer('Team Search') as t:
        matches = db.getMatchesForTeam('munster')

if __name__ == "__main__":
    testLeague()
    testDB()
    testMatchList()
    testMatch()

