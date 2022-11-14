from espn_api.football import League
import collections

LEAGUE_ID=185829
YEARS_ACTIVE=[2014, 2015, 2016, 2017, 2018]



def get_league_map(league_id):
    league_map = {}
    for year in YEARS_ACTIVE:
        league_map[year] = League(league_id=league_id, year=year, swid='{8195E145-3449-4E45-95E1-4534494E45C9}', espn_s2='AEBW30X%2F91%2BcJ5PSuqy4gkp6YQwkNkYv7AdVCvHWVxVV4xcAtyhdrli11stvaC9PAjlhqttTVnnP%2BFnGLBGFujSyLnmJQGA5U4MLHb4GJa9BCu8hUcOJWAgAB3yUeH0pdXWEruYF%2FMnGeWoTgNROBcvFmOq6%2FoNXAGWoGYMIFpsLvO9gL5URdhGP46ceePfMIAOpOJsLHHfs5IS%2B2O7p3q3GIxqVL1KwQGmpOde%2B%2F6rQCEcb9AQwLcqlsAF4vCoL9NRSD83x7lkCQgsRedI2H8fQ')
    return league_map


def get_league(league_id, season):
    league = League(league_id=league_id, year=season, swid='{8195E145-3449-4E45-95E1-4534494E45C9}',
                              espn_s2='AEBW30X%2F91%2BcJ5PSuqy4gkp6YQwkNkYv7AdVCvHWVxVV4xcAtyhdrli11stvaC9PAjlhqttTVnnP%2BFnGLBGFujSyLnmJQGA5U4MLHb4GJa9BCu8hUcOJWAgAB3yUeH0pdXWEruYF%2FMnGeWoTgNROBcvFmOq6%2FoNXAGWoGYMIFpsLvO9gL5URdhGP46ceePfMIAOpOJsLHHfs5IS%2B2O7p3q3GIxqVL1KwQGmpOde%2B%2F6rQCEcb9AQwLcqlsAF4vCoL9NRSD83x7lkCQgsRedI2H8fQ')
    return league


def get_final_standings(league):
    final_standings = {}
    for team in league.teams:
        final_standings[team.final_standing] = team
    return collections.OrderedDict(sorted(final_standings.items()))


def get_standings(league):
    standings = {}
    print(league)
    for team in league.teams:
        standings[team.standing] = team
    return collections.OrderedDict(sorted(standings.items()))



def get_head_to_head(league_map: dict[str, League]):
    h2h = {}
    scoreboards = {}
    for year, league in league_map.items():
        scoreboards[year] = {}
        for i in range(1, league.current_week + 1):
            for scoreboard in league.scoreboard(i):
                if scoreboard.away_team == 0 or scoreboard.home_team == 0:
                    continue
                if scoreboard.away_team.owner not in h2h:
                    h2h[scoreboard.away_team.owner] = {}
                if scoreboard.home_team.owner not in h2h:
                    h2h[scoreboard.home_team.owner] = {}
                if scoreboard.home_team.owner in h2h[scoreboard.away_team.owner]:
                    if scoreboard.away_score > scoreboard.home_score:
                        h2h[scoreboard.away_team.owner][scoreboard.home_team.owner]['w'] += 1
                        h2h[scoreboard.home_team.owner][scoreboard.away_team.owner]['l'] += 1
                    else:
                        h2h[scoreboard.away_team.owner][scoreboard.home_team.owner]['l'] += 1
                        h2h[scoreboard.home_team.owner][scoreboard.away_team.owner]['w'] += 1
                else:
                    if scoreboard.away_score > scoreboard.home_score:
                        h2h[scoreboard.away_team.owner][scoreboard.home_team.owner] = {'w': 1, 'l': 0}
                        h2h[scoreboard.home_team.owner][scoreboard.away_team.owner] = {'w': 0, 'l': 1}
                    else:
                        h2h[scoreboard.away_team.owner][scoreboard.home_team.owner] = {'w': 0, 'l': 1}
                        h2h[scoreboard.home_team.owner][scoreboard.away_team.owner] = {'w': 1, 'l': 0}
    return h2h


def convert_espn_to_sleeper(league: League):

    sleeper_rosters_list = []
    settings = league.settings
    standings = league.standings()
    teams = league.teams
    for team in teams:
        sleeper_rosters_model = {
            "roster_id": team.team_id
        }
    box_scores = {}
    for i in range(1, league.current_week):
        box_scores[i] = league.scoreboard(i)

    sleeper_model = {
        "sport": 'nfl',
        "total_rosters": len(teams),
        "season": league.year,
        "name": league.settings.name,

    }

    if len(league.settings.matchup_periods) == league.current_week:
        sleeper_model["status"] = "complete"
    else:
        sleeper_model["status"] = "in-progress"

    return sleeper_model




