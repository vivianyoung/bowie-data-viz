import streamlit as st
import pandas as pd
import altair as alt

import sqlite3
from sqlite3 import Connection

st.title("billboard data analysis")

@st.cache(hash_funcs={Connection: id})  # add caching so we load the data only once
def get_connection(path_to_db):
    # connect to db
    try:
        conn = sqlite3.connect(path_to_db, check_same_thread=False)
        return conn
    except Exception as e:
        print(e)

def get_data(conn: Connection, table_name):
    df = pd.read_sql(f'SELECT * FROM {table_name}', con=conn)
    return df

def display_data(conn: Connection, table_name):
    # if st.checkbox("display data"):
    #     st.dataframe(get_data(conn, table_name))
    st.dataframe(get_data(conn, table_name))

def main():
    db_conn = get_connection('./billboard-200.db')
    # db_conn = get_connection('https://www.dropbox.com/s/ahog97hcatpiddk/billboard-200.db')
    display_data(db_conn, 'albums')

main()

# st.write("Hmm 🤔, is there some correlation between body mass and flipper length? Let's make a scatterplot with [Altair](https://altair-viz.github.io/) to find.")

# chart = alt.Chart(df).mark_point().encode(
#     x=alt.X("body_mass_g", scale=alt.Scale(zero=False)),
#     y=alt.Y("flipper_length_mm", scale=alt.Scale(zero=False)),
#     color=alt.Y("species")
# ).properties(
#     width=600, height=400
# ).interactive()

# st.write(chart)


