import sqlalchemy
import pandas as pd 
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime, timedelta
import sqlite3
import os
import re

# For Airflow integration
try:
    from airflow.models import Variable
    from airflow.exceptions import AirflowException
    IN_AIRFLOW = True
except ImportError:
    IN_AIRFLOW = False

def get_token_from_local_server():
    try:
        response = requests.get("http://127.0.0.1:3000")
        if response.status_code == 200:
            # Extract token using regex
            match = re.search(r"Access token: (.+)", response.text)
            if match:
                return match.group(1)
    except requests.RequestException:
        pass
    return None

def get_config():
    if IN_AIRFLOW:
        return {
            "DATABASE_LOCATION": Variable.get("SPOTIFY_DB_LOCATION"),
            "TOKEN": Variable.get("SPOTIFY_TOKEN")
        }
    else:
        token = get_token_from_local_server()
        if not token:
            raise ValueError("Could not retrieve token from local server")
        return {
            "DATABASE_LOCATION": "sqlite:///my_played_tracks.sqlite",
            "TOKEN": token
        }

def check_if_valid_data(df: pd.DataFrame) -> bool:
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False

    # Primary Key Check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key check is violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found")

    # Check that all timestamps are of yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.strptime(timestamp, '%Y-%m-%d') != yesterday:
            raise Exception("At least one of the returned songs does not have a yesterday's timestamp")

    return True

def run_spotify_etl():
    config = get_config()
    
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : f"Bearer {config['TOKEN']}"
    }
    
    # Convert time to Unix timestamp in milliseconds      
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    # Download all songs you've listened to "after yesterday", which means in the last 24 hours      
    r = requests.get(f"https://api.spotify.com/v1/me/player/recently-played?after={yesterday_unix_timestamp}", headers = headers)

    data = r.json()

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # Extracting only the relevant bits of data from the json object      
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])
        
    # Prepare a dictionary in order to turn it into a pandas dataframe below       
    song_dict = {
        "song_name" : song_names,
        "artist_name": artist_names,
        "played_at" : played_at_list,
        "timestamp" : timestamps
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])
    
    # Validate
    if check_if_valid_data(song_df):
        print("Data valid, proceed to Load stage")

    # Load

    engine = sqlalchemy.create_engine(config['DATABASE_LOCATION'])
    conn = sqlite3.connect('my_played_tracks.sqlite')
    cursor = conn.cursor()

    sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

    cursor.execute(sql_query)
    print("Opened database successfully")

    try:
        song_df.to_sql("my_played_tracks", engine, index=False, if_exists='append')
    except:
        print("Data already exists in the database")

    conn.close()
    print("Close database successfully")

    return song_df

if __name__ == "__main__":
    run_spotify_etl()