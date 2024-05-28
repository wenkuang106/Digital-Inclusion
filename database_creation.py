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

### Drop tables if they exist ###
#db.execute("DROP TABLE IF EXISTS coalitions")
#db.execute("DROP TABLE IF EXISTS organizations")
#db.execute("DROP TABLE IF EXISTS locations")

###Create tables for dashboard ###
table_coalitions = """
create table if not exists coalitions (
  id int auto_increment,
  id_coalition varchar(255) DEFAULT NULL UNIQUE, 
  coalition_name varchar(255) NOT NULL unique,
  website varchar(255) DEFAULT NULL,
  latitude FLOAT DEFAULT NULL,
  longitude FLOAT DEFAULT NULL,
  zip varchar(255) DEFAULT NULL,
  PRIMARY KEY (id) 
); 
  """

table_organizations = """
create table if not exists organizations (
	id int auto_increment,
  organization VARCHAR(255) DEFAULT NULL,
  program_name VARCHAR(255) DEFAULT NULL,
  population_name VARCHAR(255) DEFAULT NULL,
  program_status VARCHAR(255) DEFAULT NULL,
  organization_type VARCHAR(255) DEFAULT NULL,
  website VARCHAR(255) DEFAULT NULL,
  contact VARCHAR(255) DEFAULT NULL,
  email VARCHAR(255) DEFAULT NULL,
  phone VARCHAR(255) DEFAULT NULL,
  digital_inclusion_need_device BOOL DEFAULT FALSE,
  digital_inclusion_need_education BOOL DEFAULT FALSE,
  digital_inclusion_need_broadband BOOL DEFAULT FALSE,
  coalition VARCHAR(255),
  PRIMARY KEY (id),
  FOREIGN KEY (coalition) REFERENCES coalitions(id_coalition) ON DELETE CASCADE
);
  """

table_locations = """
create table if not exists locations (
	id int auto_increment,
  organization int NOT NULL,
  location_name VARCHAR(255) DEFAULT NULL,
  address VARCHAR(255) DEFAULT NULL,
  address_2 VARCHAR(255) DEFAULT NULL,
  city VARCHAR(255) DEFAULT NULL,
  state VARCHAR(255) DEFAULT NULL,
  zip VARCHAR(255) DEFAULT NULL,
  phone VARCHAR(255) DEFAULT NULL,
  email VARCHAR(255) DEFAULT NULL,
  notes VARCHAR(255) DEFAULT NULL,
  latitude FLOAT DEFAULT NULL,
  longitude FLOAT DEFAULT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (organization) REFERENCES organizations(id) ON DELETE CASCADE
);
"""
table_users = """
create table if not exists users (
  id int auto_increment,
  username VARCHAR(255) DEFAULT NULL,
  email VARCHAR(255) DEFAULT NULL,
  password VARCHAR(255) DEFAULT NULL,
  role VARCHAR(255) DEFAULT NULL,
  logged_in BOOL DEFAULT FALSE,
  last_login DATETIME DEFAULT NULL,
  admin_for_coalition VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (id)
);
"""
### create the tables in MYSQL ###
db.execute(table_coalitions)
db.execute(table_organizations)
db.execute(table_locations)
db.execute(table_users)

