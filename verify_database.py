
import sqlite3

conn = sqlite3.connect("cricket_dashboard.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# Check number of records
print("PLAYERS:")
cursor.execute("SELECT * FROM players")
for row in cursor.fetchall():
    print(row)

print("\nMATCHES:")
cursor.execute("SELECT * FROM matches")
for row in cursor.fetchall():
    print(row)

print("\nPERFORMANCE ITEMS:")
cursor.execute("SELECT * FROM performance_items")
for row in cursor.fetchall():
    print(row)

# Display combined records using JOIN
print("\nCOMPLETE PERFORMANCE REPORT:")

cursor.execute("""
    SELECT
        p.player_name,
        m.opponent_team,
        m.match_date,
        pi.stat_name,
        pi.stat_value
    FROM players p
    JOIN matches m ON p.player_id = m.player_id
    JOIN performance_items pi ON m.match_id = pi.match_id
""")

for row in cursor.fetchall():
    print(row)

conn.close()
