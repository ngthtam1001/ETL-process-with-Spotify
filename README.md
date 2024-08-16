Spotify ETL Process

This project implements an ETL (Extract, Transform, Load) process for Spotify listening data. It extracts your recently played tracks from Spotify, transforms the data, and loads it into a SQLite database.

Features:
- Automatically retrieves Spotify access token
- Extracts recently played tracks from Spotify API
- Transforms the data into a structured format
- Loads the data into a SQLite database
- Can be run as a standalone script or integrated with Apache Airflow

Prerequisites:
- Python 3.7+
- A Spotify Developer account and registered application

Installation:
1. Clone the repository:
   git clone https://github.com/ngthtam1001/ETL-process-with-Spotify.git
   cd ETL-process-with-Spotify

2. Install the required packages:
   pip install -r requirements.txt

3. Set up your Spotify Developer account and create an application to get your Client ID and Client Secret.

Configuration:
1. Update the CLIENT_ID and CLIENT_SECRET in get_token.py with your Spotify application credentials.

2. Ensure the REDIRECT_URI in get_token.py matches the redirect URI you've set in your Spotify application settings.

Usage:
1. Run the token server:
   python get_token.py

2. In a new terminal, run the ETL process:
   python main.py

Project Structure:
- get_token.py: Handles Spotify authentication and provides access tokens
- spotify_etl.py: Contains the main ETL logic
- main.py: Entry point for running the ETL process

Airflow Integration:
This project can be integrated with Apache Airflow. See spotify_dag.py for the DAG definition.

Contributing:
Contributions are welcome! Please feel free to submit a Pull Request.

License:
This project is licensed under the MIT License.
