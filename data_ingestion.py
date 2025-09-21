import logging
from utils.db_connection import get_db_connection
from utils.api_handler    import (
    fetch_live_matches,
    fetch_scorecard,
    fetch_series,
    fetch_teams,
    fetch_venues
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_series():
    data = fetch_series().get("seriesList", [])
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO series
      (series_id, series_name, host_country, match_type, start_date, total_matches)
    VALUES (%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      host_country = VALUES(host_country),
      match_type   = VALUES(match_type),
      start_date   = VALUES(start_date),
      total_matches= VALUES(total_matches)
    """
    rows = [
        (
            s["seriesId"],
            s["seriesName"],
            s.get("hostCountry"),
            s.get("matchType"),
            s.get("startDate"),
            s.get("matchCount")
        )
        for s in data
    ]
    if rows:
        cursor.executemany(sql, rows)
        conn.commit()
        logger.info(f"Upserted {len(rows)} series")
    conn.close()

def ingest_teams():
    data = fetch_teams().get("teams", [])
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO teams (team_id, team_name, country)
    VALUES (%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      team_name=VALUES(team_name),
      country  =VALUES(country)
    """
    rows = [(t["teamId"], t["teamName"], t.get("country")) for t in data]
    if rows:
        cursor.executemany(sql, rows)
        conn.commit()
        logger.info(f"Upserted {len(rows)} teams")
    conn.close()

def ingest_venues():
    data = fetch_venues().get("venues", [])
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO venues
     (venue_id,venue_name,city,country,capacity)
    VALUES (%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      city=VALUES(city),
      country=VALUES(country),
      capacity=VALUES(capacity)
    """
    rows = [
        (
            v["venueId"],
            v["venueName"],
            v.get("city"),
            v.get("country"),
            v.get("capacity", 0)
        )
        for v in data
    ]
    if rows:
        cursor.executemany(sql, rows)
        conn.commit()
        logger.info(f"Upserted {len(rows)} venues")
    conn.close()

def ingest_matches():
    data = fetch_live_matches().get("matchList", [])
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO matches
      (match_id, series_id, match_description, team_a_id, team_b_id,
       match_date, venue_id, winning_team_id, victory_margin_type,
       victory_margin, toss_winner_team_id, toss_decision)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      winning_team_id=VALUES(winning_team_id),
      victory_margin=VALUES(victory_margin),
      toss_winner_team_id=VALUES(toss_winner_team_id)
    """
    rows = []
    for m in data:
        info = m.get("matchInfo", {})
        toss = info.get("toss", {})
        win  = info.get("winner", {})
        rows.append((
            info["matchId"],
            info.get("seriesId"),
            info.get("matchDesc"),
            info["team1"]["teamId"],
            info["team2"]["teamId"],
            info.get("startDate"),
            info.get("venueId"),
            win.get("teamId"),
            win.get("marginType"),
            win.get("marginValue"),
            toss.get("winnerTeamId"),
            toss.get("decision")
        ))
    if rows:
        cursor.executemany(sql, rows)
        conn.commit()
        logger.info(f"Upserted {len(rows)} matches")
    conn.close()

def ingest_player_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT match_id FROM matches")
    match_ids = [r[0] for r in cursor.fetchall()]

    p_sql = """
    INSERT IGNORE INTO players
      (player_id, player_name, team_id, role, batting_style, bowling_style)
    VALUES (%s,%s,%s,%s,%s,%s)
    """
    b_sql = """
    INSERT INTO batting_stats
      (match_id, player_id, team_id, innings_number, runs_scored, balls_faced, batting_position, is_out)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      runs_scored=VALUES(runs_scored), balls_faced=VALUES(balls_faced), is_out=VALUES(is_out)
    """
    bw_sql = """
    INSERT INTO bowling_stats
      (match_id, player_id, team_id, overs_bowled, runs_conceded, wickets_taken, maidens)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      runs_conceded=VALUES(runs_conceded), wickets_taken=VALUES(wickets_taken), maidens=VALUES(maidens)
    """
    for mid in match_ids:
        card = fetch_scorecard(mid)
        for inn in card.get("innings", []):
            team_id = inn["team"]["teamId"]
            inn_no  = inn["inningsNumber"]
            for b in inn.get("batting", []):
                cursor.execute(p_sql, (
                    b["playerId"], b["playerName"], team_id,
                    b.get("role"), b.get("battingStyle"), b.get("bowlingStyle")
                ))
                cursor.execute(b_sql, (
                    mid, b["playerId"], team_id, inn_no,
                    b.get("runs",0), b.get("ballsFaced",0),
                    b.get("battingPosition",0), b.get("isOut",True)
                ))
            for bw in inn.get("bowling", []):
                cursor.execute(p_sql, (
                    bw["playerId"], bw["playerName"], team_id,
                    bw.get("role"), bw.get("battingStyle"), bw.get("bowlingStyle")
                ))
                cursor.execute(bw_sql, (
                    mid, bw["playerId"], team_id,
                    bw.get("overs",0.0), bw.get("runsConceded",0),
                    bw.get("wickets",0), bw.get("maidens",0)
                ))
        conn.commit()
    conn.close()
    logger.info("Upserted player stats.")

if __name__ == "__main__":
    ingest_series()
    ingest_teams()
    ingest_venues()
    ingest_matches()
    ingest_player_stats()
    logger.info("Data ingestion complete.")
