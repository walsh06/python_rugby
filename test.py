import time

from league import League
from match import MatchList
from rugbydb import RugbyDB

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

    start = time.time()
    l = League('180659', 'Six Nations', initMatches=True)
    end = time.time()
    print "League Load took {}s".format((end - start))
    print l.getMatchIds('2017')

def testMatchList():
    matchList = MatchList.createMatchListForTeam('munster')
    print matchList.getMatchIds()

def testDB():
    start = time.time()
    db = RugbyDB()
    end = time.time()
    print "Database Load took {}s".format((end - start))
    
    start = time.time()
    matches = db.getMatchesForTeam('munster')
    end = time.time()
    print "Database team search took {}s, found {} matches".format((end - start), len(matches))

if __name__ == "__main__":
    testLeague()
    testDB()
    testMatchList()

