import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from sqlite3 import Connection

@st.cache(hash_funcs={Connection: id})  # add caching so we load the data only once
def get_connection(path_to_db):
    # connect to db
    try:
        conn = sqlite3.connect(path_to_db, check_same_thread=False)
        return conn
    except Exception as e:
        print(e)

def get_data(conn: Connection,table_name):
    df = pd.read_sql(f'SELECT * FROM {table_name} where artist="David Bowie"', con=conn)
    return df
def get_bowie_data(conn: Connection,feature):
    df = pd.read_sql(f'select song, tempo,{feature},cast(valence*10 as int) as valence,date,album from acoustic_features where artist="David Bowie"', con=conn)
    df['date'] = pd.to_datetime(df['date'])
    return df
def get_feature_avg(conn: Connection,feature):
	df = pd.read_sql(f'select song, date, album, avg({feature}) as avg_feature from acoustic_features where artist="David Bowie" group by album', con=conn)
	return df

def get_all_decade_avg(conn: Connection,feature):
	df = pd.read_sql(f'select * from (select album, date, substr(date, 1, 4) as year, substr(date, 1, 4) / 10 as ten_year_group,avg({feature}) avg_feature from acoustic_features where artist="David Bowie" group by 1, 2, 3) as source left join (select substr(date, 1, 4) / 10 as ten_year_group, avg({feature}) trend_feature from acoustic_features group by 1) as trend on trend.ten_year_group = source.ten_year_group', con=conn)
	#new_df_by_melt = pd.melt(df, id_vars=['year'], value_vars=['energy', 'danceability', 'instrumentalness', 'valence'], var_name='attr')
	return df
    
    
def main():
    #connection config
    db_conn = get_connection('./billboard-200.db')
    all_data = get_data(db_conn, 'acoustic_features')    
    
    #Paragrah-Intro
    st.title("Explore the acoustic and meta features of albums and songs by David Bowie")
    st.header("Introduction")
    st.write("This 3-week project is for the Interactive Data Science - (Spring 2021) course under Adam Perer and Hendrik Strobelt, created by Vivian Young and Carol Ho. After navigating the Acoustic and meta-features of albums and songs data from Spotify, with 340,000 rows containing acoustic data for tracks from Billboard 200 albums from 1/5/1963 to 1/19/2019. We're intrigued by the feature label on each piece - the danceability, the energy, the beats, and the valence. To better explore the feature label's trend and distribution, we decided on David Bowie's work. They are well-known for their diverse music styles, and their creation has been influential since the 60s till now.")
    st.write("The project consists of three parts; the first is the charts that allow the user to read each song's features and how albums distribute these features. The second part is a comparison of the albums' features with the overall music features by decade. With the holistic understanding of Bowie's work, the last part is an interactive search function that allows the users to search for their music by features.")
    st.write(" The analysis results aim to provide a different view of interpreting the albums and songs. Moreover, besides searching for particular songs or albums, how might we help users find the pieces that better fit the context and mood?")
    st.write("The original dataset: https://components.one/datasets/billboard-200/")
    
    #checkbox-original dataset
    agree = st.checkbox('show original data.(David Bowie)')
    if agree:
        st.text('original data set - accoustic features of songs of David Bowie from 1969-2018')
        st.dataframe(all_data)
        st.markdown("```SELECT * FROM EMP JOIN DEPT ON EMP.DEPTNO = DEPT.DEPTNO;```")
    
    #Paragraph-Intro to Features
    st.header("Intro to Features")
    st.write("Spotify labeled the songs with features to maximize the recommendation result. We picked the below features that are more relevant to the use-case of a music listener.")
    st.markdown(":point_right:Danceability: Describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity.")
    st.markdown(":point_right:Energy: Represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale.")
    st.markdown(":point_right:Instrumentalness: Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”.")
    st.markdown(":point_right:Tempo: The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece, and derives directly from the average beat duration.")
    st.markdown(":point_right:Valence: Describes the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).")
    
    #select-feature
    option = st.selectbox(
    'What feature are you interested in dicover?',
    ('danceability', 'energy', 'instrumentalness'))

    #connection config
    all_dacade_avg = get_all_decade_avg(db_conn, option)
    bowie_data = get_bowie_data(db_conn,option)
    
    #Paragrah-Chart 1
    st.header("Scatter Chart-David Bowie's albums")
    st.subheader(":musical_note: How the selected feature shapes the distribution of songs by album?")
    st.markdown("Instruction: The slider allows you to zoom in albums by issued year, and clicking on the valence allows you to see the distribution of songs, from high valence(Happy) to low valence(Sad).")

    #slider-year
    start_year = st.slider("Show me the albums within these issued year!", 1969, 2018, (1969,2000))
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
    width=1200,
    height=900,
    ).add_selection(
    select_scatter
)
    st.write(scatter)
    #checkbox-bowie's album
    agree = st.checkbox('show original dataset.',key='album')
    if agree:
        st.text('original data set - accoustic features of songs from 1969-2018')
        st.dataframe(bowie_data)

    #Paragrah-Chart 2
    st.header("Bar Chart-David Bowie's albums with average features")
    st.subheader(":musical_note: How is the feature of the album different from the songs in that decade?")
    st.markdown("Instruction: Click on the checkbox to open the overlay bar chart to compare. Click on the bar for highlight.")


    #chart-bar
    selector = alt.selection_single(empty='all', fields=['album'])    

    bar_album = alt.Chart(all_dacade_avg).mark_bar(color='#1FC3AA', opacity=0.5, thickness=10).encode(
    alt.X('album',sort={"field": "date", "order": "ascending"},title="(B)Albums order by Issued Date"),
    alt.Y('avg_feature',scale=alt.Scale(zero=False),title='(B)Average_'+ option +'_by_Albums'),
    tooltip=['album', 'date', 'avg_feature'],
    color=alt.condition(selector, 'album:O', alt.value('lightgray'), legend=None),
).properties(
    width=1200,
    height=600,
    ).add_selection(selector)

  	#chart-decade
    bar_decade = alt.Chart(all_dacade_avg).mark_bar(color='#8624F5', opacity=0.5, thickness=10).encode(
    alt.X('album',sort={"field": "date", "order": "ascending"},title="(V)The correspondent decade of albums Issued Date"),
    alt.Y('trend_feature',scale=alt.Scale(zero=False), title='(V)Average_'+ option +'_by_Decade'),
	).properties(
    width=1200,
    height=600,
    )#.add_selection(selector)
    
    text = bar_decade.mark_text(align='center').encode(
    text='trend_feature:N'
	)
    
    #checkbox-chart comparison
    agree = st.checkbox('Compare the\n'+option+'\nof the albums with the average\n'+option+'\nof songs by decede.')
    if agree:
    	st.write(bar_decade+bar_album)
    else:
        st.write(bar_album)
	
    agree = st.checkbox('show original dataset.',key='decade')
    if agree:
        st.text('David Bowie album average feature and all songs averge feature by decade')
        st.dataframe(all_dacade_avg)
    
    #Paragrah-Search
    st.header("Search with features!")
    st.subheader(":musical_note: What are the songs that fit my mood?")
    st.markdown("Instruction: blablabla.")

main()
