###This page is used to add a new coalition to the database###
#External Imports
import streamlit as st
import pandas as pd
import time
import hashlib

#Internal Imports
from dashboard_lib import db_connection, get_logged_in, get_user_role
from dashboard_page_components import new_coalition_page, new_location_page, new_organization_page, new_users_page

###Connect to database###
connection = db_connection()

###Initialize session state###

#Check if user is logged in#
get_logged_in(connection)

#Check user role#
get_user_role(connection)

if 'user' not in st.session_state:
    st.session_state['user'] = "None"


#Creates a form to login#
if st.session_state['user'] == "None":
    st.header("Login")
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        #Set up the submit button#
        submit_button_login = st.form_submit_button(label='Login')

        #If submit button is clicked, check if the username and password are correct#
        if submit_button_login:
            pass_hash = hashlib.sha256(password.encode()).hexdigest()
            #Check the database to see if the username and password are correct#
            if pd.read_sql(f"SELECT * FROM users WHERE username = '{username}' AND password = '{pass_hash}'", connection).empty:
                #Show the user a message that the username or password is incorrect#
                st.error("Username or password is incorrect")
            else:
                #Show the user a message that the username and password are correct#
                st.success("Login Successful")
                #Set the session state to the username#
                st.session_state['user'] = username
                st.session_state['role'] = pd.read_sql(f"SELECT role FROM users WHERE username = '{username}'", connection)['role'][0]

                #Updates the database to show the user has logged in, and their last login#
                connection.execute(f"UPDATE users SET last_login = '{time.strftime('%Y-%m-%d %H:%M:%S')}', logged_in = 1 WHERE username = '{username}'")
                #sets query parameters to the username and role#
                st.experimental_set_query_params(user=st.session_state['user'])
                time.sleep(.5)
                st.experimental_rerun()
else:
    #If the user is logged in, show the user a message that they are logged in and set up the page tabs# 
    st.header("Welcome, " + st.session_state['user'].capitalize() + "!") 
    st.subheader("Please remember to logout when finished!")
    st.write('''Please note that either a ' or " in a field will cause an error. Please avoid using these characters in your entries.''')
    profile_tab, coalitions_tab, organizations_tab, locations_tab, users_tab, logout_tab = st.tabs(["Profile", "Coalitions", "Organizations", "Locations", "Users", "Logout"])

    #logout tab#
    with logout_tab:
        #Set up the logout button#
        st.write("To logout, click the logout button below")
        
        if st.button("Logout"):
            #Updates the database to show the user has logged out#
            connection.execute(f"UPDATE users SET logged_in = 0 WHERE username = '{st.session_state['user']}'")
            time.sleep(.5)
            st.experimental_set_query_params(user="None")
            st.session_state['user'] = "None"
            st.session_state['role'] = "None"
            time.sleep(.5)
            st.experimental_rerun()
    
    #Profile Tab#
    with profile_tab:

        st.header(f"Account Role: {st.session_state['role']}")
        #Set up the form to change password#
        st.header("Change Password")
        with st.form(key='change_password_form'):
            old_password = st.text_input("Old Password", type='password')
            new_password = st.text_input("New Password", type='password')
            confirm_password = st.text_input("Confirm New Password", type='password')

            if new_password != confirm_password:
                st.error("New Passwords do not match")
            else:
                submit_button_change_password = st.form_submit_button(label='Change Password')
                if submit_button_change_password:
                    old_pass_hash = hashlib.sha256(old_password.encode()).hexdigest()
                    new_pass_hash = hashlib.sha256(new_password.encode()).hexdigest()
                    if pd.read_sql(f"SELECT * FROM users WHERE username = '{st.session_state['user']}' AND password = '{old_pass_hash}'", connection).empty:
                        st.error("Old password is incorrect")
                    else:
                        st.success("Password Changed!")
                        connection.execute(f"UPDATE users SET password = '{new_pass_hash}' WHERE username = '{st.session_state['user']}'")
                        time.sleep(1)
                        st.experimental_rerun()
        
        st.markdown("---")
         #Set up the form to delete current user#
        st.header("Delete Account")

        with st.form(key='delete_user_form'):
            password = st.text_input("Password", type='password')
            confirm_password = st.text_input("Confirm Password", type='password')
            
            submit_button_delete_user = st.form_submit_button(label='Delete Account')
            
            if submit_button_delete_user:
                pass_hash = hashlib.sha256(password.encode()).hexdigest()
                if pd.read_sql(f"SELECT * FROM users WHERE username = '{st.session_state['user']}' AND password = '{pass_hash}'", connection).empty:
                    st.error("Password is incorrect")
                else:
                    if password == confirm_password:
                        if st.session_state['role'] == "admin" and pd.read_sql(f"SELECT * FROM users WHERE admin_for_coalition = '{st.session_state['admin_for']}'", connection).shape[0] == 1:
                            st.error("Cannot delete final administrator account for coalition")
                        else:
                            connection.execute(f"DELETE FROM users WHERE username = '{st.session_state['user']}'")
                            st.success("Account Deleted!")
                            st.experimental_set_query_params(user="None", role="None")
                            
                            time.sleep(1)
                            st.experimental_rerun()
                    else:
                        st.error("Passwords do not match")
    
    #Users Tab#
    with users_tab:
        new_users_page(connection)
    
    #Coalitions Tab#
    with coalitions_tab:
       new_coalition_page(connection)
    
    #Organizations Tab#
    with organizations_tab:
        new_organization_page(connection)
    
    #Locations Tab#
    with locations_tab:
        new_location_page(connection)





        




