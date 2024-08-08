import os
import json
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime

class JsonDataExtractor:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.overall_data, self.individual_data = self.extract_test_data_from_json()
    
    def extract_test_data_from_json(self) -> (pd.DataFrame, pd.DataFrame):
        overall_data = []
        individual_data = []
        json_files = [f for f in os.listdir(self.folder_path) if f.endswith('.json')]
        
        for json_file in json_files:
            file_path = os.path.join(self.folder_path, json_file)
            with open(file_path, 'r') as file:
                file_data = json.load(file)
                
                test_result = file_data.get('Result', 'N/A')
                local_result_path = file_data.get('LocalResultPath', 'N/A')
                test_setup_id = file_data.get('Request', {}).get('TestSetupId', 'N/A')
                
                # Extract date from LocalResultPath
                date = local_result_path.split('\\')[-1].split('-')[0] if local_result_path != 'N/A' else 'N/A'
                
                overall_data.append({
                    "Date": date,
                    "TestSetupID": test_setup_id,
                    "Result": test_result
                })
                
                individual_tests = file_data.get('Tests', [])
                
                for test in individual_tests:
                    test_id = test.get('TestID', 'N/A')
                    result = test.get('Result', 'N/A')
                    description = test.get('Description', 'N/A')
                    individual_data.append({
                        "Date": date,
                        "TestSetupID": test_setup_id,
                        "IndividualTestID": test_id,
                        "Result": result,
                        "Description": description
                    })
        
        overall_df = pd.DataFrame(overall_data)
        individual_df = pd.DataFrame(individual_data)
        
        # Ensure sorting
        overall_df = overall_df.sort_values(by=['Date', 'TestSetupID'])
        individual_df = individual_df.sort_values(by=['Date', 'TestSetupID', 'IndividualTestID'])
        
        return overall_df, individual_df

def visualize_data(overall_df: pd.DataFrame, individual_df: pd.DataFrame):
    # Convert 'Result' to colors for overall results
    overall_df["ResultColor"] = overall_df["Result"].map(lambda x: 'green' if x == "PASS" else 'red')
    
    st.subheader('Overall Test Setup Results by Date')
    
    # Plotting the overall results using Altair
    overall_chart = alt.Chart(overall_df).mark_bar().encode(
        x=alt.X('Date:N', title='Date', sort=alt.SortField(field="Date", order="ascending")),
        y=alt.Y('TestSetupID:N', title='Test Setup ID', sort=alt.SortField(field="TestSetupID", order="ascending")),
        color=alt.Color('Result:N', scale=alt.Scale(domain=['PASS', 'FAIL'], range=['green', 'red']), legend=alt.Legend(title="Test Result")),
        tooltip=['Date', 'TestSetupID', 'Result']
    ).properties(
        title="Overall Test Setup Results by Date"
    )
    
    st.altair_chart(overall_chart, use_container_width=True)
    
    # Get unique test setup IDs
    unique_test_setup_ids = individual_df["TestSetupID"].unique()
    
    # Create tabs for each test setup ID
    tabs = st.tabs([f"Test Setup ID: {test_setup_id}" for test_setup_id in unique_test_setup_ids])
    
    for tab, test_setup_id in zip(tabs, unique_test_setup_ids):
        with tab:
            st.subheader(f'Test Setup ID: {test_setup_id}')
            setup_data = individual_df[individual_df["TestSetupID"] == test_setup_id]
            
            # Plotting using Altair for individual test results
            individual_chart = alt.Chart(setup_data).mark_bar().encode(
                x=alt.X('Date:N', title='Date', sort=alt.SortField(field="Date", order="ascending")),
                y=alt.Y('IndividualTestID:N', title='Individual Test ID', sort=alt.SortField(field="IndividualTestID", order="ascending")),
                color=alt.Color('Result:N', scale=alt.Scale(domain=['PASS', 'FAIL'], range=['green', 'red']), legend=alt.Legend(title="Test Result")),
                tooltip=['Date', 'IndividualTestID', 'Result', 'Description']
            ).properties(
                title=f"Individual Test Results for Test Setup ID: {test_setup_id}"
            )
            
            st.altair_chart(individual_chart, use_container_width=True)

# Example usage in Streamlit
def main():
    st.title("Test Results Visualization")

    # Display the date the script is running
    current_date = datetime.now().strftime("%Y-%m-%d")
    st.write(f"**Script run date:** {current_date}")
    
    # Hard-coded folder path
    folder_path = r'C:\Users\z00507fk\Desktop\all_results'
    
    extractor = JsonDataExtractor(folder_path)
    overall_df, individual_df = extractor.overall_data, extractor.individual_data
    visualize_data(overall_df, individual_df)

if __name__ == "__main__":
    main()
