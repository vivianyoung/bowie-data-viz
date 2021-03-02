# to start local streamlit app, run this command in the terminal:
# $ streamlit run practice.py

import streamlit as st 
import pandas as pd
import altair as alt 

st.write("Hello world!") # adds line of text
st.header("My first StreamlitApp") # adds header text

@st.cache
def load(url):
  """
  This function loads the json from a given url so that we are caching the data, preventing delays in interaction.
  """
  return pd.read_json(url)

# get json from online dataset
df = load("https://cdn.jsdelivr.net/npm/vega-datasets@2/data/penguins.json")

# create checkbox (default = unchecked), if checked, raw data table is rendered
if st.checkbox("Show me the raw data"):
  st.write(df)

# show code for scatterplot
with st.echo():
  scatter = alt.Chart(df).mark_point().encode(
    # note: variable names must match names from data table
    alt.X("Flipper Length (mm)", scale=alt.Scale(zero=False)), # x-axis
    alt.Y("Body Mass (g)", scale=alt.Scale(zero=False)), # y-axis
    alt.Color("Species")
  )

# st.write(scatter) # adds scatterplot to app

# add interactive slider for filtering data
min_weight = st.slider("Minimum Weight", 2500, 6500)
st.write(min_weight)

# transform scatterplot 
scatter_filtered = scatter.transform_filter(f"datum['Body Mass (g)']>= {min_weight}") # command string is in vega functional language
st.write(scatter_filtered)