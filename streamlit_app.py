import datetime
import random
import logging
import pandas as pd
import streamlit as st
import requests
import json

# Set up your API key and database ID
NOTION_API_KEY = "secret_Jz7xY1y67hkSdP7KXRw5cd4P6CLPXa9lHaZ7kUUF6Fb"
DATABASE_ID = "95d59953596a4574b5817f0300e9310f"

# Set up the API URL to query the database
url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

# Set up the headers
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Make a POST request to query the database
response = requests.post(url, headers=headers)

# Check the response status and process the results
if response.status_code == 200:
    data = response.json()

    # Prepare lists for DataFrame columns
    ids = []
    precisions = []
    recalls = []
    f1_scores = []
    aucs = []
    remarks_list = []
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
        
        # Generate random status, priority, and date (or you can extract them from Notion)
        status = random.choice(["Open", "In Progress", "Closed"])
        priority = random.choice(["High", "Medium", "Low"])
        date_submitted = datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
        
        # Append the data into respective lists
        ids.append(f"TICKET-{1100 - i}")
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        aucs.append(auc)
        remarks_list.append(remarks)
        statuses.append(status)
        priorities.append(priority)
        dates_submitted.append(date_submitted)

    # Create the data dictionary with each metric in its own column
    data = {
        "ID": ids,
        "Precision": precisions,
        "Recall": recalls,
        "F1": f1_scores,
        "AUC": aucs,
        "Remarks": remarks_list,
        "Status": statuses,
        "Priority": priorities,
        "Date Submitted": dates_submitted,
    }

    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(data)

    # Store the DataFrame in the session state for persistence
    st.session_state.df = df
    logging.info("Data retrieved and formatted successfully.")
else:
    logging.error(f"Failed to retrieve data: {response.status_code}, {response.text}")
    st.write(f"Failed to retrieve data: {response.status_code}, {response.text}")

# Show app title and description
st.set_page_config(page_title="Model Dataset Dashboard", page_icon="📖")
st.title("Model Dataset Dashboard")

# Show the existing dataset in a table with `st.data_editor`
if "df" in st.session_state:
    st.header("Existing Model Dataset")
    st.write(f"Number of logs: `{len(st.session_state.df)}`")

    # Show the DataFrame and allow editing for 'Status' and 'Priority' columns
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
        # Disable editing for the "ID" and "Date Submitted" columns
        disabled=["ID", "Date Submitted"],
    )

    # Store the edited DataFrame in session state for persistence
    st.session_state.edited_df = edited_df

    # Display the edited DataFrame below the table
    # st.subheader("Edited Data")
    # st.write(st.session_state.edited_df)