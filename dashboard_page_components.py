###This page is used to add a new coalition to the database###

import streamlit as st
import pandas as pd
import random
import dashboard_lib
import folium
from time import sleep
from geopy.distance import distance
from streamlit_folium import folium_static
from dashboard_lib import get_location_lat_long
import time 
import hashlib

def new_organization_page(connection):
    #Check if user is logged in, and only gives access if they are an admin#
    if st.session_state['role'] == 'admin':
        #Set up Title#
        st.header("Add/Edit Organizations")

        #Dropdown select coalition#
        #Creates a dropdown of available coalitions#
        if st.session_state['admin_for'] == 'all':
            with st.form(key='new_org_form_select_coalition'):
                coalition_name = st.selectbox("Which Coalition Does This Organization Belong To?", pd.read_sql("SELECT coalition_name FROM coalitions", connection)["coalition_name"].tolist())
                submit_button = st.form_submit_button(label='Select Coalition')
                if submit_button:
                    coalition_name = coalition_name
        else:
            coalition_name = pd.read_sql_query(f"SELECT coalition_name FROM coalitions WHERE id_coalition = '{st.session_state['admin_for']}'", connection)["coalition_name"][0]
            st.write("You are an admin for the " + coalition_name + " Coalition. You can only add/edit organizations in this coalition.")
            #coalition_name = st.selectbox("Please Select a Coalition to get started.", pd.read_sql("SELECT coalition_name FROM coalitions", connection)["coalition_name"].tolist())
        
        st.text("\n")
           
        #Set up the form to add a new organization#
        with st.form(key='new_organization_form'):
            st.header("Add a New Organization")
            organization_name = st.text_input("Organization Name")
            program_name = st.text_input("Program Name")
            population_name = st.text_input("Population Served")
            program_status = st.selectbox("Program Status", options=['Active', 'Inactive', 'Seasonal', 'Under Development', 'Other'])
            organization_type = st.selectbox("Organization Type", options=['Non-Profit', 'For-Profit', 'Government', 'Library', 'Other'])
            website = st.text_input("Website")
            contact = st.text_input("Contact")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            
            st.text("Digital Inclusion Services")
            digital_inclusion_need_device = st.checkbox("Provides Devices?")
            digital_inclusion_need_education = st.checkbox("Provides Educational/Skills Resources?")
            digital_inclusion_need_broadband = st.checkbox("Assists/Provides Broadband Access?")

            #Set up the submit button#
            submit_button_add = st.form_submit_button(label='Add Organization')

            #Convert the coalition name to the coalition ID#
            coalition_id = str(pd.read_sql(f"SELECT id_coalition FROM coalitions WHERE coalition_name = '{coalition_name}'", connection)["id_coalition"][0])
            
            #cast the boolean values to 1 or 0#
            digital_inclusion_need_device = int(digital_inclusion_need_device)
            digital_inclusion_need_education = int(digital_inclusion_need_education)
            digital_inclusion_need_broadband = int(digital_inclusion_need_broadband)

            #If the submit button is clicked, add the new organization to the database as long as it doesnt exist#
            if submit_button_add:
                if pd.read_sql(f"SELECT * FROM organizations WHERE organization = '{organization_name}'", connection).empty:
                    try:
                    #Add the new org to the database#
                        connection.execute(f"""INSERT INTO organizations (organization, program_name, population_name, program_status, organization_type, 
                                                website, contact, email, phone, digital_inclusion_need_device, digital_inclusion_need_education, digital_inclusion_need_broadband, coalition) 
                                                VALUES ('{organization_name}', '{program_name}', '{population_name}', '{program_status}', '{organization_type}', 
                                                '{website}', '{contact}', '{email}', '{phone}', '{digital_inclusion_need_device}', '{digital_inclusion_need_education}', '{digital_inclusion_need_broadband}', '{coalition_id}')""")
                    #Show the user a message that the coalition was added#
                        st.success(f"Organization {organization_name} added to database")
                    except: 
                    #Show the user a message that the coalition was not added#
                        st.error(f"Organization {organization_name} was not added to database, please make the organization does not already exist.")
                else:
                    st.error(f"Organization {organization_name} already exists, please make the organization does not already exist.")
        #Set up the form to remove or edit an organization#
        if pd.read_sql(f"SELECT * FROM organizations WHERE coalition = '{coalition_id}'", connection).empty:
            st.error("No organizations in database for this coalition. Please add an organization to the database.")
        else:    
            with st.form(key='remove_edit_organization_form'):
                #Creates a dropdown of available organizations#
                st.header("Remove/Edit an Organization in Selected Coalition")
                edit_organization_name = st.selectbox("Organization", pd.read_sql(f"SELECT organization FROM organizations WHERE coalition ='{coalition_id}'", connection)["organization"].tolist())
                edit_organization_id = str(pd.read_sql(f"SELECT id FROM organizations WHERE organization = '{edit_organization_name}'", connection)["id"][0])

                
                #Set up the submit button#
                submit_button_remove = st.form_submit_button(label='Remove Organization')
                #Set up edit button#
                submit_button_edit_org = st.form_submit_button(label='Edit Organization')
                
                #logic for edit button session state#
                if st.session_state.get('edit_button_org') != True:
                    st.session_state['edit_button_org'] = submit_button_edit_org

                #If the submit button is clicked, remove the organization from the database#
                if submit_button_remove:
                    #Remove the organization from the database#
                    connection.execute(f"DELETE FROM organizations WHERE id = '{edit_organization_id}'")
                    #Show the user a message that the organization was removed#
                    st.success(f"Organization {organization_name} removed from database")
        
                #If the edit button is clicked, show the edit form#
                if st.session_state['edit_button_org'] == True:
                    #Set up the form to edit an organization#
                        #Creates a dropdown of available organizations#
                        edit_organization_name = st.text_input("Organization Name", edit_organization_name)
                        edit_program_name = st.text_input("Program Name", pd.read_sql(f"SELECT program_name FROM organizations WHERE id = '{edit_organization_id}'", connection)["program_name"][0])
                        edit_population_name = st.text_input("Population Served", pd.read_sql(f"SELECT population_name FROM organizations WHERE id = '{edit_organization_id}'", connection)["population_name"][0])
                        edit_program_status = st.selectbox("Program Status (Pick 1)", options=['Active', 'Inactive', 'Seasonal', 'Other'], index=0)
                        edit_organization_type = st.selectbox("Organization Type (Pick 1)", options=['Non-Profit', 'For-Profit', 'Government', 'Library','School', 'University', 'Other'], index=6)
                        edit_website = st.text_input("Website", pd.read_sql(f"SELECT website FROM organizations WHERE id = '{edit_organization_id}'", connection)["website"][0])
                        edit_contact = st.text_input("Contact", pd.read_sql(f"SELECT contact FROM organizations WHERE id = '{edit_organization_id}'", connection)["contact"][0])
                        edit_email = st.text_input("Email", pd.read_sql(f"SELECT email FROM organizations WHERE id = '{edit_organization_id}'", connection)["email"][0])
                        edit_phone = st.text_input("Phone", pd.read_sql(f"SELECT phone FROM organizations WHERE id = '{edit_organization_id}'", connection)["phone"][0])

                        #Checkboxes for digital inclusion services#
                        st.text("Digital Inclusion Services")
                        edit_digital_inclusion_need_device = st.checkbox("Provides Devices?", pd.read_sql(f"SELECT digital_inclusion_need_device FROM organizations WHERE id = '{edit_organization_id}'", connection)["digital_inclusion_need_device"][0])
                        edit_digital_inclusion_need_education = st.checkbox("Provides Educational/Skills Resources?", pd.read_sql(f"SELECT digital_inclusion_need_education FROM organizations WHERE id = '{edit_organization_id}'", connection)["digital_inclusion_need_education"][0])
                        edit_digital_inclusion_need_broadband = st.checkbox("Provides Broadband?", pd.read_sql(f"SELECT digital_inclusion_need_broadband FROM organizations WHERE id = '{edit_organization_id}'", connection)["digital_inclusion_need_broadband"][0])

                        #cast the boolean values to 1 or 0#
                        edit_digital_inclusion_need_device = int(edit_digital_inclusion_need_device)
                        edit_digital_inclusion_need_education = int(edit_digital_inclusion_need_education)
                        edit_digital_inclusion_need_broadband = int(edit_digital_inclusion_need_broadband)

                        #Submit Changes#
                        push_submit_button_edit_org = st.form_submit_button(label='Accept Changes')
                        
                        if push_submit_button_edit_org:
                            try:
                            #submit the changes to the database#
                                connection.execute(f"""UPDATE organizations SET organization = '{edit_organization_name}', program_name = '{edit_program_name}', 
                                population_name = '{edit_population_name}', program_status = '{edit_program_status}', organization_type = '{edit_organization_type}', 
                                website = '{edit_website}', contact = '{edit_contact}', email = '{edit_email}', phone = '{edit_phone}', digital_inclusion_need_device = '{edit_digital_inclusion_need_device}', 
                                digital_inclusion_need_education = '{edit_digital_inclusion_need_education}', digital_inclusion_need_broadband = '{edit_digital_inclusion_need_broadband}', coalition = '{coalition_id}' WHERE id = '{edit_organization_id}'""")
                                
                                #Show the user a message that the org was edited#
                                st.success(f"Organization {edit_organization_name} updated in database")
                                st.session_state['edit_button_org'] = False
                            except:
                            #Show the user a message that the organization was not edited#
                                st.error(f"Organization {edit_organization_name} not updated in database")
            #create a dataframe of all the organizations in the database that belong to the selected coalition#
            organizations = (pd.read_sql(f"""SELECT * FROM organizations WHERE coalition = '{coalition_id}'""", connection))
            #Show the user the organizations in the database#
            st.write(f"Below is a list of all the organizations in the database that belong to the {coalition_name} Coaltion (As selected above).")
            st.write(organizations)
    #If the user is not an admin, show them a message that they do not have access#
    else:
        st.error("You do not have permission to view this page")

def new_location_page(connection):
    #Check if user is logged in, and only gives access if they are an admin#
    if st.session_state['role'] == 'admin':
    
        #Set up Title#
        st.header("Add a New Location to an Existing Organization")

        #Dropdown select coalition#
        if st.session_state['admin_for'] == 'all':
            coalition_name = st.selectbox("Which Coalition Does This Organization Belong To?", pd.read_sql("SELECT coalition_name FROM coalitions", connection)["coalition_name"].tolist())
        else:
            coalition_name = pd.read_sql_query(f"SELECT coalition_name FROM coalitions WHERE id_coalition = '{st.session_state['admin_for']}'", connection)["coalition_name"][0]
            st.write("You are an admin for the " + coalition_name + " Coalition. You can only add/edit locations to organizations in this coalition.")
        
        #Dropdown to select org based on coalition selected#
        try:
            org_name = st.selectbox("Organization", pd.read_sql(f"SELECT organization FROM organizations WHERE coalition = (SELECT id_coalition FROM coalitions WHERE coalition_name = '{coalition_name}')", connection)["organization"].tolist())
        except:
            st.error("No organizations in this coalition")
        
        #Based on the selected org, get the org ID#
        try:
            org_id = pd.read_sql(f"SELECT id FROM organizations WHERE organization = '{org_name}'", connection)['id'][0]
        except:
            st.error("No organizations in this coalition")

        #display the current locations for the selected org#
        try:
            st.text("Current Locations:")
            st.dataframe(pd.read_sql(f"SELECT * FROM locations WHERE organization = '{org_id}'", connection))
        except:
            st.error("No locations to display")

        ###Form to add a new location###
        with st.form(key='new_location_form'):
            location_name = st.text_input("Location Name (Tooltip on Map)")
            location_address = st.text_input("Location Address")
            location_address_2 = st.text_input("Location Address 2")
            location_city = st.text_input("Location City")
            location_state = st.text_input("Location State")
            location_zip = st.text_input("Location Zip")
            location_phone = st.text_input("Location Phone")
            location_email = st.text_input("Location Email")
            notes = st.text_input("Location Notes")

            #Set up the submit button#
            submit_button_add = st.form_submit_button(label='Add Location')

            #If the submit button is clicked, add the new coalition to the database as long as it doesnt exist#
            if submit_button_add:
                    #check if the location already exists#
                    try:
                        location_id = pd.read_sql(f"SELECT id FROM locations WHERE organization = '{org_id}' AND location_name = '{location_name}'", connection)['id'][0]
                        st.error("Location already exists")
                    except:
                        #Add the new coalition to the database#
                        address = location_address + " " + location_address_2 + "" + location_city + " " + location_state + " " + location_zip
                        lat,lon = dashboard_lib.get_location_lat_long(address)
                        #check if a lat and lon were returned#
                        if lat != None: 
                            connection.execute(f"""INSERT INTO locations (location_name, address, city, state, zip, phone, email, notes, organization,latitude,longitude) 
                                                VALUES ('{location_name}', '{location_address}', '{location_city}', '{location_state}', '{location_zip}',
                                                '{location_phone}', '{location_email}', '{notes}', '{org_id}', '{lat}', '{lon}')""")
                            #Show the user a message that the coalition was added#
                            st.success(f"Location {location_name} added to database Successfully!")
                            time.sleep(.5)
                            st.experimental_rerun()
                        else:
                            st.error(f"{address} not found. Please check the address and try again.")

        ###Form to edit/remove a location###
        with st.form(key='remove_edit_locations_form'):
            try:
                #Creates a dropdown of available organizations#
                st.header("Remove/Edit a Location in Selected Orgnization")
                edit_location_name = st.selectbox("Location Name", options=pd.read_sql(f"SELECT location_name FROM locations WHERE organization = '{org_id}'", connection)['location_name'].to_list())
                edit_location_id = str(pd.read_sql(f"SELECT id FROM locations WHERE location_name = '{edit_location_name}'", connection)['id'][0])

                
                #Set up the submit button#
                submit_button_remove_location = st.form_submit_button(label='Remove Location')
                #Set up edit button#
                submit_button_edit_location = st.form_submit_button(label='Edit Location')
                
                #logic for edit button session state#
                if st.session_state.get('edit_button_location') != True:
                    st.session_state['edit_button_location'] = submit_button_edit_location

                #If the submit button is clicked, remove the organization from the database#
                if submit_button_remove_location:
                    #Remove the organization from the database#
                    connection.execute(f"DELETE FROM locations WHERE id = '{edit_location_id}'")
                    #Show the user a message that the organization was removed#
                    st.success(f"Organization {edit_location_name} removed from database Successfully!")
                    time.sleep(.5)
                    st.experimental_rerun()
        
                #If the edit button is clicked, show the edit form#
                if st.session_state['edit_button_location'] == True:
                    #Set up the form to edit an organization#
                        edit_location_name = st.text_input("Location Name", value=pd.read_sql(f"SELECT location_name FROM locations WHERE id = '{edit_location_id}'", connection)['location_name'][0])
                        edit_location_address = st.text_input("Location Address", value=pd.read_sql(f"SELECT address FROM locations WHERE id = '{edit_location_id}'", connection)['address'][0])
                        edit_location_address_2 = st.text_input("Location Address 2", value=pd.read_sql(f"SELECT address_2 FROM locations WHERE id = '{edit_location_id}'", connection)['address_2'][0])
                        edit_location_city = st.text_input("Location City", value=pd.read_sql(f"SELECT city FROM locations WHERE id = '{edit_location_id}'", connection)['city'][0])
                        edit_location_state = st.text_input("Location State", value=pd.read_sql(f"SELECT state FROM locations WHERE id = '{edit_location_id}'", connection)['state'][0])
                        edit_location_zip = st.text_input("Location Zip", value=pd.read_sql(f"SELECT zip FROM locations WHERE id = '{edit_location_id}'", connection)['zip'][0])
                        edit_location_phone = st.text_input("Location Phone", value=pd.read_sql(f"SELECT phone FROM locations WHERE id = '{edit_location_id}'", connection)['phone'][0])
                        edit_location_email = st.text_input("Location Email", value=pd.read_sql(f"SELECT email FROM locations WHERE id = '{edit_location_id}'", connection)['email'][0])
                        edit_notes = st.text_input("Location Notes", value=pd.read_sql(f"SELECT notes FROM locations WHERE id = '{edit_location_id}'", connection)['notes'][0])

                        #Submit Changes#
                        push_submit_button_edit_location = st.form_submit_button(label='Accept Changes')
                        
                        if push_submit_button_edit_location:
                            #Make sure the edit location name is not already in the database#
                            try:
                                location_id = pd.read_sql(f"SELECT id FROM locations WHERE organization = '{org_id}' AND location_name = '{edit_location_name}'", connection)['id'][0]
                                st.error("Location already exists")
                            except:
                                #submit the changes to the database#
                                address_edit = edit_location_address + " "  + " " + edit_location_city + " " + edit_location_state + " " + edit_location_zip
                                edit_lat, edit_lon = dashboard_lib.get_location_lat_long(address_edit)
                                #check if a lat and lon were returned#
                                if edit_lat != None: 
                                    connection.execute(f"""UPDATE locations SET location_name = '{edit_location_name}', address = '{edit_location_address}', city = '{edit_location_city}', state = '{edit_location_state}', zip = '{edit_location_zip}',
                                                        phone = '{edit_location_phone}', email = '{edit_location_email}', notes = '{edit_notes}', latitude = '{edit_lat}', longitude = '{edit_lon}' WHERE id = '{edit_location_id}'""")
                                    #Show the user a message that the coalition was added#
                                    st.success(f"Location {edit_location_name} updated in database Successfully!")
                                    st.session_state['edit_button_location'] = False
                                    time.sleep(.5)
                                    st.experimental_rerun()
                                else:
                                    st.error(f"{address_edit} not found. Please check the address and try again.")                       
            except:
                st.form_submit_button("No locations to edit")
        ###Form for bulk delete of locations###
        with st.form(key='bulk_delete_locations_form'):
            try:
                st.header("Bulk Delete Locations")
                #Creates a dropdown of available organizations#
                bulk_delete_locations = st.multiselect("Select Locations to Delete", options=pd.read_sql(f"SELECT location_name FROM locations WHERE organization = '{org_id}'", connection)['location_name'].to_list())

                #Convert the list of location names to a list of location ids#
                bulk_delete_locations_ids = []
                for location in bulk_delete_locations:
                    bulk_delete_locations_ids.append(str(pd.read_sql(f"SELECT id FROM locations WHERE location_name = '{location}'", connection)['id'][0]))
                #Set up the submit button#
                submit_button_bulk_delete_locations = st.form_submit_button(label='Delete Locations')
                #If the submit button is clicked, remove the organization from the database#
                if submit_button_bulk_delete_locations:
                    #Remove the organization from the database#
                    for location in bulk_delete_locations_ids:
                        connection.execute(f"DELETE FROM locations WHERE id = '{location}'")
                    #Show the user a message that the organization was removed#
                    st.success(f"Locations removed from database Successfully!")
                    time.sleep(.5)
                    st.experimental_rerun()
            except:
                st.form_submit_button("No locations to delete")
    else:
        st.error("You must be logged in as an admin to view this page")

def new_coalition_page(connection):
    #Check if user is logged in, and only gives access if they are an admin#
    if st.session_state['user'] != "None" and st.session_state['role'] == 'admin' and st.session_state['admin_for'] == 'all':
        #Set up Title#
        st.header("Add a New Coalition")

        #Set up the form#
        with st.form(key='new_coalition_form'):
            coalition_id = str(random.randint(100000,100000000))
            st.text("New Coalition ID: " + coalition_id)
            coalition_name = st.text_input("Coalition Name")
            coalition_website = st.text_input("Coalition Website")
            coalition_zip = st.text_input("Please enter the zip code for the coalition to be used for the map")
            new_lat,new_lon = get_location_lat_long(coalition_zip)
            #Set up the submit button#
            submit_button_add = st.form_submit_button(label='Add Coalition')

            #If the submit button is clicked, add the new coalition to the database as long as it doesnt exist#
            if submit_button_add:
                try:
                #Add the new coalition to the database#
                    connection.execute(f"""INSERT INTO coalitions (id_coalition, coalition_name, website, zip, latitude, longitude) VALUES ('{coalition_id}', '{coalition_name}', '{coalition_website}', '{coalition_zip}', '{new_lat}', '{new_lon}')""")
                   
                    #Show the user a message that the coalition was added#
                    st.success(f"Coalition {coalition_name} added to database with ID {coalition_id}")
                except:
                #Show the user a message that the coalition was not added#
                    st.error(f"Coalition {coalition_name} was not added to database, please make the coalition does not already exist.")

        #Remove coalition from database#
        st.header("Edit/Remove a Coalition")

        #Set up the form#
        with st.form(key='remove_coalition_form'):
            coalition_name = st.selectbox("Coalition Name", options=pd.read_sql("SELECT coalition_name FROM coalitions", connection)['coalition_name'])

            #Set up the submit button#
            submit_button_remove = st.form_submit_button(label='Remove')
        
        
            #Set up edit button#
            submit_button_edit = st.form_submit_button(label='Edit Coalition')
            #logic for edit button session state#
            if st.session_state.get('edit_button') != True:
                st.session_state['edit_button'] = submit_button_edit

            #If the submit_remove button is clicked, remove the coalition from the database as long as it exists in DB#
            if submit_button_remove:
                try:
                #Remove the coalition from the database#
                    connection.execute(f"DELETE FROM coalitions WHERE coalition_name = '{coalition_name}'")
                #Show the user a message that the coalition was removed#
                    st.success(f"Coalition {coalition_name} removed from database")
                    st.experimental_rerun()
                except:
                #Show the user a message that the coalition was not removed#
                    st.error(f"Coalition {coalition_name} was not removed from database, please mak sure the coalition exists.")
            
            #check if edit button is clicked#
            if st.session_state.get('edit_button') == True:
                edit_coalition_id = pd.read_sql(f"SELECT id_coalition FROM coalitions WHERE coalition_name = '{coalition_name}'", connection)['id_coalition'][0]
                new_coalition_name = st.text_input("Enter New Coalition Name", key='new_coalition_name', value=coalition_name)
                new_coalition_website = st.text_input("Enter New Coalition Website", key='new_coalition_website', value=pd.read_sql(f"SELECT website FROM coalitions WHERE id_coalition = {edit_coalition_id}", connection)['website'][0])
                new_zip = st.text_input("Enter New Zip Code to move marker on the map", key='new_zip', value=pd.read_sql(f"SELECT zip FROM coalitions WHERE id_coalition = {edit_coalition_id}", connection)['zip'][0])
                new_lat, new_lon = get_location_lat_long(new_zip)
                submit_button_edit_complete = st.form_submit_button(label='Accept Changes')
                #If the submit_edit button is clicked, edit the coalition name in the database as long as it exists in DB#   
                if submit_button_edit_complete:
                    try:
                    #Edit the coalition name in the database#
                        connection.execute(f"UPDATE coalitions SET coalition_name = '{new_coalition_name}', website = '{new_coalition_website}', zip = {new_zip}, latitude = '{new_lat}', longitude = '{new_lon}' WHERE id_coalition = '{edit_coalition_id}'")
                    #Show the user a message that the coalition name was changed#
                        st.success(f"Coalition {coalition_name} changed to {new_coalition_name}")
                    except:
                    #Show the user a message that the coalition name was not changed#
                        st.error(f"Coalition {coalition_name} was not changed, please mak sure the coalition exists.")

        #Display the list of coalitions#
        st.header("List of Coalitions")
        coalitions = pd.read_sql("SELECT * FROM coalitions", connection)
        coalitions.columns = coalitions.columns.str.replace('_', ' ')
        coalitions.columns = coalitions.columns.str.title()

        st.dataframe(coalitions)

    #If the user is not logged in, show them a message#
    else:
        st.error("You do not have access to this page")

def new_users_page(connection):
    #Set up the form to add a new user#
        if st.session_state['role'] == "admin":
            st.header("Add New User")
            with st.form(key='add_user_form'):
                #Set up the form fields#
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type='password')
                confirm_password = st.text_input("Confirm New Password", type='password')
                new_role = st.selectbox("New Role", ["admin", "user"])     
                
                #Check the type of admin adding the user#
                if st.session_state['admin_for'] != "all":
                    new_admin_for_id = st.session_state['admin_for']
                    st.write(f"Admin For: {pd.read_sql(f'SELECT coalition_name FROM coalitions WHERE id_coalition = {new_admin_for_id}', connection)['coalition_name'][0]}")
                else:
                    new_admin_for = st.selectbox("Admin For", pd.read_sql("SELECT coalition_name FROM coalitions", connection)['coalition_name'].tolist() + ["all"])
                    if new_admin_for == "all":
                        new_admin_for_id = "all"
                    else:    
                        new_admin_for_id = pd.read_sql(f"SELECT id_coalition FROM coalitions WHERE coalition_name = '{new_admin_for}'", connection)['id_coalition'][0]
               
                #make sure the passwords match#
                if new_password != confirm_password:
                    st.error("New Passwords do not match")
                else:
                    submit_button_add_user = st.form_submit_button(label='Add User')
                    if submit_button_add_user:
                        if pd.read_sql(f"SELECT * FROM users WHERE username = '{new_username}'", connection).empty:
                            
                            #hash the password#
                            new_pass_hash = hashlib.sha256(new_password.encode()).hexdigest()
                            connection.execute(f"INSERT INTO users (username, password, role, admin_for_coalition) VALUES ('{new_username}', '{new_pass_hash}', '{new_role}', '{new_admin_for_id}')")
                            st.success("User Added!")
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error("Username already exists")
            st.markdown("---")   
        
        #display all users#
        if st.session_state['role'] == "admin" and st.session_state['admin_for'] == "all":
            users = pd.read_sql("SELECT * FROM users", connection)
            users['password'] = "********"
            for index, row in users.iterrows():
                if row['admin_for_coalition'] != "all":
                    users.loc[index, 'admin_for_coalition'] = pd.read_sql(f"SELECT coalition_name FROM coalitions WHERE id_coalition = {row['admin_for_coalition']}", connection)['coalition_name'][0]
            st.write(users)
            
            users_no_global_admins = users[users['admin_for_coalition'] != "all"]
            with st.expander('Change password for a coalition admin (Cannot change for global admins)'):
                with st.form(key='change_other_user_password_form'):
                    username = st.selectbox("Username", users_no_global_admins['username'].tolist())
                    new_password = st.text_input("New Password", type='password')
                    confirm_password = st.text_input("Confirm New Password", type='password')
                    if new_password != confirm_password:
                        st.error("New Passwords do not match")
                    else:
                        submit_button_change_password = st.form_submit_button(label='Change Password')
                        if submit_button_change_password:
                            #hash the password#
                            new_pass_hash = hashlib.sha256(new_password.encode()).hexdigest()
                            connection.execute(f"UPDATE users SET password = '{new_pass_hash}' WHERE username = '{username}'")
                            st.success("Password Changed!")
                            time.sleep(1)
                            st.experimental_rerun()

        elif st.session_state['role'] == "admin" and st.session_state['admin_for'] != "all":
            users = pd.read_sql(f"SELECT * FROM users WHERE admin_for_coalition = {st.session_state['admin_for']}", connection)
            users['password'] = "********"
            for index, row in users.iterrows():
                if row['admin_for_coalition'] != "all":
                    users.loc[index, 'admin_for_coalition'] = pd.read_sql(f"SELECT coalition_name FROM coalitions WHERE id_coalition = {row['admin_for_coalition']}", connection)['coalition_name'][0]
            st.write(users)

def dashboard_map(map_df, connection):
    
    ###Folium map###
    st.header("New York Digital Inclusion Map")
    st.image('images/map_legend.png', width=180)

    #center on New York State  
    m = folium.Map(location=[43.0000, -75.0000], zoom_start=6, max_zoom=14, min_zoom=6)

    #Iterate through the dataframe or organizations and plot each point
    try: 
        for index, row in map_df.iterrows():
            
            #DI Resources Provided
            if row['digital_inclusion_need_device'] == 1:
                di_device = 'Yes'
            else:
                di_device = 'No'
            
            if row['digital_inclusion_need_broadband'] == 1:
                di_broadband = 'Yes'
            else:
                di_broadband = 'No'
            
            if row['digital_inclusion_need_education'] == 1:
                di_edu = 'Yes'
            else:
                di_edu = 'No'

            #Create a popup with the organization information
            html = f'''
                        Organization: {row['location_name']} <br>
                        <br>

                        Organization Type: {row['organization_type']} <br>
                        Program: {row['program_name']} <br>
                        Population Served: {row['population_name']} <br>
                        Status: {row['program_status']} <br>
                        Website: {row['website']} <br>
                        
                        <br>
                        Services Provided: <br>
                        Device Access: {di_device} <br>
                        Broadband Acces/Affordability: {di_broadband} <br>
                        Education/Skills: {di_edu} <br>

                        <br>
                        Contact Information (Location) <br>
                        Phone: {row['phone_location']} <br>
                        Email: {row['email_location']} <br>

                        <br>
                        Contact Information (Organization) <br>
                        Contact Name: {row['contact']} <br>
                        Phone: {row['phone']} <br>
                        Email: {row['email']} <br>

                        <br>
                        Location: <br>
                        Address: {row['address']} <br>
                        Address 2: {row['address_2']} <br>
                        City: {row['city']} <br>
                        State: {row['state']} <br>
                        Zip: {row['zip']} <br>

                    '''
            
            #Create a popup with the organization information
            iframe = folium.IFrame(html, width=400,height=200)
            popup = folium.Popup(iframe, max_width=400)
            
            #place a marker on the map
            folium.Marker([row['latitude'],row['longitude']], popup=popup, tooltip=row['location_name'], icon=folium.Icon(color='blue')).add_to(m)
    except:
        pass
    #iterate through the dataframe of coalitions and plot each point
    df_coaltions = pd.read_sql("SELECT * FROM coalitions", connection)
    for index, row in df_coaltions.iterrows():
        html = f'''
                    Coalition: {row['coalition_name']} <br>
                    Website: {row['website']} <br>

                '''
        iframe = folium.IFrame(html, width=300,height=55)
        popup = folium.Popup(iframe, max_width=400)
        folium.Marker([row['latitude'],row['longitude']], popup=popup, tooltip=row['coalition_name'], icon=folium.Icon(color='red')).add_to(m)

    folium_static(m)

def dashboard_map_search(map_df):
    # Search Functionality for Nearest Organization to User Location (Zipcode)
        with st.form(key='distance_search'):

            st.header("Search for the nearest organizations")
            st.write("Please select the filters on the left you would like to use to find the nearest organization to your location.")
            st.write("If you would like to change the filters please click the 'Search' button again.") 
            address_distance_search = st.text_input(label="Please enter your address") #User Input for Address
            city_distance_search = st.text_input(label="Please enter your city")
            state_distance_search = st.text_input(label="Please enter your state")
            zipcode_distance_search = st.text_input(label="Please enter your zipcode")
            results_distance_search_size = st.number_input(label="Please enter the number of results you would like to see", min_value=1, max_value=30, value=5)
            checkbox_see_map = st.checkbox(label="See Map", value=True)

            #convert the address to a lat/long
            lat, lon = dashboard_lib.get_location_lat_long(address_distance_search + ' ' + city_distance_search + ' ' + state_distance_search + ' ' + str(zipcode_distance_search))

            #Define Progress bar for search function
            def progress_bar():
                    for pct_complete in range (1,121,20):
                        sleep(0.25)
                        pct_complete = min(pct_complete,100)
                        my_bar.progress(pct_complete)

        # Search Button for zipcode search (Displays nearest organization to user location)
            if st.form_submit_button("Search"):
                with st.spinner("Please wait while we search the database"):
                    my_bar = st.progress(0)
                    progress_bar()
                    st.markdown("---")        
                    st.write("Your Zipcode is", zipcode_distance_search)
                    st.write("GPS Coordinates: ", lat, lon)
                    st.subheader("Results:")
                    
                    try:    
                        df_location = map_df[[
                            'organization',
                            'organization_type',
                            'location_name',
                            'program_name',
                            'program_status',
                            'address',
                            'address_2',
                            'city',
                            'state',
                            'zip',
                            'phone_location',
                            'email_location',
                            'website',
                            'latitude',
                            'longitude',
                            'digital_inclusion_need_device',
                            'digital_inclusion_need_broadband',
                            'digital_inclusion_need_education'
                            ]]
                        
                        df_location['distance (in miles)'] = df_location.apply(lambda x: distance((lat,lon),(x['latitude'],x['longitude'])).miles,axis=1)
                        
                        #Move the distance column to the front of the dataframe
                        cols = df_location.columns.tolist()
                        cols = cols[-1:] + cols[:-1]
                        df_location = df_location[cols]

                        #Sort the dataframe by distance and display the top X results
                        df_location = df_location.sort_values(by='distance (in miles)')
                        df_location = df_location.head(results_distance_search_size)
                        st.session_state['df_location'] = True
                    except:
                        st.write("No results found")
                        del st.session_state['df_location']
                    

        # Display the map with the nearest organizations to user location
        if 'df_location' in st.session_state and checkbox_see_map == True:
            try:
              
                m = folium.Map(location=[lat,lon], zoom_start=9, max_zoom=14, min_zoom=6)
                st.dataframe(df_location)
                for index, row in df_location.iterrows():
                            #DI Resources Provided
                    if row['digital_inclusion_need_device'] == 1:
                        di_device = 'Yes'
                    else:
                        di_device = 'No'
                    
                    if row['digital_inclusion_need_broadband'] == 1:
                        di_broadband = 'Yes'
                    else:
                        di_broadband = 'No'
                    
                    if row['digital_inclusion_need_education'] == 1:
                        di_edu = 'Yes'
                    else:
                        di_edu = 'No'
                            
                    
                    html = f'''
                        Organization: {row['location_name']} <br>
                        <br>
                        Organization Type: {row['organization_type']} <br>
                        Program: {row['program_name']} <br>
                        Status: {row['program_status']} <br>
                        Website: {row['website']} <br>
                        
                        <br>
                        Services Provided: <br>
                        Device Access: {di_device} <br>
                        Broadband Acces/Affordability: {di_broadband} <br>
                        Education/Skills: {di_edu} <br>

                        <br>
                        Contact Information (Location) <br>
                        Phone: {row['phone_location']} <br>
                        Email: {row['email_location']} <br>


                        <br>
                        Location: <br>
                        Address: {row['address']} <br>
                        Address 2: {row['address_2']} <br>
                        City: {row['city']} <br>
                        State: {row['state']} <br>
                        Zip: {row['zip']} <br>

                    '''
                    iframe = folium.IFrame(html, width=400,height=200)
                    popup = folium.Popup(iframe, max_width=400)
                    folium.Marker([row['latitude'],row['longitude']], popup=popup, tooltip=row['location_name'], icon=folium.Icon(color='blue')).add_to(m)
            
            
                #Display the map
                folium_static(m)
        
            except:
                st.write("No results found! Please make sure you have entered a valid address. If you have changed a filter, please click the search button again.")
                del st.session_state['df_location']


        if 'df_location' in st.session_state:
            df_location.drop(['latitude','longitude'],axis=1, inplace=True)
            st.table(df_location)
            st.download_button(
                    label="Download of Nearest Digital Inclusion Resources",
                    data=dashboard_lib.convert_df(df_location),
                    file_name="Nearest Digital Inclusion Resources.csv",
                    mime='text/csv')
