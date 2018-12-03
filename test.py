import datetime
import time

from league import League
from match import MatchList, Match
from matchevent import MatchEvent, MatchEventList
from rugbydb import RugbyDB

ZEBO_TRY = {
    'homeScore': 0,
    'awayScore': 5,
    'time': "11'",
    'type': 1,
    'text': 'Try - Simon Zebo , Ireland',
}
SEXTON_CONV = {
    'homeScore': 0,
    'awayScore': 7,
    'time': "12'",
    'type': 2,
    'text': 'Conversion - Johnny Sexton , Ireland',
}


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

    fail = "{}: Fail\nExpected Result: {}\nResult: {}".format(
        test_name, expected, result
    )
    assert result == expected, fail
    print("{}: Success".format(test_name))


def test_league():
    league = League(
        1234, 'leagueOne', {
            '1718': [5, 6, 7, 8],
            '1819': [1, 2, 3, 4],
        }, False)

    check_result("League - All Match ids",
                 league.get_match_ids,
                 [],
                 [5, 6, 7, 8, 1, 2, 3, 4])
    check_result("League - Season Match ids",
                 league.get_match_ids,
                 ['1819'],
                 [1, 2, 3, 4])

    with Timer('League Load') as t:
        league = League('180659', 'Six Nations', init_matches=True)
    start_date = datetime.datetime(2018, 3, 16)
    end_date = datetime.datetime(2018, 3, 18)
    filtered_matches = league.get_matches_in_range(start_date, end_date)
    check_result('League - Test date range', len, [filtered_matches], 3)

    league = League.from_league_name('Six Nations', init_matches=False)
    assert league.id == '180659', 'League - Test from_league_name failed'


def test_match_list():
    with Timer('Create Match List for Team'):
        match_list = MatchList.create_for_team('munster')
    
    start_date = datetime.datetime(2018, 10, 12)
    end_date = datetime.datetime(2018, 10, 15)
    filtered_list = match_list.get_matches_in_range(start_date, end_date)
    check_result('MatchList - Test date range', len, [filtered_list], 1)


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
    test_event = ZEBO_TRY
    test_event = MatchEvent.from_dict(test_event)
    check_result("Match Event - test is try", test_event.is_try, [], True)
    check_result("Match Event - test is not conversion", test_event.is_conversion, [], False)
    assert test_event.type_string == 'Try', "Match Event - test type string failed"


def test_match_event_list():
    test_events = [ZEBO_TRY, SEXTON_CONV]
    match_event_list = MatchEventList([
        MatchEvent.from_dict(test_events[0]),
        MatchEvent.from_dict(test_events[1]),
    ])
    try_list = match_event_list.get_events_for_type(1)
    check_result('Match Event List - test filter by type', len, [try_list], 1)


def test_player():
    m = Match.from_match_id('133782')
    player = m.players[m.home_team['name']].get_player(0)
    check_result("Player - get stat for player", player.get_stat, ['Tries'], 1)
    check_result("Player - get wrong stat for player", player.get_stat, ['FakeStat'], None)
    player.minutes_played = 20
    player.match_stats['tries'] = 1
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
