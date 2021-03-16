import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from sqlite3 import Connection
import plotly.express as px

from utils import *

st.write(f'spotify client id: {SPOTIFY_CLIENT_ID}')

def main():
  # use custom css
  with open('./styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

  db_conn = get_connection('./billboard-200.db') # connect to local db file
  df = get_data(db_conn)

  # title + intro
  # TODO: format title better
  st.title("Exploring the musical landscape of David Bowie")
  st.header("Introduction")
  st.write('In this project, we aim to visualize and explore the trends and evolution of acoustic features in David Bowie\'s work from 1969 to 2018 (posthumous releases included).')
  st.markdown('''We started with a large dataset (containing ~340,000 rows) that comprised of various features of albums and songs from the Billboard Top 200 through the decades. 
              After exploring the data, we were mostly intrigued by the following features of each row in our data set: the danceability, energy, tempo, and valence of each work.
              This led us to the realization that with about half a century of data and a sizable list of features to analyze, what we most wanted to visualize was the evolution and 
              musical tendencies of artists with incredible diversity in their work.<br><br>With that goal in mind, we chose <strong>David Bowie</strong> for his extensive and musically-divergent career.
              Bowie is well-known for his eccentric music styles and wide-reaching influence from his start in the 60s to his death in 2016.
          ''', unsafe_allow_html=True)
  st.write('This project consists of three parts:')
  st.markdown('''
              <ul id="project-parts-list">
              <li><a class="link" href="#charts">Charts allowing for visualization of acoustic features in the songs and the distributions of such features in various albums</a></li>
              <li><a class="link" href="#comparison">Comparison of the acoustic features in David Bowie albums vs. the overall features in other works by decade</a></li>
              <li><a class="link" href="#search">An interactive music search feature that allows users to retrieve a list of recommended Bowie songs with selected acoustic features</a></li>
              </ul>
              ''', unsafe_allow_html=True)
  st.write("""
            Ultimately, our analysis results aim to provide a different view of interpreting David Bowie's work. Moreover, besides searching for particular songs or albums in a traditional music search engine 
            which often requires users to already have a song name in mind, how might we allow users find the work that better fits the context and mood they have in mind?
          """)
  st.markdown("<span class='small'>This project was completed by <strong>Vivian Young</strong> and <strong>Carol Ho</strong> for the Interactive Data Science (Spring 2021) course taught by Professors Adam Perer and Hendrik Strobelt.</span>", unsafe_allow_html=True)
  st.write("The original dataset: https://components.one/datasets/billboard-200/")

  #checkbox-original dataset
  if st.checkbox('show original dataset'):
    st.text('original data set - accoustic features of songs of David Bowie from 1969-2018')
    st.dataframe(df)
    st.markdown("```SELECT * FROM EMP JOIN DEPT ON EMP.DEPTNO = DEPT.DEPTNO;```")
  
  #Paragraph-Intro to Features
  st.header("Intro to acoustic features")
  st.write("Spotify includes various acoustic features of tracks in order to maximize recommendation results. We picked the below features based on relevancy to the use-case of a music listener.")

  st.markdown(":point_right:Danceability: Describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity.")
  st.markdown(":point_right:Energy: Represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale.")
  st.markdown(":point_right:Instrumentalness: Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”.")
  st.markdown(":point_right:Tempo: The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece, and derives directly from the average beat duration.")
  st.markdown(":point_right:Valence: Describes the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).")

  st.write("The full list of features can be found here: https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/")

  #select-feature
  option = st.selectbox(
  'Which acoustic feature do you want to explore?',
  ('danceability', 'energy', 'instrumentalness'))

  #connection config
  all_dacade_avg = get_all_decade_avg(db_conn, option)
  bowie_data = get_bowie_data(db_conn, option)

  #Paragrah-Chart 1
  st.markdown("<div id='charts'>", unsafe_allow_html=True)
  st.header("Scatter Chart - David Bowie's albums")
  st.subheader(":musical_note: How does the selected feature shape the distribution of songs by album?")
  st.markdown("Instructions: The slider allows you to zoom in albums by year and clicking on the valence allows you to see the distribution of songs from high valence (happy) to low valence (sad).")

  #slider-year
  start_year = st.slider("Show me albums released within these years!", 1969, 2018, (1969,2000))
  filtered_data1 = bowie_data[start_year[0] < bowie_data['date'].dt.year]
  filtered_data2 = filtered_data1[filtered_data1['date'].dt.year <= start_year[1]]
  select_scatter = alt.selection_multi(fields=['valence'], bind='legend') 

  #color palette for scatter chart
  range_ = ['#D64550', '#EE8189', '#FC8B4A','#F7B801','#B9F18C','#71DA1B','#439A86','#00BECC','#7678ED','#3D348B']

 	#chart-scatter
  scatter = alt.Chart(filtered_data2).mark_circle().encode(
  alt.X('album',scale=alt.Scale(zero=True), sort={"field": "date", "order": "ascending"},title="Albums order by Issued Date"),
  alt.Y(option,scale=alt.Scale(zero=True), title=option),
  alt.Color('valence:O',
    sort='descending',scale=alt.Scale(range=range_)),
    tooltip=['album','song','date', option, 'valence', 'tempo'],
    size=alt.Size('tempo',
    scale=alt.Scale(domain=[0,100], range=[1,200]),
    legend=alt.Legend(values=[50,100,150,200])),
    opacity=alt.condition(select_scatter, alt.value(1), alt.value(0.1))
  ).properties(
    width=900,
    height=900
  ).add_selection(
    select_scatter
  )
  st.write(scatter) # TODO: fix sizing of scatter chart

  #checkbox-bowie's album
  if st.checkbox('show original dataset',key='album'):
    st.text('original data set - accoustic features of songs from 1969-2018')
    st.dataframe(bowie_data)

  #Paragrah-Chart 2
  st.markdown("<div id='comparison'>", unsafe_allow_html=True)
  st.header("Bar Chart - David Bowie's albums with average features")
  st.subheader(":musical_note: How do the acoustic features of Bowie's albums differ from other songs in that decade?")
  st.markdown("Instructions: Click on the checkbox to compare with other songs from that decade. Click on the bar to highlight.")

  #chart-bar
  selector = alt.selection_single(empty='all', fields=['album'])    

  # TODO: fix chart sizing
  bar_album = alt.Chart(all_dacade_avg).mark_bar(color='#1FC3AA', opacity=0.5, thickness=10).encode(
    alt.X('album',
      sort={"field": "date", "order": "ascending"},
      title="(B)Albums order by Issued Date"),
    alt.Y('avg_feature',
      scale=alt.Scale(zero=False),
      title='(B)Average_'+ option +'_by_Albums'),
      tooltip=['album', 'date', 'avg_feature'],
      color=alt.condition(selector, 'album:O', alt.value('lightgray'), legend=None),
  ).properties(
    width=850,
    height=600
  ).add_selection(selector)

  #chart-decade-the numbers
  #chart-decade
  bar_decade = alt.Chart(all_dacade_avg).mark_bar(color='#8624F5', opacity=0.5, thickness=10).encode(
    alt.X('album',
      sort={"field": "date", "order": "ascending"},
      title="(V)The correspondent decade of albums Issued Date"),
    alt.Y('trend_feature',
      scale=alt.Scale(zero=False),
      title='(V)Average_'+ option +'_by_Decade')
	).properties(
    width=850,
    height=600
  )#.add_selection(selector)
  
  #chart-decade-the numbers
  text_decade = bar_decade.mark_text(align='center', color='white',dy=80).encode(
    text='avg_feature:N'
	)
    
  #checkbox-chart comparison
  agree = st.checkbox('Compare the\n'+option+'\nof the albums with the average\n'+option+'\nof songs by decede.')
  if agree:
    st.write(bar_decade+bar_album+text_decade)
  else:
    st.write(bar_album)

  agree = st.checkbox('show original dataset',key='decade')
  if agree:
    st.text('David Bowie album average feature and all songs averge feature by decade')
    st.dataframe(all_dacade_avg)

  ################################################
  # music search
  st.markdown("<div id='search'>", unsafe_allow_html=True)
  st.header("Acoustic feature song search")
  st.subheader(":musical_note: Which David Bowie songs fit my mood?")
  st.markdown("Instructions: Follow the prompts and tune the sliders for energy, valence, danceability, and instrumentalness to find recommended David Bowie songs. Click on the recommended songs in the list to hear a 30-second preview of the track.")

  st.text("") # blank line for separation
  st.text("") # blank line for separation

  # decades / year range
  st.write('First, choose your decade(s) / year range:')
  decades = st.slider(
    'year',
    1963, 2019, (1970, 1979)
  )

  # parse years as full dates for sql query purposes
  for year_boundary in decades:
    year_boundary = f'{year_boundary}/01/01'

  st.text("") # blank line for separation
  st.text("") # blank line for separation
  
  st.write('Secondly, how ...')
  # energy
  st.write('energetic?')
  energy = st.slider("energy", 0.0, 1.0, (0.5,1.0))

  # valence
  st.write('positive / happy?')
  valence = st.slider("valence", 0.0, 1.0, (0.5,1.0))

  # danceability
  st.write('danceable?')
  danceability = st.slider("danceability", 0.0, 1.0, (0.5,1.0))

  st.text("") # blank line for separation
  st.text("") # blank line for separation

  # sort by
  st.write('Lastly, choose an acoustic feature to prioritize:')
  sort_by = st.selectbox(
    'prioritize',
    ('energy', 'valence', 'danceability', 'date')
  )

  st.text("") # blank line for separation
  st.text("") # blank line for separation

  # show results button
  # if st.button('show me my music!'):
  sql_query = f"""
    SELECT
      song, artist, album, date, energy, valence, danceability
    FROM 
      acoustic_features
    WHERE
      (artist LIKE '%David Bowie%') AND
      (date BETWEEN {decades[0]} AND {decades[1]}) AND
      (energy BETWEEN {energy[0]} AND {energy[1]}) AND
      (valence BETWEEN {valence[0]} AND {valence[1]}) AND
      (danceability BETWEEN {danceability[0]} AND {danceability[1]})
    ORDER BY {sort_by} DESC
  """
  df = pd.read_sql(sql_query, con=db_conn)

  # check if there are any results
  if len(df.index) == 0:
    st.write('error: no songs were found with your constraints. please try again!')
  else:
    df = remove_duplicates(df.head(10))

    chart = px.bar(
      df,
      x='song',
      y=['energy','valence','danceability'],
      barmode='group',
      height=500
    )

    st.plotly_chart(chart)

    st.markdown("<br>Your top recommendations:<br>", unsafe_allow_html=True)
    for row in df.values:
      song = row[0]
      album = row[2]
      date = row[3]
      if '-' in date:
        date = date.split('-')[0]

      try:
        # get spotify preview
        preview_url = spotify_search(f'{song} david bowie')

        st.markdown(f'''
          <a class="rec-link" href="{preview_url}" target="_blank">
            <span id="song-name">{song}</span><span id="song-details"> - {album} ({date})</span>
          </a>
        ''', unsafe_allow_html=True)
      except Exception:
        st.markdown(f'''
          <div class="rec-link">
            <span id="song-name">{song}</span><span id="song-details"> - {album} ({date})</span>
          </div>
        ''', unsafe_allow_html=True)



main()
