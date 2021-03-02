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

###########################################################################################################
# picked = alt.selection_single() # single selection, xor
# # picked = alt.selection_single(empty='none') # single selection, default behavior is all not selected
# picked = alt.selection_single(on="mouseover", fields=["Species"]) # single selection, xor
# picked = alt.selection_multi() # multi selection, and
# picked = alt.selection_interval() # box around selection
# picked = alt.selection_interval(encodings=["x"]) # add selection interval along x-axis

# programmatic selections
# input_dropdown = alt.binding_select(options=["Adelie", "Chinstrap", "Gentoo"], name="Species of ...") # like html dropdown
# picked = alt.selection_single(encodings=["color"], bind=input_dropdown)

# scatterplot
# scatter = alt.Chart(df).mark_point().encode(
#   # note: variable names must match names from data table
#   alt.X("Flipper Length (mm)", scale=alt.Scale(zero=False)), # x-axis
#   alt.Y("Body Mass (g)", scale=alt.Scale(zero=False)), # y-axis
#   # alt.Color("Species")
#   color = alt.condition(picked, "Species:N", alt.value("lightgray")) # picked items are colored, otherwise gray
# ).add_selection(picked)

###########################################################################################################
# # add panning and zooming
# scatter = alt.Chart(df).mark_point().encode(
#   # note: variable names must match names from data table
#   alt.X("Flipper Length (mm)", scale=alt.Scale(zero=False)), # x-axis
#   alt.Y("Body Mass (g)", scale=alt.Scale(zero=False)) # y-axis
# )

# interval = alt.selection_interval(bind="scales")
# interval = alt.selection_interval(bind="scales", encodings=["x"]) # bind zooming to x-axis
# st.write(scatter.add_selection(interval))
###########################################################################################################

# show code for scatterplot
# with st.echo():
#   scatter = alt.Chart(df).mark_point().encode(
#     # note: variable names must match names from data table
#     alt.X("Flipper Length (mm)", scale=alt.Scale(zero=False)), # x-axis
#     alt.Y("Body Mass (g)", scale=alt.Scale(zero=False)), # y-axis
#     alt.Color("Species")
#   )

# st.write(scatter) # adds scatterplot to app

###########################################################################################################
# # add interactive slider for filtering data
# min_weight = st.slider("Minimum Weight", 2500, 6500)
# st.write(min_weight)

# # transform scatterplot 
# scatter_filtered = scatter.transform_filter(f"datum['Body Mass (g)']>= {min_weight}") # command string is in vega functional language
# st.write(scatter_filtered)
###########################################################################################################
# use a brush to generate a histogram based on brushed values
scatter = alt.Chart(df).mark_point().encode(
  # note: variable names must match names from data table
  alt.X("Flipper Length (mm)", scale=alt.Scale(zero=False)), # x-axis
  alt.Y("Body Mass (g)", scale=alt.Scale(zero=False)) # y-axis
)

brush = alt.selection_interval(encodings=["x"])
st.write(scatter.add_selection(brush) & alt.Chart(df).mark_bar().encode(
  alt.X("Body Mass (g)", bin=True),
  alt.Y("count()"),
  alt.Color("Species")
).transform_filter(brush))