import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pandas_gbq
import pandas 
from google.oauth2 import service_account
from google.cloud import bigquery
import statsmodels.api as sm
from plotly.subplots import make_subplots

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.

query = '''SELECT * FROM `sunpower-375201.sunpower_agg.sunpower_full_funnel` WHERE Date >= "2023-10-01" AND Date <= "2023-10-31"'''
data = pandas.read_gbq(query, credentials=credentials)

st.set_page_config(page_title="SunPower Overview Dash",page_icon="🧑‍🚀",layout="wide")

st.markdown("<h1 style='text-align: center; color: black;'>SunPower Overview Dash - Oct. 23rd</h1>", unsafe_allow_html=True)

# Collapsible data frame
with st.expander("Data Preview"):
    st.dataframe(data)

# Metrics
st.markdown("<h2 style='text-align: center; color: black;'>Metrics</h2>", unsafe_allow_html=True)
#st.subheader("Metrics")

# Number of Impressions, Clicks, and Conversions
impressions = data['Impressions'].sum()
clicks = data['Clicks'].sum()
conversions = data['Conversions'].sum()

col1, col2, col3 = st.columns(3)
col1.metric(label = "Total Impressions", value = impressions)
col2.metric(label = "Total Clicks", value = clicks)
col3.metric(label = "Total Conversions", value = conversions)

# Additional metrics
ctr = clicks / impressions
cvr = conversions / impressions
cpc = data['Cost'].sum() / conversions

col4, col5, col6 = st.columns(3)
col4.metric(label = "CTR", value = "{}%".format(round(ctr*100, 2)))
col5.metric(label = "CVR", value = "{}%".format(round(cvr*100, 2)))
col6.metric(label = "CPC", value = "{}$".format(round(cpc, 2)))

bottom_left_column, bottom_right_column = st.columns(2)

with bottom_left_column:
    # Pie chart showing Conversions by Campaign
    fig_pie = px.pie(data, names='State_Name', values='Cost', title='Cost by State')
    fig_pie.update_traces(textposition='inside')
    st.plotly_chart(fig_pie, use_container_width=True)

with bottom_right_column:
    # Scatter plot showing Conversions as a function of cost with a regression line
    fig_scatter = px.scatter(data, x ='Cost', y='Conversions', trendline='ols', title='Conversions vs Cost')
    st.plotly_chart(fig_scatter, use_container_width=True)

#Trying to get daily clicks
data['Date'] = pd.to_datetime(data['Date'])
daily_clicks = data.groupby(data['Date'].dt.date)['Clicks'].sum().reset_index()
#st.write(daily_clicks)

# Create the figure
fig = go.Figure()

# Add a line trace for daily click sums
fig.add_trace(go.Scatter(x=daily_clicks['Date'], y=daily_clicks['Clicks'], mode='lines', name='Daily Clicks'))
fig.update_layout(
    title='Daily Click Sums',
    xaxis_title='Date',
    yaxis_title='Clicks',
)
st.plotly_chart(fig, use_container_width=True)

