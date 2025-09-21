# utils/api_handler.py

import requests
import logging

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- API Configuration ---
API_KEY   = "ac2248c809mshb91e7cfb0629886p16d68fjsnff5618af519a"
API_HOST  = "cricbuzz-cricket.p.rapidapi.com"
BASE_URL  = f"https://{API_HOST}"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}


def fetch_data(path: str, label: str, params: dict = None) -> dict:
    """
    Generic GET wrapper.
    - path: e.g. "/matches/v1/live" or "/mcenter/v1/{match_id}/scard"
    - label: used for logging
    - params: optional query parameters
    """
    url = BASE_URL + path
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        logger.info(f"✅ Fetched {label}")
        return resp.json()
    except requests.HTTPError as he:
        logger.error(f"❌ HTTP error fetching {label}: {he}")
    except Exception as e:
        logger.error(f"❌ Exception fetching {label}: {e}")
    return {}


# --- Match Endpoints ---
def fetch_live_matches() -> dict:
    return fetch_data("/matches/v1/live", "live matches")

def fetch_recent_matches() -> dict:
    return fetch_data("/matches/v1/recent", "recent matches")

def fetch_match_details(match_id: int) -> dict:
    return fetch_data(f"/mcenter/v1/{match_id}", f"match info {match_id}")

def fetch_scorecard(match_id: int) -> dict:
    return fetch_data(f"/mcenter/v1/{match_id}/scard", f"scorecard {match_id}")

def fetch_commentary(match_id: int) -> dict:
    return fetch_data(f"/mcenter/v1/{match_id}/comm", f"commentary {match_id}")

def fetch_overs(match_id: int) -> dict:
    return fetch_data(f"/mcenter/v1/{match_id}/overs", f"overs {match_id}")


# --- Player Endpoints ---
def fetch_player_info(player_id: int) -> dict:
    return fetch_data(f"/stats/v1/player/{player_id}", f"player info {player_id}")

def fetch_player_stats(player_id: int) -> dict:
    return fetch_data(f"/stats/v1/player/{player_id}/stats", f"player stats {player_id}")

def fetch_browse_players(query: str = "") -> dict:
    # you can pass search text via params: {"search": query}
    return fetch_data("/stats/v1/player/search", "browse players", params={"search": query})


# --- Venue Endpoints ---
def fetch_venues() -> dict:
    return fetch_data("/venues/v1/45", "venues list")

def fetch_venue_matches(venue_id: int) -> dict:
    return fetch_data(f"/venues/v1/{venue_id}/matches", f"venue matches {venue_id}")

def fetch_venue_stats(venue_id: int) -> dict:
    return fetch_data(f"/stats/v1/venue/{venue_id}", f"venue stats {venue_id}")


# --- Series Endpoints ---
def fetch_series() -> dict:
    return fetch_data("/series/v1/international", "series list")

def fetch_series_squads(series_id: int) -> dict:
    return fetch_data(f"/series/v1/{series_id}/squads", f"series squads {series_id}")

def fetch_series_stats(series_id: int) -> dict:
    return fetch_data(f"/stats/v1/series/{series_id}", f"series stats {series_id}")


# --- Team Endpoints ---
def fetch_teams() -> dict:
    return fetch_data("/teams/v1/international", "teams list")

def fetch_team_stats(team_id: int) -> dict:
    return fetch_data(f"/stats/v1/team/{team_id}", f"team stats {team_id}")

def fetch_team_results(team_id: int) -> dict:
    return fetch_data(f"/teams/v1/{team_id}/results", f"team results {team_id}")


# --- Demo Runner ---
if __name__ == "__main__":
    print("Live Matches →", fetch_live_matches())
    print("Recent Matches →", fetch_recent_matches())
    print("Match Details  →", fetch_match_details(41881))
    print("Scorecard       →", fetch_scorecard(41881))
    print("Commentary      →", fetch_commentary(41881))
    print("Venues list     →", fetch_venues())
    print("Series list     →", fetch_series())
    print("Teams list      →", fetch_teams())
