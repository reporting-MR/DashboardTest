import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pandas_gbq
import pandas 
from google.oauth2 import service_account
from google.cloud import bigquery

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.

query = '''SELECT * FROM `sunpower-375201.sunpower_agg.sunpower_full_funnel` WHERE Date = "2023-10-19"'''
data = pandas.read_gbq(query, credentials=credentials)


# Collapsible data frame
st.dataframe(data)

# Metrics
st.subheader("Metrics")

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
cvr = conversions / clicks
cpc = data['Cost'].sum() / conversions

col4, col5, col6 = st.columns(3)
col4.metric(label = "CTR", value = ctr)
col5.metric(label = "CVR", value = cvr)
col6.metric(label = "CPC", value = cpc)


# Pie chart showing Conversions by Campaign
fig_pie = px.pie(data, names='Channel_Non_Truth', values='Cost', title='Conversions by Campaign')
fig_pie.update_traces(textposition='inside')
st.plotly_chart(fig_pie, use_container_width=True)

# Scatter plot showing Conversions as a function of cost with a regression line
fig_scatter = px.scatter(data, x='Costs', y='Conversions', trendline='ols', title='Conversions vs Cost')
st.plotly_chart(fig_scatter, use_container_width=True)
