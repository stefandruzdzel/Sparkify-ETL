# Sparkify ETL Project

## Overview

This is the first project in the Udacity Data Engineering Nano Degree Program.  
The purpose is to build data pipelines that read in two types of json files and create a relational postgres database, consisting of 5 tables in a star schema.
Spark is a fictional music streaming service.  The raw data files contain data on songs, and user listener data.  The goal of this project is to create a database organized for queries that analyze song plays.  

Some of the code was provided as part of the project.  I provided all queries in sql_queries.py, and much of the code in etl.py (although the general layout and functions were provided by Udacity).

## How to run
1. To run locally, follow the instructions at the bottom of the README below to install a Docker image that will allow the postgresql DB to run
https://github.com/kenhanscombe/project-postgres

2. Run create_tables.py

3. Run etl.py

4. Run or alter test.py to view the contents of the databases


## Schema Design

### Fact Table
songplays - records in log data associated with song plays i.e. records with page NextSong
    songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

### Dimension Tables
users - users in the app
    user_id, first_name, last_name, gender, level
songs - songs in music database
    song_id, title, artist_id, year, duration
artists - artists in music database
    artist_id, name, location, latitude, longitude
time - timestamps of records in songplays broken down into specific units
    user_id, hour, day, week, month, year, weekday, song_id
    With the rubric's scheme this table did not have a way to be linked to the other tables so I added in user_id and song_id.
        
        

### Other Notes
1. If I was to devote more time to this, I would optimize the datatypes, researching whether smaller data types would be appropriate for some columns.
2. I would also research and implement a way to insert multiple rows of data at a time since it would likely improve performance.