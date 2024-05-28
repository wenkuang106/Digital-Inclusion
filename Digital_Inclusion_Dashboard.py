##Import Dependencies
import streamlit as st
from st_aggrid import AgGrid
import pandas as pd

#local dependencies
import dashboard_lib
from dashboard_page_components import dashboard_map, dashboard_map_search

###Connect to database###
connection = dashboard_lib.db_connection()

# Page Setting
st.set_page_config(layout='centered', page_title='Digital Inclusion Dashboard', page_icon='📊', initial_sidebar_state='expanded')

#css for font
st.markdown(
         """
        <style>
@font-face {
  font-family: 'orpheus-pro';
  font-style: normal;
  font-weight: 400;
  src: url(https://use.typekit.net/af/8b252c/00000000000000007735ebd8/30/l?subset_id=2&fvd=n5&v=3) format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

    html, body, [class*="css"]  {
    font-family: 'orpheus-pro';
    font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True,
    )


#Initialize session state#
if 'user' not in st.session_state:
    st.session_state['user'] = "None"
if 'role' not in st.session_state:
    st.session_state['role'] = "None"



#Title of the Website#
st.title("Welcome to the New York State Digital Inclusion Dashboard") # Title of the Website
st.subheader("Created by Stony Brook University AHI 2022 Cohort") # Subheader


# Importing Dataframe
    
df = dashboard_lib.load_data(connection)
list(df.columns)

# Download Data
csv = dashboard_lib.convert_df(df)
       
# Clean data for filtering 
 
df.columns = df.columns.str.replace(' ', '_')

# Sidebar
#Image
st.sidebar.image('images/digital_equity_nw.png')

#Filters
st.sidebar.header("Please Select Filters Here:")
coalition = st.sidebar.multiselect(
    "Select the Coalition",
    options=df['coalition'].unique(),
)
organizations = st.sidebar.multiselect(
    "Select the Organizations",
    options=df['organization'].unique()
)
digital_inclusion_need_device = st.sidebar.multiselect(
    "Select to include organizations that assist with device access/ownership",
    options={'Yes','No'}
)
digital_inclusion_need_education = st.sidebar.multiselect(
    "Select to include organizations that assist with technology skills education",
    options={'Yes','No'}
)
digital_inclusion_need_broadband = st.sidebar.multiselect(
    "Select to include organizations that assist with broadband access",
     options={'Yes','No'}
)
status = st.sidebar.multiselect(
    "Select the Status",
    options=df['program_status'].unique(),
)

#Cast digital_inclusion_need_* to boolean
digital_inclusion_need_device = [True if x == 'Yes' else False for x in digital_inclusion_need_device]
digital_inclusion_need_education = [True if x == 'Yes' else False for x in digital_inclusion_need_education]
digital_inclusion_need_broadband = [True if x == 'Yes' else False for x in digital_inclusion_need_broadband]

#Logic for filtering if no filters are selected
if digital_inclusion_need_device == []:
    digital_inclusion_need_device = [True, False]
if digital_inclusion_need_education == []:
    digital_inclusion_need_education = [True, False]
if digital_inclusion_need_broadband == []:
    digital_inclusion_need_broadband = [True, False]
if organizations == []:
    organizations = df['organization'].unique()
if coalition == []:
    coalition = df['coalition'].unique()
if status == []:
    status = df['program_status'].unique()

#Filtering the dataframe#
df_selection = df[(df['coalition'].isin(coalition)) & 
                  (df['organization'].isin(organizations)) & 
                  (df['digital_inclusion_need_device'].isin(digital_inclusion_need_device)) &
                  (df['digital_inclusion_need_education'].isin(digital_inclusion_need_education)) & 
                  (df['digital_inclusion_need_broadband'].isin(digital_inclusion_need_broadband)) & 
                  (df['program_status'].isin(status))]

#Setting up the map dataframe
try:
    #Load in the data by only selecting id that are in the filtered dataframe
    map_df = pd.read_sql_query(f"SELECT * FROM locations", connection)

    #drop the id column
    map_df = map_df.drop(columns=['id'])

    #drop organizations that are not in the filtered dataframe
    map_df = map_df[map_df['organization'].isin(df_selection['id'])]

    #rename the email column to email_location and the phone column to phone_location
    map_df = map_df.rename(columns={'email': 'email_location', 'phone': 'phone_location'})

    #join the filtered dataframe with the map dataframe
    map_df = map_df.merge(df_selection, left_on='organization', right_on='id')

    #Change the name of organization_y to organization
    map_df['organization'] = map_df['organization_y']
    #drop the organization_x and organization_y columns
    map_df = map_df.drop(columns=['organization_x', 'organization_y'])
except:
    map_df = pd.DataFrame()

# Assigning variables to metrics 
col_1, col_2, col_3 = st.columns(3)
col_4, col_5, col_6 = st.columns(3)


Map, Search = st.tabs(["Overall Map","Search"])
with Map:
        dashboard_map(map_df, connection)
        #Code for Metrics
        #try:
        with col_1:
            st.metric(label="Total of Organizations", value=map_df['organization'].nunique())# Displays Total Organizations in a metric box on the top of the page 
        with col_2:
            st.metric(label="Active Program Status",value=sum(map_df['program_status']=="Active")) # Display Total active programs
        with col_3:
            st.metric(label="Total Location",value=map_df['location_name'].nunique()) #Displays Total Locations
        with col_4:
            st.metric(label="Device Access Resources", value=map_df['digital_inclusion_need_device'].sum()) #Displays Total of Device Access Resources
        with col_5:
            st.metric(label="BroadBand Access Resources", value=map_df['digital_inclusion_need_broadband'].sum()) # Display total amount of BroadBand Access Resources 
        with col_6:
            st.metric(label="Digital Literacy Education Resources", value=map_df['digital_inclusion_need_education'].sum()) # Display total amount of Digital Literacy Education Resources
        #except:
           # st.write("No Data Available")
        #Show the filtered dataframe#
        st.title("Organizations based on your filters")
        st.dataframe(df_selection)
                #Download Data#
        with st.expander("Download Data"):
            if st.checkbox('Preview Download DataSet',False):
                chart_data = AgGrid(df)

            st.markdown("---")
            st.download_button (
                label="Download the DI dataset as CSV",
                data=csv,
                file_name='Digital_Inclusion_Data_Set.csv',
                mime='text/csv',
                )

##search
with Search:
       dashboard_map_search(map_df)
