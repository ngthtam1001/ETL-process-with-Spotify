from spotify_etl import run_spotify_etl

def main():
    try:
        df = run_spotify_etl()
        print("ETL process completed successfully")
        print(df)  # Display the DataFrame
    except ValueError as ve:
        print(f"Error: {str(ve)}")
        print("Make sure the local server (get_token.py) is running on http://127.0.0.1:3000")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()