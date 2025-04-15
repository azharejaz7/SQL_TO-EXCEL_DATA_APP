import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get environment variables
AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME")
AUTH_COOKIE_KEY = os.getenv("AUTH_COOKIE_KEY")
AUTH_COOKIE_EXPIRY_DAYS = int(os.getenv("AUTH_COOKIE_EXPIRY_DAYS", "30"))

# Create a credentials dictionary
credentials = {
    "usernames": {
        os.getenv("USER1_USERNAME"): {
            "name": os.getenv("USER1_NAME"),
            "password": os.getenv("USER1_PASSWORD")
        },
        os.getenv("USER2_USERNAME"): {
            "name": os.getenv("USER2_NAME"),
            "password": os.getenv("USER2_PASSWORD")
        }
    }
}

# Create a cookie dictionary
cookie = {
    "name": AUTH_COOKIE_NAME,
    "key": AUTH_COOKIE_KEY,
    "expiry_days": AUTH_COOKIE_EXPIRY_DAYS
}

# Create a config dictionary
config = {
    "credentials": credentials,
    "cookie": cookie
}

# Initialize authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Handle login
try:
    # Try different login methods
    st.write("Testing login method 1:")
    login_result = authenticator.login("Login", "main")
    
    if login_result is None:
        st.warning("Please enter your credentials")
    else:
        name, authentication_status, username = login_result
        st.write(f"Login result: {name}, {authentication_status}, {username}")
        
        if authentication_status:
            st.success(f"Welcome {name}!")
            authenticator.logout("Logout", "sidebar", key="logout_button")
        elif authentication_status == False:
            st.error("Username/password is incorrect")
        elif authentication_status == None:
            st.warning("Please enter your username and password")
            
except Exception as e:
    st.error(f"Login error: {e}")
    
# Display environment variables for debugging
st.write("Environment variables:")
st.write(f"SQL_SERVER: {os.getenv('SQL_SERVER')}")
st.write(f"SQL_USER: {os.getenv('SQL_USER')}")
st.write(f"AUTH_COOKIE_NAME: {os.getenv('AUTH_COOKIE_NAME')}")
st.write(f"AUTH_COOKIE_KEY: {os.getenv('AUTH_COOKIE_KEY')}") 