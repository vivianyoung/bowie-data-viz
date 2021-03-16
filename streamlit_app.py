import streamlit as st
import pandas as pd
import altair as alt

import sqlite3
from sqlite3 import Connection

# add title to streamlit app
st.title("david bowie music data analysis")

@st.cache(hash_funcs={Connection: id})  # add caching so we load the data only once
def get_connection(path_to_db):
    # connect to db
    try:
        conn = sqlite3.connect(path_to_db, check_same_thread=False)
        return conn
    except Exception as e:
        print(e)

def get_data(conn: Connection):
    sql = f"""
    SELECT
      song, artist, album, date, energy, valence, danceability, instrumentalness, tempo
    FROM 
      acoustic_features
    WHERE
      (artist LIKE '%David Bowie%')
    """
    df = pd.read_sql(sql, con=conn)
    return df

def display_data(conn: Connection):
    st.dataframe(get_data(conn))

def main():
    db_conn = get_connection('./billboard-200.db') # connect to local db file
    display_data(db_conn) # display data from albums table

main()

