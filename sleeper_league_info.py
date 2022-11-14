from sleeper_wrapper import League
import league_utilities

def get_league_map(league_id):
    end_of_leagues = False
    map_of_leagues = {}
    while not end_of_leagues:
        if league_id is None:
            end_of_leagues = True
        else:
            league = League(league_id)
            map_of_leagues[league.get_league()["season"]] = league
            league_id = league.get_league()["previous_league_id"]
    return map_of_leagues


# Need to enter the most recent league_id
def get_league(league_id, season):
    league_found = False
    league = None
    while not league_found:
        if league_id is None:
            return None
        league = League(league_id)
        if league.get_league()["season"] == str(season):
            league_found = True
        else:
            league_id = league.get_league()["previous_league_id"]
    return league


def get_final_standings(league_id):
    winners_order = [0] * 6
    losers_order = [0] * 6
    league = League(league_id)
    rosters = league.get_rosters()
    map = league.map_rosterid_to_ownerid(league.get_rosters())
    m2 = league.map_users_to_team_name(league.get_users())
    m3 = league.map_users_to_user_name(league.get_users())
    winners_bracket = league.get_playoff_winners_bracket()
    losers_bracket = league.get_playoff_losers_bracket()
    for item in winners_bracket:
        if 'p' in item:
            winners_order[item["p"] - 1] = m3[rosters[item["w"] - 1]["owner_id"]]
            winners_order[item["p"]] = m3[rosters[item["l"] - 1]["owner_id"]]
    for item in losers_bracket:
        if 'p' in item:
            losers_order[item["p"] - 1] = m3[rosters[item["w"] - 1]["owner_id"]]
            losers_order[item["p"]] = m3[rosters[item["l"] - 1]["owner_id"]]
    losers_order.reverse()
    final_order = winners_order + losers_order
    clean_standings_list = []
    for team in final_order:
        clean_standings_list.append((team, '', '', ''))
    return clean_standings_list


def map_username_to_ownerid(users):
    map = {}
    for user in users:
        map[user["display_name"]] = user['user_id']
    return map


def get_head_to_head(league_map: dict[str, League], h2h: dict):
    owner_id_to_name = league_utilities.get_sleeper_owner_to_name_map()
    for year, league in league_map.items():
        l = league.get_league()
        roster_to_ownerid = league.map_rosterid_to_ownerid(league.get_rosters())
        for i in range(1, l["settings"]["last_scored_leg"]):
            weekly_matchups = league.get_matchups(i)
            for j in range(1, 7):
                matchup = list(filter(lambda matchup: matchup['matchup_id'] == j, weekly_matchups))
                if len(matchup) == 0:
                    continue
                ownerA = owner_id_to_name[roster_to_ownerid[matchup[0]['roster_id']]]
                ownerB = owner_id_to_name[roster_to_ownerid[matchup[1]['roster_id']]]
                if ownerA not in h2h:
                    h2h[ownerA] = {}
                if ownerB not in h2h:
                    h2h[ownerB] = {}
                if ownerB in h2h[ownerA]:
                    if matchup[0]['points'] > matchup[1]['points']:
                        h2h[ownerA][ownerB]['w'] += 1
                        h2h[ownerB][ownerA]['l'] += 1
                    else:
                        h2h[ownerA][ownerB]['l'] += 1
                        h2h[ownerB][ownerA]['w'] += 1
                else:
                    if matchup[0]['points'] > matchup[1]['points']:
                        h2h[ownerA][ownerB] = {'w': 1, 'l': 0}
                        h2h[ownerB][ownerA] = {'w': 0, 'l': 1}
                    else:
                        h2h[ownerA][ownerB] = {'w': 0, 'l': 1}
                        h2h[ownerB][ownerA] = {'w': 1, 'l': 0}

    return h2h

