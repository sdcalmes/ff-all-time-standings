from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
import espn_league_info
import sleeper_league_info
import league_utilities
from sleeper_wrapper import League

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

ESPN_LEAGUE_ID = 185829
SLEEPER_LEAGUE_ID = 850787395090624512
season_platform_map = {
    2014: 'ESPN',
    2015: 'ESPN',
    2016: 'ESPN',
    2017: 'ESPN',
    2018: 'ESPN',
    2019: 'SLEEPER',
    2020: 'SLEEPER',
    2021: 'SLEEPER',
    2022: 'SLEEPER'
}


@app.get("/convert")
async def convert():
    model = espn_league_info.convert_espn_to_sleeper(espn_league_info.get_league(ESPN_LEAGUE_ID, 2014))
    return {'model': model}


@app.get("/h2h")
async def h2h():
    espn_out = {}
    espn_league_map = espn_league_info.get_league_map(ESPN_LEAGUE_ID)
    sleeper_league_map = sleeper_league_info.get_league_map(SLEEPER_LEAGUE_ID)
    espn_out = espn_league_info.get_head_to_head(espn_league_map)
    espn_out = sleeper_league_info.get_head_to_head(sleeper_league_map, espn_out)
    return {'h2h': espn_out}

@app.get("/root")
async def root():
    return all_league_data('Lathropolis')


@app.get("/league/{league_id}")
async def get_league(league_id: int):
    league_map = espn_league_info.get_league_map(league_id)
    all_league_info = {}
    standings = {}
    for year, league in league_map.items():
        final_standings = espn_league_info.get_final_standings(league)
        standings[year] = {}
        for place, team in final_standings.items():
            standings[year][place] = team.owner
    all_league_info["final_standings"] = standings
    return {league_id: all_league_info}


@app.get("/league/{league_id}/{season}")
async def get_league(league_id: int, season: int):
    standings = {}
    league = espn_league_info.get_league(league_id, season)
    final_standings = espn_league_info.get_top_three(league)
    standings_str = ""
    for team in final_standings:
        standings_str = standings_str + team.owner + ", "
    standings[season] = standings_str
    return {"message": standings}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, 'result': {}})

@app.get("/all")
async def get_all():
    return {'data': all_league_data('Lathropolis')}


@app.post("/")
async def get_sleeper_espn_league(request: Request, espn_id: int = Form(), sleeper_id: int = Form(), league_name: str = Form()):
    data = all_league_data(league_name)
    return templates.TemplateResponse('index.html', context={'request': request, 'result': {'espn_id': espn_id, 'sleeper_id': sleeper_id, 'data': data}})


def all_league_data(league_name):
    league_map = {}
    all_league_info = {}
    all_league_info['year_data'] = {}
    espn_league_map = {}
    sleeper_league_map = {}

    for year, platform in season_platform_map.items():
        print("Grabbing year..." + str(year))
        curr_year = {}
        all_league_info['year_data'][year] = {}
        if platform == 'ESPN':
            league_map[year] = espn_league_info.get_league(ESPN_LEAGUE_ID, year)
            espn_league_map[year] = league_map[year]
        else:
            league_map[year] = sleeper_league_info.get_league(SLEEPER_LEAGUE_ID, year)
            sleeper_league_map[year] = league_map[year]
        curr_year[year] = league_map[year]
        all_league_info['year_data'][year]["regular_standings"] = league_utilities.get_standings_by_type(curr_year,
                                                                                                         'regular')
        all_league_info['year_data'][year]["final_standings"] = league_utilities.get_standings_by_type(curr_year,
                                                                                                       'final')
    all_league_info['total_w_l'] = league_utilities.get_w_l_record_overall(league_map)
    print("Done grabbing data.")
    all_league_info["average_regular_standing"] = league_utilities.get_average_standing(all_league_info['year_data'],
                                                                                        'regular')
    all_league_info["average_final_standing"] = league_utilities.get_average_standing(all_league_info['year_data'],
                                                                                      'final')
    all_league_info["average_standing_difference"] = league_utilities.get_average_standing_difference(all_league_info)
    print("Getting ESPN h2h data.")
    h2h = espn_league_info.get_head_to_head(espn_league_map)
    print("Getting Sleeper  h2h data.")
    h2h = sleeper_league_info.get_head_to_head(sleeper_league_map, h2h)
    for key, value in h2h.items():
        value[key] = {"w": 0, "l": 0}
    #h2h = league_utilities.get_total_w_l_from_h2h(h2h)
    h2h_sorted = {}
    for key, value in h2h.items():
        print("Sorting h2h items...")
        sorted_keys = value.items()
        new_values = sorted(sorted_keys)
        h2h_sorted[key] = new_values
        # sortedkeys = sorted(value.keys(), key=lambda x: x.lower())
        # new_values = sorted(sortedkeys)
    sorted_keys = h2h_sorted.items()
    all_league_info['head_to_head'] = sorted(sorted_keys)
    return {league_name: all_league_info}
