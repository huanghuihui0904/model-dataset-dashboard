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

    # Get column order from the database properties
    first_row_properties = data['results'][0]['properties']
    # column_order = list(first_row_properties.keys())  # Get the original column order from Notion
    column_order = list(first_row_properties.keys())[::-1]

    # Dynamically get column names from the database
    all_columns = {col_name: [] for col_name in column_order}  # Initialize columns in the correct order
    
    for row in data['results']:
        properties = row['properties']
        
        for col_name in column_order:
            col_value = properties[col_name]
            
            # Depending on the type of the property, retrieve the appropriate data
            if col_value['type'] == 'rich_text':
                all_columns[col_name].append(col_value['rich_text'][0]['text']['content'] if col_value['rich_text'] else "N/A")
            elif col_value['type'] == 'number':
                all_columns[col_name].append(col_value['number'] if col_value['number'] is not None else "N/A")
            elif col_value['type'] == 'select':
                all_columns[col_name].append(col_value['select']['name'] if col_value['select'] else "N/A")
            elif col_value['type'] == 'multi_select':
                all_columns[col_name].append(", ".join([opt['name'] for opt in col_value['multi_select']]) if col_value['multi_select'] else "N/A")
            elif col_value['type'] == 'title':
                all_columns[col_name].append(col_value['title'][0]['text']['content'] if col_value['title'] else "N/A")
            elif col_value['type'] == 'date':
                all_columns[col_name].append(col_value['date']['start'] if col_value['date'] else "N/A")
            elif col_value['type'] == 'checkbox':
                all_columns[col_name].append(col_value['checkbox'])
            else:
                all_columns[col_name].append("N/A")

    # Create a DataFrame from the extracted data, maintaining the correct column order
    
    df = pd.DataFrame(all_columns, columns=column_order)
    df = df.sort_values(by='Index')
    

    # Store the dataframe in the session state
    st.session_state.df = df
    logging.info("Data retrieved and formatted successfully.")
else:
    logging.error(f"Failed to retrieve data: {response.status_code}, {response.text}")
    st.write(f"Failed to retrieve data: {response.status_code}, {response.text}")

# Show app title and description
st.set_page_config(page_title="Model Dataset Dashboard", page_icon="📖")
col1, col2 = st.columns(2)
with col1:
    st.image("smu-logo.jpg", width=300)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("GovTechSg_True_Inline_Logo_3_Blue.jpg", width=300)
# st.image("smu-logo.jpg", width=50)  # Adjust the width as necessary
st.title("Model Dataset Dashboard")

# Show the existing dataset in a table with `st.data_editor`
if "df" in st.session_state:
    st.header("Dataset")

    # Show the editable DataFrame and allow editing
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
    )

    # Update the session state with the edited data
    st.session_state.edited_df = edited_df

    # Show only the edited DataFrame
    # st.subheader("Edited Data")
    # st.write(edited_df)