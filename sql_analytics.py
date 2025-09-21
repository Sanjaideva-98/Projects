import streamlit as st
import pandas as pd
from utils.db_connection import get_db_connection

def app():
    st.title("📊 SQL-Driven Analytics")

    def run_sql(sql: str):
        conn = get_db_connection()
        try:
            df = pd.read_sql_query(sql, conn)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Query error: {e}")
        finally:
            conn.close()
# 1. Define ALL 25 queries in one place
QUERIES = {
    "Q1: Find all players who represent India": 
    """
    SELECT p.player_name, p.role, p.batting_style, p.bowling_style
      FROM players p
      JOIN teams t ON p.team_id = t.team_id
     WHERE t.team_name = 'India';
    """,

    "Q2: Show matches in the last 30 days": 
    """
    SELECT m.match_description,
           ta.team_name AS team_a,
           tb.team_name AS team_b,
           v.venue_name, v.city,
           m.match_date
      FROM matches m
      JOIN teams ta ON m.team_a_id = ta.team_id
      JOIN teams tb ON m.team_b_id = tb.team_id
      JOIN venues v  ON m.venue_id = v.venue_id
     WHERE m.match_date >= CURDATE() - INTERVAL 30 DAY
     ORDER BY m.match_date DESC;
    """,

    "Q3: Top 10 ODI run scorers": 
    """
    SELECT p.player_name,
           p.total_runs,
           (p.total_runs / 
             (SELECT COUNT(DISTINCT match_id)
                FROM batting_stats
               WHERE player_id = p.player_id)
           ) AS batting_average,
           (SELECT COUNT(DISTINCT match_id)
              FROM batting_stats
             WHERE player_id = p.player_id
               AND runs_scored >= 100
           ) AS centuries
      FROM players p
      JOIN series s  ON s.match_type = 'ODI'
      JOIN matches m ON m.series_id = s.series_id
      JOIN batting_stats bs 
        ON bs.player_id = p.player_id
       AND bs.match_id  = m.match_id
     GROUP BY p.player_name
     ORDER BY p.total_runs DESC
     LIMIT 10;
    """,

    "Q4: Display venues with capacity > 30,000": 
    """
    SELECT venue_name, city, country, capacity
      FROM venues
     WHERE capacity > 30000
     ORDER BY capacity DESC;
    """,

    "Q5: Calculate how many matches each team has won": 
    """
    SELECT t.team_name, COUNT(*) AS total_wins
      FROM matches m
      JOIN teams t ON m.winning_team_id = t.team_id
     GROUP BY t.team_name
     ORDER BY total_wins DESC;
    """,

    "Q6: Count players by role": 
    """
    SELECT role, COUNT(*) AS player_count
      FROM players
     GROUP BY role
     ORDER BY player_count DESC;
    """,

    "Q7: Highest individual batting score by format": 
    """
    SELECT s.match_type,
           MAX(bs.runs_scored) AS highest_score
      FROM batting_stats bs
      JOIN matches m ON bs.match_id = m.match_id
      JOIN series s  ON m.series_id = s.series_id
     GROUP BY s.match_type;
    """,

    "Q8: Series started in 2024": 
    """
    SELECT series_name, host_country, match_type, start_date, total_matches
      FROM series
     WHERE YEAR(start_date) = 2024;
    """,

    "Q9: All-rounders with >1000 runs & >50 wickets": 
    """
    SELECT player_name, total_runs, total_wickets, role
      FROM players
     WHERE role = 'All-rounder'
       AND total_runs   > 1000
       AND total_wickets > 50;
    """,

    "Q10: Details of last 20 completed matches": 
    """
    SELECT m.match_description,
           ta.team_name       AS team_a,
           tb.team_name       AS team_b,
           tw.team_name       AS winning_team,
           m.victory_margin,
           m.victory_margin_type,
           v.venue_name
      FROM matches m
      JOIN teams ta ON m.team_a_id      = ta.team_id
      JOIN teams tb ON m.team_b_id      = tb.team_id
      JOIN teams tw ON m.winning_team_id= tw.team_id
      JOIN venues v  ON m.venue_id       = v.venue_id
     ORDER BY m.match_date DESC
     LIMIT 20;
    """,

    "Q11: Compare players' performance across formats": 
    """
    SELECT p.player_name,
           SUM(CASE WHEN s.match_type = 'Test' THEN bs.runs_scored ELSE 0 END)  AS test_runs,
           SUM(CASE WHEN s.match_type = 'ODI'  THEN bs.runs_scored ELSE 0 END)  AS odi_runs,
           SUM(CASE WHEN s.match_type = 'T20I' THEN bs.runs_scored ELSE 0 END)  AS t20i_runs,
           AVG(bs.runs_scored)                                           AS overall_avg
      FROM players p
      JOIN batting_stats bs ON p.player_id = bs.player_id
      JOIN matches m       ON bs.match_id  = m.match_id
      JOIN series s        ON m.series_id  = s.series_id
     GROUP BY p.player_name
    HAVING COUNT(DISTINCT s.match_type) >= 2;
    """,

    "Q12: Home vs Away performance": 
    """
    SELECT t.team_name,
           SUM(CASE WHEN t.country = v.country 
                    AND m.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
           SUM(CASE WHEN t.country <> v.country 
                    AND m.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
      FROM matches m
      JOIN teams t  ON m.winning_team_id = t.team_id
      JOIN venues v ON m.venue_id        = v.venue_id
     GROUP BY t.team_name;
    """,

    "Q13: Batting partnerships ≥100 runs": 
    """
    SELECT p1.player_name AS batsman_1,
           p2.player_name AS batsman_2,
           bs1.runs_scored + bs2.runs_scored AS partnership_runs,
           bs1.innings_number
      FROM batting_stats bs1
      JOIN batting_stats bs2 
        ON bs1.match_id       = bs2.match_id
       AND bs1.innings_number = bs2.innings_number
       AND bs1.batting_position = bs2.batting_position - 1
      JOIN players p1 ON bs1.player_id = p1.player_id
      JOIN players p2 ON bs2.player_id = p2.player_id
     WHERE (bs1.runs_scored + bs2.runs_scored) >= 100;
    """,

    "Q14: Bowling performance by venue": 
    """
    SELECT p.player_name,
           v.venue_name,
           AVG(bs.runs_conceded / bs.overs_bowled) AS avg_economy_rate,
           SUM(bs.wickets_taken)                  AS total_wickets,
           COUNT(DISTINCT bs.match_id)            AS matches_played
      FROM bowling_stats bs
      JOIN players p ON bs.player_id = p.player_id
      JOIN matches m ON bs.match_id  = m.match_id
      JOIN venues v  ON m.venue_id   = v.venue_id
     WHERE bs.overs_bowled >= 4
     GROUP BY p.player_name, v.venue_name
    HAVING COUNT(DISTINCT bs.match_id) >= 3;
    """,

    "Q15: Performance in close matches": 
    """
    SELECT p.player_name,
           AVG(bs.runs_scored) AS avg_runs,
           COUNT(DISTINCT m.match_id) AS close_matches_played,
           SUM(CASE WHEN m.winning_team_id = bs.team_id THEN 1 ELSE 0 END) AS team_won_count
      FROM batting_stats bs
      JOIN matches m ON bs.match_id  = m.match_id
      JOIN players p ON bs.player_id = p.player_id
     WHERE (m.victory_margin_type = 'runs' AND m.victory_margin < 50)
        OR (m.victory_margin_type = 'wickets' AND m.victory_margin < 5)
     GROUP BY p.player_name;
    """,

    "Q16: Track batting performance by year": 
    """
    SELECT p.player_name,
           YEAR(m.match_date) AS year,
           AVG(bs.runs_scored) AS avg_runs_per_match,
           AVG((bs.runs_scored / bs.balls_faced) * 100) AS avg_strike_rate
      FROM batting_stats bs
      JOIN matches m ON bs.match_id = m.match_id
      JOIN players p ON bs.player_id = p.player_id
     WHERE YEAR(m.match_date) >= 2020
     GROUP BY p.player_name, YEAR(m.match_date)
    HAVING COUNT(bs.match_id) >= 5;
    """,

    "Q17: Advantage from winning the toss": 
    """
    SELECT toss_decision,
           (SUM(CASE WHEN toss_winner_team_id = winning_team_id THEN 1 ELSE 0 END) * 100.0)
           / COUNT(*) AS win_percentage
      FROM matches
     GROUP BY toss_decision;
    """,

    "Q18: Most economical bowlers in limited-overs": 
    """
    SELECT p.player_name,
           (SUM(bs.runs_conceded) * 6.0) / SUM(bs.overs_bowled * 6) AS economy_rate,
           SUM(bs.wickets_taken) AS total_wickets
      FROM bowling_stats bs
      JOIN players p ON bs.player_id = p.player_id
      JOIN matches m ON bs.match_id   = m.match_id
      JOIN series s  ON m.series_id   = s.series_id
     WHERE s.match_type IN ('ODI', 'T20I')
     GROUP BY p.player_name
    HAVING COUNT(DISTINCT bs.match_id) >= 10
       AND AVG(bs.overs_bowled) >= 2
     ORDER BY economy_rate ASC;
    """,

    "Q19: Most consistent batsmen": 
    """
    SELECT p.player_name,
           AVG(bs.runs_scored) AS avg_runs,
           STDDEV(bs.runs_scored) AS stdev_runs
      FROM batting_stats bs
      JOIN players p ON bs.player_id = p.player_id
      JOIN matches m ON bs.match_id  = m.match_id
     WHERE YEAR(m.match_date) >= 2022
       AND bs.balls_faced >= 10
     GROUP BY p.player_name
     ORDER BY stdev_runs ASC;
    """,

    "Q20: Matches & average by format": 
    """
    SELECT p.player_name,
           SUM(CASE WHEN s.match_type = 'Test' THEN 1 ELSE 0 END) AS test_matches,
           AVG(CASE WHEN s.match_type = 'Test' THEN bs.runs_scored END) AS test_avg,
           SUM(CASE WHEN s.match_type = 'ODI'  THEN 1 ELSE 0 END) AS odi_matches,
           AVG(CASE WHEN s.match_type = 'ODI'  THEN bs.runs_scored END) AS odi_avg,
           SUM(CASE WHEN s.match_type = 'T20I' THEN 1 ELSE 0 END) AS t20_matches,
           AVG(CASE WHEN s.match_type = 'T20I' THEN bs.runs_scored END) AS t20_avg
      FROM players p
      JOIN batting_stats bs ON p.player_id = bs.player_id
      JOIN matches m       ON bs.match_id  = m.match_id
      JOIN series  s       ON m.series_id   = s.series_id
     GROUP BY p.player_name
    HAVING COUNT(DISTINCT bs.match_id) >= 20;
    """,

    "Q21: Comprehensive player ranking": 
    """
    SELECT p.player_name,
           s.match_type,
           SUM((bs.runs_scored * 0.01)
               + (bs.runs_scored / bs.balls_faced * 100 * 0.3)
           ) AS batting_points,
           SUM((bws.wickets_taken * 2)
               + ((6 - bws.runs_conceded / bws.overs_bowled) * 2)
           ) AS bowling_points,
           (SUM((bs.runs_scored * 0.01)
               + (bs.runs_scored / bs.balls_faced * 100 * 0.3))
            + SUM((bws.wickets_taken * 2)
               + ((6 - bws.runs_conceded / bws.overs_bowled) * 2))
           ) AS total_score
      FROM players p
      LEFT JOIN batting_stats bs ON p.player_id = bs.player_id
      LEFT JOIN bowling_stats bws 
         ON p.player_id = bws.player_id
        AND bs.match_id  = bws.match_id
      JOIN matches m   ON bs.match_id  = m.match_id
      JOIN series s    ON m.series_id  = s.series_id
     GROUP BY p.player_name, s.match_type
     ORDER BY total_score DESC;
    """,

    "Q22: Head-to-head match analysis": 
    """
    SELECT ta.team_name AS team_a,
           tb.team_name AS team_b,
           COUNT(m.match_id) AS total_matches,
           SUM(CASE WHEN m.winning_team_id = ta.team_id THEN 1 ELSE 0 END) AS team_a_wins,
           SUM(CASE WHEN m.winning_team_id = tb.team_id THEN 1 ELSE 0 END) AS team_b_wins
      FROM matches m
      JOIN teams ta ON m.team_a_id = ta.team_id
      JOIN teams tb ON m.team_b_id = tb.team_id
     WHERE m.match_date >= CURDATE() - INTERVAL 3 YEAR
     GROUP BY team_a, team_b
    HAVING COUNT(m.match_id) >= 5;
    """,

    "Q23: Recent form & momentum": 
    """
    WITH PlayerLast10 AS (
      SELECT bs.*,
             ROW_NUMBER() OVER (
               PARTITION BY bs.player_id 
               ORDER BY m.match_date DESC
             ) as rn
        FROM batting_stats bs
        JOIN matches m ON bs.match_id = m.match_id
    )
    SELECT p.player_name,
           AVG(CASE WHEN rn <= 5 THEN bs.runs_scored END)    AS avg_last_5,
           AVG(bs.runs_scored)                               AS avg_last_10,
           SUM(CASE WHEN bs.runs_scored >= 50 THEN 1 ELSE 0 END) AS scores_50_plus,
           STDDEV(bs.runs_scored)                            AS consistency_score
      FROM PlayerLast10 bs
      JOIN players p ON bs.player_id = p.player_id
     WHERE bs.rn <= 10
     GROUP BY p.player_name
     ORDER BY avg_last_5 DESC;
    """,

    "Q24: Best batting partnerships": 
    """
    WITH Partnerships AS (
      SELECT bs1.player_id AS player_1,
             bs2.player_id AS player_2,
             bs1.runs_scored + bs2.runs_scored AS runs,
             bs1.match_id
        FROM batting_stats bs1
        JOIN batting_stats bs2 
          ON bs1.match_id       = bs2.match_id
         AND bs1.innings_number = bs2.innings_number
         AND bs1.batting_position = bs2.batting_position - 1
    )
    SELECT p1.player_name AS player_1,
           p2.player_name AS player_2,
           AVG(pa.runs)                AS avg_runs,
           SUM(CASE WHEN pa.runs > 50 THEN 1 ELSE 0 END) AS over_50_count,
           MAX(pa.runs)                AS best_partnership,
           (SUM(CASE WHEN pa.runs > 50 THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS success_rate
      FROM Partnerships pa
      JOIN players p1 ON pa.player_1 = p1.player_id
      JOIN players p2 ON pa.player_2 = p2.player_id
     GROUP BY p1.player_name, p2.player_name
    HAVING COUNT(*) >= 5
     ORDER BY avg_runs DESC;
    """,

    "Q25: Time-series analysis of performance": 
    """
    WITH QuarterlyPerformance AS (
      SELECT player_id,
             YEAR(m.match_date)    AS year,
             QUARTER(m.match_date) AS quarter,
             AVG(bs.runs_scored)   AS avg_runs,
             AVG((bs.runs_scored / bs.balls_faced) * 100) AS avg_sr
        FROM batting_stats bs
        JOIN matches m ON bs.match_id = m.match_id
       GROUP BY player_id, year, quarter
      HAVING COUNT(bs.match_id) >= 3
    ),
    RankedQuarters AS (
      SELECT *,
             LAG(avg_runs)     OVER (PARTITION BY player_id ORDER BY year, quarter)    AS prev_runs,
             LAG(avg_sr)       OVER (PARTITION BY player_id ORDER BY year, quarter)    AS prev_sr
        FROM QuarterlyPerformance
    )
    SELECT p.player_name,
           rq.year,
           rq.quarter,
           rq.avg_runs,
           rq.avg_sr    AS avg_strike_rate,
           CASE
             WHEN rq.avg_runs > rq.prev_runs THEN 'Improving'
             WHEN rq.avg_runs < rq.prev_runs THEN 'Declining'
             ELSE 'Stable'
           END AS runs_trajectory
      FROM RankedQuarters rq
      JOIN players p ON rq.player_id = p.player_id
     ORDER BY p.player_name, rq.year, rq.quarter;
    """,
}


