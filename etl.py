import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *

def process_song_file(cur, filepath):
    """
    Takes a sql cursor and single song file path (.json).
    Opens the file, updates song and artist tables
    """

    # open song file
    df = pd.read_json(filepath, lines=True, dtype={'year': float})

    # insert song record
    song_data = df.loc[0,['song_id','title','artist_id','year','duration']].values
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_data = df.loc[0,['artist_id','artist_name','artist_location','artist_latitude','artist_longitude']].values
    cur.execute(artist_table_insert, artist_data)



def process_log_file(cur, filepath):
    """
    Takes a sql cursor log file path (.json)
    Extracts data from the file and transforms the data, querying to find songid and artistid if there is a match
    Loads data into time, user and songplay tables 
    """

    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df.query('page == "NextSong"').reset_index()

    # convert timestamp column to datetime
    t = pd.to_datetime(df.loc[:,'ts'], unit='ms')
    
    # insert time data records
    time_data = [df.loc[:,'ts'].values, df.loc[:,'userId'].astype(float).values, t.dt.hour, t.dt.day, t.dt.isocalendar().week, t.dt.month, t.dt.year, t.dt.weekday]
    column_labels = ('start_time', 'userId', 'hour', 'day', 'week', 'month', 'year', 'weekday')
    time_df = pd.DataFrame(time_data).T
    time_df.columns = column_labels
    time_df.loc[:,'songid'] = None


    # load user table
    user_df = df.loc[:,['userId', 'firstName', 'lastName', 'gender', 'level']]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # Add songid to time_df
        time_df.loc[index,'songid'] = songid
        # insert songplay record
        songplay_data = [row['ts'], row['userId'], row['level'], songid, artistid, row['sessionId'], row['location'], row['userAgent']]
        cur.execute(songplay_table_insert, songplay_data)
    
    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))


def process_data(cur, conn, filepath, func):
    """
    Is given a sql cursor, connection, folder path and function.
    It performs the function across all .json files in the folder path.
    Commits the changes to the tables performed in the functions
    """

    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """
    Performs process_data on the log_data and song_data folders
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()