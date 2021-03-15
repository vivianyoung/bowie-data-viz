import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from sqlite3 import Connection
import plotly.express as px

# add title to streamlit app
st.title("music data analysis")
st.header("how have acoustic features in david bowie's music changed over time?")

st.text("") # blank line for separation
st.text("")

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

def display_data(conn: Connection):
  # st.dataframe(get_data(conn))
  if st.checkbox("display raw data"):
    st.dataframe(get_data(conn))

def main():
  db_conn = get_connection('./billboard-200.db') # connect to local db file
  # display_data(db_conn) # display data from albums table

  # add dropdown list for column
  column_option = st.selectbox(
    'which acoustic feature do you want to explore?',
    ('energy', 'valence', 'danceability', 'instrumentalness', 'tempo')
  )

  df = get_data(db_conn)

  # add interactive slider for filtering by year
  start_year = st.slider("starting year", 1969, 2018, 1969)

  filtered_data = df[df['date'].dt.year >= start_year]
  if st.checkbox("display raw data"):
    st.write(filtered_data)

  scatter = alt.Chart(filtered_data).mark_point().encode(
    alt.X('date', scale=alt.Scale(zero=False)),
    alt.Y(column_option, scale=alt.Scale(zero=True)),
    color = alt.Y('album')
  ).properties(
    width=800, height=600
  ).interactive()

  st.write(scatter)

  ################################################
  # music search
  st.header('music search')
  st.write('find ten songs with your desired acoustic features')

  st.text("") # blank line for separation
  st.text("") # blank line for separation

  # decades / year range
  st.write('first, choose your decade(s) / year range')
  decades = st.slider(
    'year',
    1963, 2019, (1970, 1979)
  )

  # parse years as full dates for sql query purposes
  for year_boundary in decades:
    year_boundary = f'{year_boundary}/01/01'

  st.text("") # blank line for separation
  st.text("") # blank line for separation
  st.text("") # blank line for separation
  
  st.write('secondly, how ...')
  # energy
  st.write('energetic?')
  energy = st.slider("energy", 0.0, 1.0, (0.75,1.0))

  # valence
  st.write('positive / happy?')
  valence = st.slider("valence", 0.0, 1.0, (0.75,1.0))

  # danceability
  st.write('danceable?')
  danceability = st.slider("danceability", 0.0, 1.0, (0.75,1.0))

  # instrumentalness
  st.write('instrumental?')
  instrumentalness = st.slider("instrumentalness", 0.0, 1.0, (0.0,0.5))

  # tempo
  st.write('fast?')
  tempo = st.slider("tempo", 0, 250, (100,250))

  # sort by
  sort_by = st.selectbox(
    'sort by',
    ('energy', 'valence', 'danceability', 'instrumentalness', 'tempo', 'date')
  )

  st.text("") # blank line for separation
  st.text("") # blank line for separation

  # show results button
  # if st.button('show me my music!'):
  sql_query = f"""
    SELECT 
      song, artist, album, date, energy, valence, danceability, instrumentalness, tempo
    FROM 
      acoustic_features 
    WHERE 
      (date BETWEEN {decades[0]} AND {decades[1]}) AND
      (energy BETWEEN {energy[0]} AND {energy[1]}) AND
      (valence BETWEEN {valence[0]} AND {valence[1]}) AND
      (danceability BETWEEN {danceability[0]} AND {danceability[1]}) AND
      (instrumentalness BETWEEN {instrumentalness[0]} AND {instrumentalness[1]}) AND
      (tempo BETWEEN {tempo[0]} AND {tempo[1]})
    ORDER BY {sort_by} DESC
  """
  df = pd.read_sql(sql_query, con=db_conn)

  st.dataframe(df[0:10])
  # print(df.head(10))

  # chart = alt.Chart(df.head(10)).mark_bar().encode(
  #   alt.X('song', scale=alt.Scale(zero=False)),
  #   alt.Color('energy', 'valence', 'danceability', 'instrumentalness')
  # )

  chart = px.bar(
    df.head(10),
    x='song',
    y=['energy','valence','danceability','instrumentalness'],
    barmode='group',
    height=500
  )

  st.plotly_chart(chart)

main()
