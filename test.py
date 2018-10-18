from league import League


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
    l = League(1234, 'leagueOne', {'1819': [1,2,3,4], '1718': [5,6,7,8]})

    checkResult("All Match ids", l.getMatchIds, [], [5,6,7,8,1,2,3,4])
    checkResult("1819 Match ids", l.getMatchIds, ['1819'], [1,2,3,4])

if __name__ == "__main__":
    testLeague()