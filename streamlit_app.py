import datetime
import random
import logging
import pandas as pd
import streamlit as st
import requests
import json

# Set up your API key and database ID
NOTION_API_KEY = "secret_Jz7xY1y67hkSdP7KXRw5cd4P6CLPXa9lHaZ7kUUF6Fb"
DATABASE_ID = "100405e87d9a800997ace1eee578c2b3"

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
    column_order = list(first_row_properties.keys())[::-1]

    # Dynamically get column names from the database
    all_columns = {col_name: [] for col_name in column_order}
    
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

# Set up page configuration
st.set_page_config(page_title="Model Dataset Dashboard", page_icon="govtech-icon.png")

# Sidebar navigation
page = st.sidebar.selectbox("Select a page", ["Homepage", "Dataset"])




# Homepage content
if page == "Homepage":
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("smu-logo.jpg", width=300)

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("GovTechSg_True_Inline_Logo_3_Blue.jpg", width=300)

    st.title("Welcome to the Model Dataset Dashboard!")
    st.write("This is the homepage of the dashboard, where you can explore different datasets and visualizations.")
    
    # Add more homepage content (e.g., introductory text, links, etc.)
    # st.markdown("""
    # ### Key Features
    # - Explore datasets.
    # - Analyze data trends.
    # - View results and insights.
    # """)

# Dataset page content
elif page == "Dataset":
    st.title("Model Dataset")

    if "df" in st.session_state:
        st.header("Dataset")

        # # Add an ID column if it doesn't already exist (optional, for tracking purposes)
        # if 'ID' not in st.session_state.df.columns:
        #     st.session_state.df.insert(0, 'ID', range(1, len(st.session_state.df) + 1))

        # Highlight the total number of logs (rows)
        total_logs = len(st.session_state.df)
        st.markdown(
            f"""
            <div style="font-size: 20px;">
                Total Number of Logs: <span style="color: #007BFF; background-color: #e0f7fa; padding: 5px 10px; border-radius: 5px;">{total_logs}</span>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Reset the Pandas internal index to start from 1 instead of 0
        st.session_state.df = st.session_state.df.reset_index(drop=True)  # Drop the original index
        st.session_state.df.index += 1  # Start index from 1

        # Define default columns to show (including Pandas internal index, if desired)
        default_columns = ['Index', 'Data', 'Name', 'Settings', 'F1', 'F0.3', 'Precision', 'Recall']

        # Allow the user to select which columns to display, default to your specified columns
        selected_columns = st.multiselect(
            "Select columns to display",
            options=st.session_state.df.columns.tolist(),
            default=[col for col in default_columns if col in st.session_state.df.columns]  # Only keep valid columns
        )

        # Show only the selected columns
        filtered_df = st.session_state.df[selected_columns]

        # Show the editable DataFrame with Pandas internal index visible and sorted by index
        edited_df = st.data_editor(
            filtered_df,
            use_container_width=True,
            hide_index=False  # Show the Pandas internal index (row numbers)
        )

        # Update the session state with the edited data
        st.session_state.edited_df = edited_df

        # Optionally show edited data
        # st.subheader("Edited Data")
        # st.write(edited_df)

