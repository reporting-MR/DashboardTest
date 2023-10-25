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


##### Getting the Data #####
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

st.markdown("<h1 style='text-align: center; color: black;'>SunPower Overview Dash - October</h1>", unsafe_allow_html=True)


##### Displaying the dashboard #####
# Collapsible data frame
with st.expander("Data Preview"):
    st.dataframe(data)

#### Metrics ####
st.markdown("<h2 style='text-align: center; color: black;'>Metrics</h2>", unsafe_allow_html=True)
#st.subheader("Metrics")

# Number of Impressions, Clicks, and Conversions
impressions = data['Impressions'].sum()
clicks = data['Clicks'].sum()
conversions = data['Conversions'].sum()
cost = data['Cost'].sum()
leads = data['Number_of_reports__Salesforce_Reports'].sum()
DQs = data['DQ'].sum()
CPL = cost/leads

# Additional metrics
ctr = clicks / impressions
cvr = conversions / impressions
cpc = data['Cost'].sum() / conversions

col1, col2, col3 = st.columns(3)
with col1:
    col11, col12, col13 = st.columns(3)
    col11.metric(label = "Total Impressions", value = impressions)
    col12.metric(label = "Total Clicks", value = clicks)
    col13.metric(label = "CTR", value = "{}%".format(round(ctr*100, 2)))

with col2:
    col21, col22, col23 = st.columns(3)
    col21.metric(label = "Leads", value = leads)
    col22.metric(label = "DQs", value = DQs)
    col23.metric(label = "CPL", value = "{}$".format(round(CPL, 2)))

with col3:
    col31, col32, col33 = st.columns(3)
    col31.metric(label = "Placeholder", value = clicks)
    col32.metric(label = "Placeholder", value = clicks)
    col33.metric(label = "Placeholder", value = clicks)

##### Line Charts Under Metrics #####

col4, col5, col6 = st.columns(3)

#Trying to get daily clicks
data['Date'] = pd.to_datetime(data['Date'])
daily_data = data.groupby(data['Date'].dt.date)['Clicks'].sum().reset_index()
daily_impressions = data.groupby(data['Date'].dt.date)['Impressions'].sum().reset_index()
daily_data['Impressions'] = daily_impressions['Impressions']
daily_data['CTR'] = daily_data['Clicks'] / daily_data['Impressions']
st.write(daily_data)

# Create the figure
fig = go.Figure()
# Add a line trace for daily click sums
fig.add_trace(go.Scatter(x=daily_data['Date'], y=daily_data['Clicks'], mode='lines', name='Daily Clicks', yaxis='y'))
fig.add_trace(go.Scatter(x=daily_data['Date'], y=daily_data['CTR'], mode='lines', name='CTR', yaxis='y2'))
fig.update_layout(
    title='Daily Clicks and CTR',
    xaxis_title='Date',
    yaxis_title='Clicks',
    yaxis2=dict(
        title='CTR (%)',
        overlaying='y',
        side='right',
        rangemode='tozero'  # Sets the secondary y-axis to start from 0
    )
)
with col4:
    st.plotly_chart(fig, use_container_width=True)

with col5: 
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.plotly_chart(fig, use_container_width=True)


### Bottom Charts ###
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

