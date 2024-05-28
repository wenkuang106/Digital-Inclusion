from geopy.geocoders import Nominatim
import streamlit as st
import pandas as pd
import usaddress
import os
import dotenv
import sqlalchemy
import time
import numpy as np

##Functions for geocoding, but also some other useful ones

#Combines excel files into one dataframe
def combine_excel_files(excel_files):
    organizations = pd.DataFrame()
    locations = pd.DataFrame()
    for file in excel_files:
        organizations = organizations.append(pd.read_excel(file, sheet_name='Sheet3'))
    for file in excel_files:
        locations = locations.append(pd.read_excel(file, sheet_name='Organization Locations'))
    locations.dropna(subset=['Lead Organization'], inplace=True)
    organizations.dropna(subset=['Lead Organization'], inplace=True)

    writer = pd.ExcelWriter('Asset Forms/Asset_Combined.xlsx', engine = 'xlsxwriter')
    locations.to_excel(writer, sheet_name = 'locations', index=False)
    organizations.to_excel(writer, sheet_name = 'organizations', index=False)
    writer.close()
    return print('Complete')

#uses usaddress to parse the address
def parse_address(address):
    parsed_address = usaddress.parse(address)
    street_name = ""
    zipcode = ""
    unit = ""
    for component in parsed_address:
        if component[1] == 'PlaceName':
            city = component[0]
        if component[1] == 'StateName':
            state = component[0]
        if component[1] == 'ZipCode':
            zipcode = component[0]
        if component[1] == 'AddressNumber':
            street_number = component[0]
        if component[1]  == 'StreetNamePostDirectional' or component[1]  == 'StreetName' or component[1]  == 'StreetNamePreDirectional' or component[1]  == 'StreetNamePostType':
            street_name = street_name + " " + component[0]
        if component[1] == 'OccupancyType' or component[1] == 'OccupancyIdentifier':
            unit = unit + ' ' +component[0]
    return city, state, zipcode, street_number, street_name, unit

#Gets the lat and long from the address
def get_location_lat_long(address):
    lat = None
    lon = None
    try:
        geolocator = Nominatim(user_agent="di_dashboard_app")
        location = geolocator.geocode(address)
        lat = float(location.latitude)
        lon = float(location.longitude)
    except:
        pass
    return lat, lon

#updates location data with lat and long
def update_locations_df(excel_file):    
    # Read in the data
    df = pd.read_excel(excel_file, sheet_name='locations')

    #add columns for street, number, city, state, zip, lat, long
    df.columns = ['lead_organization', 'address']
    df['street_number'] = ''
    df['street_name'] = ''
    df['city'] = ''
    df['state'] = ''
    df['zipcode'] = ''
    df['unit'] = ''
    df['lat'] = ''
    df['lon'] = ''

    #loop through the rows and parse the address
    for index, row in df.iterrows():
        try:
            parsed_address = parse_address(row['address'])
            #loop through the parsed address and add the values to the appropriate column
            df.at[index, 'city'] = parsed_address[0]
            df.at[index, 'state'] = parsed_address[1]
            df.at[index, 'zipcode'] = parsed_address[2]
            df.at[index, 'street_number'] = parsed_address[3]
            df.at[index, 'street_name'] = parsed_address[4]
            df.at[index, 'unit'] = parsed_address[5]
        except:
            pass
    
    #Remove special characters from all columns
    df['street_number'] = df['street_number'].str.replace('[^0-9]', '')
    df['street_name'] = df['street_name'].str.replace('[^A-Za-z0-9]+', ' ')
    df['city'] = df['city'].str.replace('[^A-Za-z0-9]+', ' ')
    df['state'] = df['state'].str.replace('[^A-Za-z0-9]+', ' ')
    df['zipcode'] = df['zipcode'].str.replace('[^0-9]', '')
    df['unit'] = df['unit'].str.replace('[^A-Za-z0-9]+', ' ')

    #apply geo location to the dataframe 
    for index, row in df.iterrows():
        try:
            address = row['street_number'] + " " + row['street_name'] +", " + row['city'] + ", " + row['state'] + " " + row['zipcode']
            print (address)
            lat, long = get_location_lat_long(address)
            print (lat, long)
            df.at[index, 'lat'] = lat
            df.at[index, 'lon'] = long
        except:
            pass
    #write the dataframe to a csv
    df.dropna(subset=['lat', 'lon'], inplace=True)
    df.to_csv('Asset Forms/locations.csv', index=False)
    return print('Complete')

#Checks the url to see if the user is logged in and what their role is
def get_logged_in(connection):
    #get query parameters
    query_params = st.experimental_get_query_params()

    #check the database to see if the user is logged in.
    try:
        logged_in = pd.read_sql_query("SELECT logged_in FROM users WHERE username = '" + query_params['user'][0] + "'", connection).values[0][0]
    except:
        logged_in = 0
    #Check the database to make sure the user has not been idle for more than 30 minutes
    try:
        #last_active = pd.read_sql_query("SELECT last_login FROM users WHERE username = 'israel'", connection).values[0][0]
        last_active = pd.read_sql_query("SELECT last_login FROM users WHERE username = '" + query_params['user'][0] + "'", connection).values[0][0]
        now = np.datetime64('now')
        time_passed = (now - last_active).astype('timedelta64[m]')
        if time_passed < np.timedelta64(15, 'm'):
            activity_timeout = False
        else:
            activity_timeout = True
    except:
        activity_timeout = True

    #check if the user is logged in and that the last login was less than 30 minutes ago
    if 'user' in query_params and logged_in == 1 and query_params['user'][0] != 'None' and activity_timeout == False:
        st.session_state['user'] = query_params['user'][0]      
    elif 'user' in query_params and logged_in == 0 and query_params['user'][0] != 'None' :
        st.warning('You are not logged in. Please use the log in page to continue. This may be due to a timeout.')
    else:
        pass

#Checks current user's role
def get_user_role(connection):
    st.session_state['role'] = 'None'
    st.session_state['admin_for'] = 'None'
    #updates last_login to current time for the user
    #get user role from database if the role is not in the session state
    try:
        get_user_role = pd.read_sql("SELECT role FROM users WHERE username = '" + st.session_state['user'] + "'", connection)
        get_admin_for_coalition = pd.read_sql("SELECT admin_for_coalition FROM users WHERE username = '" + st.session_state['user'] + "'", connection) 
        time.sleep(.5)
        st.session_state['role'] = get_user_role['role'][0]
        st.session_state['admin_for'] = get_admin_for_coalition['admin_for_coalition'][0]
        pd.read_sql_query("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = '" + st.session_state['user'] + "'", connection)
    except:
        pass
            
#database connection function
def db_connection():
#load environment variables#
    dotenv.load_dotenv()
    MYSQL_HOSTNAME = os.getenv("MYSQL_HOSTNAME")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
#connect to database#
    engine = sqlalchemy.create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DATABASE}")
    connection = engine.connect()
    return connection

#function to load the data from the database
def load_data(connection):
    df = pd.read_sql("SELECT * FROM organizations", connection)
    #make all column names lowercase
    lowercase = lambda x:str(x).lower()
    df.rename(lowercase, axis='columns', inplace=True)
    #remove id_coalition column and replace it with coalition_name#

    #This line is more efficient than the commented out linea below#
    df['coalition'] = df['coalition'].map(pd.read_sql("SELECT * FROM coalitions", connection).set_index('id_coalition')['coalition_name'])
    #df['coalition'] = df['coalition'].map(lambda x: pd.read_sql(f"SELECT coalition_name FROM coalitions WHERE id_coalition = {x}", connection)["coalition_name"][0])
    
    #Reorder the columns#
    df = df[['coalition','id', 'organization', 'program_name', 'population_name', 'program_status', 'organization_type', 'website', 'contact', 'email', 'phone', 'digital_inclusion_need_device', 'digital_inclusion_need_education', 'digital_inclusion_need_broadband']]
    return df

#function to convert the dataframe to a csv
def convert_df(df):
    return df.to_csv().encode('utf-8')

