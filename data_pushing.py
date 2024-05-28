import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

##### loading in the credentials from the .env file ##### 

load_dotenv('.env')

MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

##### connecting to the database #####

connection_string = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DATABASE}'
db = create_engine(connection_string)

tables_names = db.table_names()
print(tables_names) ## confirming connection worked in addition to printing the current tables within the connected database 

#### loading in all the master table .CSV files

organizations = pd.read_csv('') ## insert the .CSV file containing the data 
coalitions = pd.read_csv('') ## insert the .CSV file containing the data 
locations = pd.read_csv('') ## insert the .CSV file containing the data 

#### changing the NaN values to NONE values in order for SQLAlchemy to be able to work

organizationsUpdated = organizations.astype("object").where(pd.notnull(organizations), None)
coalitionsUpdated = coalitions.astype("object").where(pd.notnull(coalitions), None)
locationsUpdated = locations.astype("object").where(pd.notnull(locations), None)

#### creating the query command for when pushing data into MySQL database

coalInsertQuery = """INSERT INTO coalitions (
    id_coalition, 
    coalition_name,
    website,
    latitude,
    longitude,
    zip
    ) 
    VALUES (%s, %s, %s, %s, %s, %s)
"""

orgInsertQuery = """INSERT INTO organizations (
    organization,
    program_name,
    population_name,
    program_status,
    organization_type,
    website,
    contact,
    email,
    phone,
    digital_inclusion_need_device,
    digital_inclusion_need_education,
    digital_inclusion_need_broadband,
    coalition
    ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

locInsertQuery = """INSERT INTO locations (
    organization,
    location_name,
    address,
    address_2,
    city,
    state,
    zip,
    phone,
    email,
    notes,
    latitude,
    longitude
    ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

#### checking the total rows within the within the uploaded CSV files to know the breaking row

organizationsUpdated.shape
coalitionsUpdated.shape
locationsUpdated.shape

#### pushing the data into MySQL database

startingRow = 0
for index, row in coalitionsUpdated.iterrows(): 
    startingRow += 1 
    ## replace the 'xx' with the column names in which the data that needs to pushed into is from
    ## however the column title should be the same as the column names within the SQL table for smoother data insertion
    ## add 'row['xx']' if needed 
    db.execute(coalInsertQuery, (row['id_coalition'], row['coalition_name'])) 
    print("Row completed: ", index)
    ## replace the 'xx' with the total number of rows that you will be inserting from the .CSV file 
    ## because the startingRow started at 0
    if startingRow == xx:
        break

startingRow = 0
for index, row in organizationsUpdated.iterrows(): 
    startingRow += 1 
    ## replace the 'xx' with the column names in which the data that needs to pushed into is from
    ## however the column title should be the same as the column names within the SQL table for smoother data insertion
    ## add 'row['xx']' if needed 
    db.execute(orgInsertQuery, (row['organization'], row['program_name'], row['population_name'], row['program_status'], 
                                row['organization_type'], row['website'], row['contact'],  row['email'], 
                                row['phone'],row['digital_inclusion_need_device'], row['digital_inclusion_need_education'], row['digital_inclusion_need_broadband'],
                                row['coalition'])) 
    print("Row completed: ", index)
    ## replace the 'xx' with the total number of rows -1 that you will be inserting from the .CSV file 
    ## because the startingRow started at 0
    if startingRow == xx:
        break
        
startingRow = 0
for index, row in locationsUpdated.iterrows(): 
    startingRow += 1 
    ## replace the 'xx' with the column names in which the data that needs to pushed into is from
    ## however the column title should be the same as the column names within the SQL table for smoother data insertion
    ## add 'row['xx']' if needed 
    db.execute(locInsertQuery, (row['organization'], row['location_name'], row['address'], row['address_2'], 
                                row['city'], row['state'], row['zip'], row['phone'], 
                                row['email'], row['notes'], row['latitude'], row['longitude'])) 
    print("Row completed: ", index)
    ## replace the 'xx' with the total number of rows that you will be inserting from the .CSV file 
    ## because the startingRow started at 0
    if startingRow == xx:
        break
        
#### running queries to see if the data insertion functioned properly
        
df_coal = pd.read_sql_query("select * from coalitions;", db)
df_org = pd.read_sql_query("select * from organizations;", db)
df_loc = pd.read_sql_query("select * from locations;", db)

df_coal
df_org
df_loc
