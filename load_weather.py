import sqlite3
import pandas as pd

# Load both stages of the weather data.
raw_df = pd.read_csv("weather_raw.csv")
clean_df = pd.read_csv("weather_clean.csv")

print("Raw data before cleaning:")
print(raw_df.head())
print("Raw rows:", len(raw_df))

print("\nCleaned and transformed data:")
print(clean_df.head())
print("Clean rows:", len(clean_df))

# Save each CSV into a separate SQLite table.
with sqlite3.connect("weather.db") as conn:
    # Remove the old single-table version of the database.
    conn.execute("DROP TABLE IF EXISTS weather;")

    raw_df.to_sql(
        "weather_raw",
        conn,
        if_exists="replace",
        index=False
    )

    clean_df.to_sql(
        "weather_clean",
        conn,
        if_exists="replace",
        index=False
    )

    # Read both tables back to verify the database contents.
    saved_raw_df = pd.read_sql_query(
        "SELECT * FROM weather_raw",
        conn
    )

    saved_clean_df = pd.read_sql_query(
        "SELECT * FROM weather_clean",
        conn
    )

    tables = pd.read_sql_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """,
        conn
    )

print("\nSQLite tables:")
print(tables)

print("\nRaw data read back from SQLite:")
print(saved_raw_df.head())
print("Raw rows in database:", len(saved_raw_df))

print("\nClean data read back from SQLite:")
print(saved_clean_df.head())
print("Clean rows in database:", len(saved_clean_df))