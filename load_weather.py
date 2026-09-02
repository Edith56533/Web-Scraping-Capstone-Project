import sqlite3
import pandas as pd

# Load the cleaned weather data.
df = pd.read_csv("weather_clean.csv")

print("Data to save:")
print(df.head())
print("Rows in CSV:", len(df))

# Connect to SQLite and save the DataFrame as a table.
with sqlite3.connect("weather.db") as conn:
    df.to_sql(
        "weather",
        conn,
        if_exists="replace",
        index=False
    )

    # Read the saved data back to verify it.
    saved_df = pd.read_sql_query(
        "SELECT * FROM weather",
        conn
    )

    print("\nData read back from SQLite:")
    print(saved_df.head())
    print("Rows in database:", len(saved_df))