import datetime
import random
import logging
import streamlit as st

# Streamlit logging (use st.write or st.error for logging in the web app)
st.write('Test log')

import altair as alt
import numpy as np
import pandas as pd
import requests
import json

# Your Notion API token and database ID
NOTION_TOKEN = "secret_Jz7xY1y67hkSdP7KXRw5cd4P6CLPXa9lHaZ7kUUF6Fb"
DATABASE_ID = "95d59953596a4574b5817f0300e9310f"

# The Notion API endpoint for querying a database
url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

# Headers for the API request
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Make the API request
response = requests.post(url, headers=headers)
data = {}

# Parse and print the response
if response.status_code == 200:
    data = response.json()

    # Prepare lists for DataFrame columns
    ids = []
    issues = []
    statuses = []
    priorities = []
    dates_submitted = []
    
    for i, row in enumerate(data['results']):
        properties = row['properties']
        
        # Extract values from Notion properties
        precision = properties['Precision']['rich_text'][0]['text']['content'] if properties['Precision']['rich_text'] else "N/A"
        recall = properties['Recall']['rich_text'][0]['text']['content'] if properties['Recall']['rich_text'] else "N/A"
        f1 = properties['F1']['rich_text'][0]['text']['content'] if properties['F1']['rich_text'] else "N/A"
        auc = properties['AUC']['rich_text'][0]['text']['content'] if properties['AUC']['rich_text'] else "N/A"
        remarks = properties['Remarks']['rich_text'][0]['text']['content'] if properties['Remarks']['rich_text'] else "N/A"
        
        # Concatenate all the values into a single line for the "Issue" column
        issue = f"Precision: {precision}, Recall: {recall}, F1: {f1}, AUC: {auc}, Remarks: {remarks}"
        
        # Generate random status, priority, and date (or you can extract them from Notion)
        status = random.choice(["Open", "In Progress", "Closed"])
        priority = random.choice(["High", "Medium", "Low"])
        date_submitted = datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
        
        # Append the data into respective lists
        ids.append(f"TICKET-{1100 - i}")
        issues.append(issue)
        statuses.append(status)
        priorities.append(priority)
        dates_submitted.append(date_submitted)

    # Create the data dictionary
    data = {
        "ID": ids,
        "Issue": issues,
        "Status": statuses,
        "Priority": priorities,
        "Date Submitted": dates_submitted,
    }

    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(data)

    # Display the DataFrame using Streamlit
    st.write(df)
else:
    st.error(f"Failed to retrieve data: {response.status_code}, {response.text}")


# Show app title and description.
st.set_page_config(page_title="Model Dataset Dashboard", page_icon="📖")
st.title("Model Dataset Dashboard")

# Show the existing DataFrame
if "df" not in st.session_state:
    # Save the DataFrame in the session state
    st.session_state.df = df

# Show section to view and edit existing tickets in a table.
st.header("Existing Model Dataset")
st.write(f"Number of logs: `{len(st.session_state.df)}`")

# Show the DataFrame and allow editing
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
    },
    disabled=["ID", "Date Submitted"],
)