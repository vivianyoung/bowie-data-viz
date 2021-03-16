import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from sqlite3 import Connection
import requests
import json
import plotly.express as px

# spotify stuff
CLIENT_ID = ''
CLIENT_SECRET = ''

def get_spotify_token():
  url='https://accounts.spotify.com/api/token'
  grant_type = 'client_credentials'
  body_params = {'grant_type' : grant_type}

  r = requests.post(url, data=body_params, auth = (CLIENT_ID, CLIENT_SECRET))
  r.raise_for_status()

  token_raw = json.loads(r.text)
  token = token_raw["access_token"]

  return token

def spotify_search(song):
  token = get_spotify_token()
  url = f'https://api.spotify.com/v1/search?q={song}&type=track&limit=1'
  headers = {
    'Accept': 'application/json',
    'Content-type': 'application/json',
    'Authorization': f'Bearer {token}'
  }

  r = requests.get(url, headers=headers)
  r.raise_for_status()

  if r.status_code == 200:
    data = r.json()
    result = data['tracks']['items'][0]
    thirty_sec_preview_url = result['preview_url']
    return thirty_sec_preview_url
  else:
    raise Exception('Failed to get Spotify data.')

@st.cache(hash_funcs={Connection: id})  # add caching so we load the data only once
def get_connection(path_to_db):
  # connect to db
  try:
    conn = sqlite3.connect(path_to_db, check_same_thread=False)
    return conn
  except Exception as e:
    print(e)

def get_data(conn: Connection):
  sql_query = """
  SELECT 
    song, artist, album, date, energy, valence, danceability, instrumentalness, tempo
  FROM 
    acoustic_features 
  WHERE 
    artist LIKE '%David Bowie%'
  ORDER BY date DESC
  """
  df = pd.read_sql(sql_query, con=conn)
  df['date'] = pd.to_datetime(df['date'])
  return df

def get_bowie_data(conn: Connection,feature):
    df = pd.read_sql(f'select song, tempo,round({feature},2) as {feature},cast(valence*10 as int) as valence,date,album from acoustic_features where artist="David Bowie"', con=conn)
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_feature_avg(conn: Connection,feature):
	df = pd.read_sql(f'select song, date, album, round(avg({feature}),2) as avg_feature from acoustic_features where artist="David Bowie" group by album', con=conn)
	return df

def get_all_decade_avg(conn: Connection,feature):
	df = pd.read_sql(f'select * from (select album, date, substr(date, 1, 4) as year, substr(date, 1, 4) / 10 as ten_year_group,round(avg({feature}),2) avg_feature from acoustic_features where artist="David Bowie" group by 1, 2, 3) as source left join (select substr(date, 1, 4) / 10 as ten_year_group, round(avg({feature}),2) trend_feature from acoustic_features group by 1) as trend on trend.ten_year_group = source.ten_year_group', con=conn)
	#new_df_by_melt = pd.melt(df, id_vars=['year'], value_vars=['energy', 'danceability', 'instrumentalness', 'valence'], var_name='attr')
	return df

def display_data(conn: Connection):
  # st.dataframe(get_data(conn))
  if st.checkbox("display raw data"):
    st.dataframe(get_data(conn))
    
def remove_duplicates(df):
  song_list = []
  new_df = None

  i = 0
  for row in df.values:
    song_name = row[0]

    if '-' in song_name:
      song_name = song_name.split(' - ')[0]
      df.at[i, 'song'] = song_name # rewrite song name

    if song_name not in song_list:
      song_list.append(song_name)

      if new_df is None:
        new_df = df[i:i+1]
      else:
        new_df = pd.concat([new_df, df[i:i+1]])
    i += 1

  return new_df