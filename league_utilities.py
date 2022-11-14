import sleeper_league_info
import espn_league_info
from sleeper_wrapper import League

def get_sleeper_owner_to_name_map():
    sleeper_owner_to_name_map = {
        '76465061719588864': 'Drew Davis',
        '458362349540077568': 'Andy Keal',
        '94591622507282432': 'Victor Markus',
        '333314910077321216': 'Sam Calmes',
        '458364312960888832': 'Matt Dallman',
        '458362753975840768': 'Jake Folz',
        '81262579812810752': 'justin alt',
        '216255396094930944': 'Luke Fowler',
        '342429448563458048': 'Joey Janz',
        '458362357068853248': 'James Stecker',
        '458363773762138112': 'James Olson',
        '458428894018531328': 'Joe Keal'
    }

    return sleeper_owner_to_name_map

def get_w_l_record_overall(league_map: dict[str, League]):
    wlrecord = []

    owner_id_to_name = get_sleeper_owner_to_name_map()
    for year, league in league_map.items():
            if isinstance(league, League):
                username_to_userid_map = sleeper_league_info.map_username_to_ownerid(league.get_users())
                standings = league.get_standings(league.get_rosters(), league.get_users())
                for team in standings:
                    f = get_sleeper_owner_to_name_map()[username_to_userid_map[team[0]]]
                    wlrecord[f]['w'] += int(team[1])
                    wlrecord[f]['l'] += int(team[2])
            else:
                for team in league.teams:
                    if team.owner not in wlrecord:
                        wlrecord[team.owner] = {'w': 0, 'l': 0}
                    wlrecord[team.owner]['w'] += team.wins
                    wlrecord[team.owner]['l'] += team.losses
    return wlrecord

def get_standings_by_type(league_map, type='regular'):
    standings_output = {}
    for year, league in league_map.items():
        standings_output = {}
        if isinstance(league, League):
            rosters = league.get_rosters()
            users = league.get_users()
            username_to_userid_map = sleeper_league_info.map_username_to_ownerid(users)
            if 'regular' == type:
                standings = league.get_standings(rosters, users)
            elif 'final' == type and not league.get_league()["status"] == 'in_season':
                standings = sleeper_league_info.get_final_standings(league.league_id)
            else:
                standings = {}
            place = 1
            for team in standings:
                standings_output[place] = get_sleeper_owner_to_name_map()[username_to_userid_map[team[0]]]
                place = place + 1
        else:
            if 'regular' == type:
                standings = espn_league_info.get_standings(league)
            elif 'final' == type:
                standings = espn_league_info.get_final_standings(league)
            else:
                standings = {}

            for place, team in standings.items():
                standings_output[place] = team.owner
    return standings_output


def get_average_standing(standings, type='regular'):
    owner_map = {}
    owner_count = {}
    for year, placements in standings.items():
        for place, owner in placements[type + '_standings'].items():
            if owner in owner_map:
                owner_map[owner] = owner_map[owner] + place
                owner_count[owner] = owner_count[owner] + 1
            else:
                owner_map[owner] = place
                owner_count[owner] = 1
    for owner, total_place in owner_map.items():
        owner_map[owner] = round(owner_map[owner] / owner_count[owner], 2)
    return dict(sorted(owner_map.items(), key=lambda item: item[1]))


def get_average_standing_difference(league_info):
    owner_map = {}
    for owner, value in league_info["average_regular_standing"].items():
        owner_map[owner] = round(value - league_info["average_final_standing"][owner], 2)
    return dict(sorted(owner_map.items(), key=lambda item: item[1], reverse=True))


def get_total_w_l_from_h2h(h2h: dict):
    for owner, h2h_matchup in h2h.items():
        all = {
            'w': 0,
            'l': 0
        }
        for opp, wl in h2h_matchup.items():
            all["w"] += h2h_matchup[opp]["w"]
            all["l"] += h2h_matchup[opp]["l"]
        all["pct"] = round(all["w"] / (all["w"] + all["l"]), 3)
        h2h[owner]['Total'] = all
    return h2h