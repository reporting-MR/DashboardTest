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
from prophet import Prophet



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
data['Appts'] = pd.to_numeric(data['Appts'], errors='coerce').fillna(0).astype(int)
Appointments = data['Appts'].sum()

# Additional metrics
ctr = clicks / impressions
cvr = conversions / impressions
cpc = cost / conversions
cpa = cost / Appointments
L2A = Appointments / leads

col1, col2, col3 = st.columns(3)
with col1:
    st.write("Clicks, Impressions, and CTR")
    col11, col12, col13 = st.columns(3)
    col11.metric(label = "Total Impressions", value = impressions)
    col12.metric(label = "Total Clicks", value = clicks)
    col13.metric(label = "CTR", value = "{}%".format(round(ctr*100, 2)))

with col2:
    st.write("Leads, DQs, and CPL")
    col21, col22, col23 = st.columns(3)
    col21.metric(label = "Leads", value = leads)
    col22.metric(label = "DQs", value = round(DQs))
    col23.metric(label = "CPL", value = "{}$".format(round(CPL, 2)))

with col3:
    st.write("Appts, L2A, and CPA")
    col31, col32, col33 = st.columns(3)
    col31.metric(label = "Appointments", value = Appointments)
    col32.metric(label = "L2A", value = "{}%".format(round(L2A*100, 2)))
    col33.metric(label = "CPA", value = "{}$".format(round(cpa, 2)))

##### Line Charts Under Metrics #####
col4, col5, col6 = st.columns(3)

#Getting daily data

data['Date'] = pd.to_datetime(data['Date'])
numerical_columns = data.select_dtypes(include=['number']).columns

daily_sums = data.groupby(data['Date'].dt.date)[numerical_columns].sum()
daily_sums = daily_sums.reset_index()
daily_sums['CTR'] = daily_sums['Clicks'] / daily_sums['Impressions']
daily_sums['CPL'] = daily_sums['Cost'] / daily_sums['Number_of_reports__Salesforce_Reports']
daily_sums['CPA'] = daily_sums['Cost'] / daily_sums['Appts']

####Line Chart for Clicks and CTR
fig = go.Figure()
# Add a line trace for daily click sums
fig.add_trace(go.Scatter(x=daily_sums['Date'], y=daily_sums['Clicks'], mode='lines', name='Daily Clicks', yaxis='y'))
fig.add_trace(go.Scatter(x=daily_sums['Date'], y=daily_sums['CTR'], mode='lines', name='CTR', yaxis='y2'))
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

#### Line Chart for Leads and CPL
fig2 = go.Figure()
# Add a line trace for daily click sums
fig2.add_trace(go.Scatter(x=daily_sums['Date'], y=daily_sums['Number_of_reports__Salesforce_Reports'], mode='lines', name='Daily Leads', yaxis='y', line = dict(color="Red")))
fig2.add_trace(go.Scatter(x=daily_sums['Date'], y=daily_sums['CPL'], mode='lines', name='CPL', yaxis='y2', line=dict(color = 'orange')))
fig2.update_layout(
    title='Daily Leads and CPL',
    xaxis_title='Date',
    yaxis_title='Leads',
    yaxis2=dict(
        title='CPL ($)',
        overlaying='y',
        side='right',
        rangemode='tozero'  # Sets the secondary y-axis to start from 0
    )
)

#### Line Chart for Appts and CPA
fig3 = go.Figure()
# Add a line trace for daily click sums
fig3.add_trace(go.Scatter(x=daily_sums['Date'], y=daily_sums['Appts'], mode='lines', name='Daily Appts', yaxis='y', line = dict(color="Purple")))
fig3.add_trace(go.Scatter(x=daily_sums['Date'], y=daily_sums['CPA'], mode='lines', name='CPA', yaxis='y2', line=dict(color = 'Green')))
fig3.update_layout(
    title='Daily Appts and CPA',
    xaxis_title='Date',
    yaxis_title='Leads',
    yaxis2=dict(
        title='CPA ($)',
        overlaying='y',
        side='right',
        rangemode='tozero'  # Sets the secondary y-axis to start from 0
    )
)


with col4:
    st.plotly_chart(fig, use_container_width=True)

with col5: 
    st.plotly_chart(fig2, use_container_width=True)

with col6:
    st.plotly_chart(fig3, use_container_width=True)


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



query2 = '''SELECT * FROM `sunpower-375201.sunpower_agg.sunpower_full_funnel`'''
data2 = pandas.read_gbq(query2, credentials=credentials)

data2['Date'] = pd.to_datetime(data2['Date'])

# Group by date and sum 'Appointments' to get 'y'
data2['Appts'] = pd.to_numeric(data2['Appts'], errors='coerce').fillna(0).astype(int)
daily_aggregated = data2.groupby(data2['Date'].dt.date)['Appts'].sum().reset_index()
daily_aggregated.columns = ['ds', 'y']  # Rename columns

model = Prophet()
model.fit(daily_aggregated)

future = model.make_future_dataframe(periods=120)  # Forecast for 120 days into the future
forecast = model.predict(future)

# Create Plotly traces for the forecasted values, lower, and upper bounds
trace_forecast = go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast')
trace_lower = go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='none', name='Lower Bound')
trace_upper = go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill='tonexty', mode='none', name='Upper Bound')

# Create a Plotly figure
fig = go.Figure(data=[trace_forecast, trace_lower, trace_upper])

# Customize the layout
fig.update_layout(title='Prophet Forecast of Appointments w/ Confidence Interval', xaxis_title='Date', yaxis_title='Forecasted Appts')

# Display the Plotly chart in Streamlit
st.plotly_chart(fig)

#st.plot(model.plot(forecast))
