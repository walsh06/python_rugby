from match import MatchList
from league import League


def get_average_points(team, seasons=None):
    """
    Get average points scored by a team, limit it by season.

    ARGS:
        team (str) - team name
        seasons (str) - season string to limit search, None is all seasons
    RETURNS:
        float - average points scored
    """
    return get_average_stat_for_team('points', team, seasons)


def get_average_stat_for_team(stat, team, seasons=None):
    """
    Get average of a stat for a team, limit it by season.

    ARGS:
        stat (str) - name of stat to search for
        team (str) - team name
        seasons (str) - season string to limit search, None is all seasons
    RETURNS:
        float - average of stats
    """
    match_list = MatchList.create_for_team(team, seasons=seasons)
    matches, stat_total = 0, 0
    for match in match_list:
        stat_total += match.get_stat_for_team(team, stat)
        matches += 1
    return stat_total / matches


def get_players_stats(match_list, stat):
    """
    Get a list of all players in the list of matches
    and their total for the stat in each match.

    ARGS:
        match_list (MatchList) - list of matches to search
        stat (str) - name of the stat to get for each player
    RETURNS:
        [(str, str, float),] - list of tuples sorted by value, in the form
                               (playerName, teamName, statValue)
    """
    player_stats = []
    for match in match_list:
        for team in match.players:
            for player in match.players[team]:
                player_stats.append((player.name, team, player.get_stat(stat)))
    return sorted(player_stats, key=lambda tup: tup[2], reverse=True)


def get_teams_stats(match_list, stat):
    """
    Get a list of all teams in the list of matches
    and their total for the stat in each match.

    ARGS:
        match_list (MatchList) - list of matches to search
        stat (str) - name of the stat to get for each player
    RETURNS:
        [(str, float),] - list of tuples sorted by value, in the form
                          (teamName, statValue)
    """
    team_stats = [
        (team, match.get_stat_for_team(team, stat))
        for match in match_list for team in match.players
    ]
    return sorted(team_stats, key=lambda tup: tup[1], reverse=True)


def get_league_leaders_for_stat(league_name, season, stat):
    """
    Get the league leaders for a given stat in a season.

    ARGS:
        league_name (str) - name of the league
        season (str) - seasons string to search
        stat (str) - stat name to get leaders for
    RETURNS:
        [(str, str, float),] - list of tuples sorted by value, in the form
                               (playerName, teamName, statValue)
    """
    league_leaders_dict = {}
    league = League.from_league_name(league_name)
    if league is not None:
        for match in league._matches[season]:
            for team in match.players:
                for player in match.players[team]:
                    if player.id in league_leaders_dict:
                        league_leaders_dict[player.id][2] += player.get_stat(stat)
                    else:
                        league_leaders_dict[player.id] = [player.name, team, player.get_stat(stat)]
    return sorted(league_leaders_dict.values(), key=lambda tup: tup[2], reverse=True)
