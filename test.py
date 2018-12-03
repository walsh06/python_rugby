import time
import datetime

from league import League
from match import MatchList, Match
from rugbydb import RugbyDB
from matchevent import MatchEvent, MatchEventList


class Timer:

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        end = time.time()
        print("Timer: {} - {:.2f}s".format(self.name, (end - self.start)))


def check_result(test_name, func, args, expected):
    try:
        result = func(*args)
    except Exception as e:
        print("Exception caught while running > {}".format(test_name))
        print(">>> Exception: {}".format(repr(e)))
        return False
    
    if result == expected:
        success = True
        message = "{}: Success".format(test_name)
    else:
        success = False
        message = "{}: Fail\nExpected Result: {}\nResult: {}".format(test_name, expected, result)
    print(message)
    return success


def test_league():
    l = League(
        1234, 'leagueOne', {
            '1718': [5, 6, 7, 8],
            '1819': [1, 2, 3, 4],
        }, False)

    check_result("League - All Match ids",
                 l.get_match_ids,
                 [],
                 [5, 6, 7, 8, 1, 2, 3, 4])
    check_result("League - Season Match ids",
                 l.get_match_ids,
                 ['1819'],
                 [1, 2, 3, 4])

    with Timer('League Load') as t:
        l = League('180659', 'Six Nations', init_matches=True)
    startDate = datetime.datetime(2018, 3, 16)
    endDate = datetime.datetime(2018, 3, 18)
    filteredLeagueMatches = l.get_matches_in_range(startDate, endDate)
    check_result('League - Test date range', len, [filteredLeagueMatches], 3)

    l = League.from_league_name('Six Nations', init_matches=False)
    assert l.id == '180659', 'League - Test from_league_name failed'


def test_match_list():
    with Timer('Create Match List for Team'):
        matchList = MatchList.create_for_team('munster')
    
    startDate = datetime.datetime(2018, 10, 12)
    endDate = datetime.datetime(2018, 10, 15)
    filteredMatchList = matchList.get_matches_in_range(startDate, endDate)
    check_result('MatchList - Test date range', len, [filteredMatchList], 1)


def test_match():
    m = Match.from_match_id('133782')
    check_result("Match - get stat for team", m.get_stat_for_team, ['Ireland', 'Points'], 30)
    check_result("Match - get wrong stat for team", m.get_stat_for_team, ['Ireland', 'FakeStat'], None)
    check_result("Match - get stat for wrong team", m.get_stat_for_team, ['FakeTeam', 'FakeStat'], None)
    check_result("Match - get Opposition", m.get_opposition, ['Ireland'], 'wales')
    check_result("Match - get Opposition Stat", m.get_stat_for_opposition, ['Ireland', 'Points'], 22)
    check_result("Match - is team playing True", m.is_team_playing, ['Ireland'], True)
    check_result("Match - is team playing False", m.is_team_playing, ['France'], False)
    check_result("Match - is player in game True", m.is_player_in_game, ['Conor Murray'], (True, 'ireland'))
    check_result("Match - is player in game False", m.is_player_in_game, ['Fake Player'], (False, None))


def test_match_event():
    testEvent = {'homeScore': 0, 'awayScore': 5, 'time': "11'", 'type': 1, 'text': 'Try - Simon Zebo , Ireland'}
    testEvent = MatchEvent.from_dict(testEvent)
    check_result("Match Event - test is try", testEvent.is_try, [], True)
    check_result("Match Event - test is not conversion", testEvent.is_conversion, [], False)
    assert testEvent.type_string == 'Try', "Match Event - test type string failed"


def test_match_event_list():
    testEvents = [
        {
            'homeScore': 0,
            'awayScore': 5,
            'time': "11'",
            'type': 1,
            'text': 'Try - Simon Zebo , Ireland',
        },
        {
            'homeScore': 0,
            'awayScore': 7,
            'time': "12'",
            'type': 2,
            'text': 'Conversion - Johnny Sexton , Ireland',
        },
    ]
    matchEventList = MatchEventList([
        MatchEvent.from_dict(testEvents[0]),
        MatchEvent.from_dict(testEvents[1]),
    ])
    tryList = matchEventList.get_events_for_type(1)
    check_result('Match Event List - test filter by type', len, [tryList], 1)


def test_player():
    m = Match.from_match_id('133782')
    player = m.players[m.homeTeam['name']].get_player(0)
    check_result("Player  - get stat for player", player.get_stat, ['Tries'], 1)
    check_result("Player  - get wrong stat for player", player.get_stat, ['FakeStat'], None)
    player.minutesPlayed = 20
    player.matchStats['tries'] = 1
    check_result("Player - get stat per 80", player.get_stat_per_eighty, ['Tries'], 4)


def test_db():
    with Timer('Database Load') as t:
        db = RugbyDB()
    with Timer('Team Search') as t:
        db.get_matches_for_team('Munster')


if __name__ == "__main__":
    print('Test suite started...')
    test_db()
    test_league()
    test_match_list()
    test_match()
    test_player()
    test_match_event()
    test_match_event_list()
    print('Test suite is over.')
