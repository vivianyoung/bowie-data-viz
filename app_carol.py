import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from sqlite3 import Connection

st.title("Acoustic and meta features of albums and songs analysis - David Bowie")
st.write("")

@st.cache(hash_funcs={Connection: id})  # add caching so we load the data only once
def get_connection(path_to_db):
    # connect to db
    try:
        conn = sqlite3.connect(path_to_db, check_same_thread=False)
        return conn
    except Exception as e:
        print(e)

def get_data(conn: Connection,table_name):
    df = pd.read_sql(f'SELECT * FROM {table_name} WHERE artist= "David Bowie"', con=conn)
    return df
def get_bowie_data(conn: Connection,feature):
    df = pd.read_sql(f'select song, tempo,{feature},cast(valence*10 as int) as valence,date,album from acoustic_features where artist="David Bowie"', con=conn)
    df['date'] = pd.to_datetime(df['date'])
    return df
def get_feature_avg(conn: Connection,feature):
	df = pd.read_sql(f'select song, date, album, avg({feature}) as avg_feature from acoustic_features where artist="David Bowie" group by album', con=conn)
	return df
def get_album_feature_avg(conn: Connection):
	df = pd.read_sql(f'select date , album, avg(energy) as energy, avg(danceability) as danceability, avg(instrumentalness) as instrumentalness,avg(valence) as valence from acoustic_features where artist="David Bowie" group by album', con=conn)	
	#new_df_by_stack = df.set_index(['date', 'album']).stack().reset_index().rename(columns={'level_2': 'attr', 0: 'value'})
	new_df_by_melt = pd.melt(df, id_vars=['date', 'album'], value_vars=['energy', 'danceability', 'instrumentalness', 'valence'], var_name='attr')

	return new_df_by_melt

def get_all_decade_avg(conn: Connection,feature):
	df = pd.read_sql(f'select * from (select album, date, substr(date, 1, 4) as year, substr(date, 1, 4) / 10 as ten_year_group,avg({feature}) avg_feature from acoustic_features where artist="David Bowie" group by 1, 2, 3) as source left join (select substr(date, 1, 4) / 10 as ten_year_group, avg({feature}) trend_feature from acoustic_features group by 1) as trend on trend.ten_year_group = source.ten_year_group', con=conn)
	#new_df_by_melt = pd.melt(df, id_vars=['year'], value_vars=['energy', 'danceability', 'instrumentalness', 'valence'], var_name='attr')
	return df

def display_data(conn: Connection, table_name):
    # if st.checkbox("display data"):
    #     st.dataframe(get_data(conn, table_name))
    st.dataframe(get_data(conn, table_name))

#def dropdown_input(value)
    
    
def main():
    range_ = ['#D64550', '#EE8189', '#FC8B4A','#F7B801','#B9F18C','#71DA1B','#439A86','#00BECC','#7678ED','#3D348B']
    option = st.selectbox(
    'What feature are you interested in dicover?',
    ('energy', 'danceability', 'instrumentalness'))
    st.write('You selected:', option )
    db_conn = get_connection('./billboard-200.db')
    all_data = get_data(db_conn, 'acoustic_features')
    alb_feature_avg = get_feature_avg(db_conn, option)
    all_dacade_avg = get_all_decade_avg(db_conn, option)
    bowie_data = get_bowie_data(db_conn,option)
    alb_avg = get_album_feature_avg(db_conn) 
    start_year = st.slider("Show me the albums within these issued year!", 1969, 2018, (1969,2000))
    st.write(start_year[1])
    filtered_data1 = bowie_data[start_year[0] < bowie_data['date'].dt.year]
    filtered_data2 = filtered_data1[filtered_data1['date'].dt.year <= start_year[1]]
    select_scatter = alt.selection_multi(fields=['valence'], bind='legend')
 	#chart
    scatter = alt.Chart(filtered_data2).mark_circle().encode(
    alt.X('album',scale=alt.Scale(zero=True), sort={"field": "date", "order": "ascending"},title="Albums order by Issued Date"),
    alt.Y(option,scale=alt.Scale(zero=True), title=option),
    alt.Color('valence:N',
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


    selector = alt.selection_single(empty='all', fields=['album'])    
    #point chart
    base = alt.Chart(all_dacade_avg).properties(
    width=1200,
    height=600
	).add_selection(selector)
    
    bar_album = base.mark_bar(color='#1FC3AA', opacity=0.5, thickness=10).encode(
    alt.X('album',sort={"field": "date", "order": "ascending"},title="(B)Albums order by Issued Date"),
    alt.Y('avg_feature',scale=alt.Scale(zero=False),title='(B)Average_'+ option +'_by_Albums'),
    tooltip=['album', 'date', 'avg_feature'],
    color=alt.condition(selector, 'album:O', alt.value('lightgray'), legend=None),
).properties(
    width=1200,
    height=600,
    )
  	#decade chart
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
    agree = st.checkbox('Compare the'+option+'of the albums with the average level of songs by decede.')
    #st.write(bar_decade)
    if agree:
    	st.write(bar_decade+bar_album)
    else:
        st.write(bar_album)
	


    st.text('original data set - accoustic features of songs from 1969-2018')
    display_data(db_conn, 'acoustic_features')
    st.text('David Bowie album accoustic features from 1969-2018')
    #dataset
    st.dataframe(alb_feature_avg)
    st.dataframe(all_dacade_avg)

main()
