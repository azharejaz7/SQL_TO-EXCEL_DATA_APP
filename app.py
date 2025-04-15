# Imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO 
import openpyxl
import pyodbc
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import logging
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import json
import toml
from pathlib import Path
from dotenv import load_dotenv
import bcrypt

# Load environment variables from .env file if it exists
if os.path.exists(".env"):
    load_dotenv()
st.set_page_config(page_title="💾 SQL TO EXCEL", layout="wide")

# Get environment variables with defaults for cloud deployment
SQL_SERVER = os.getenv("SQL_SERVER", "")
SQL_USER = os.getenv("SQL_USER", "")
SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")
AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "auth_cookie")
AUTH_COOKIE_KEY = os.getenv("AUTH_COOKIE_KEY", "default_insecure_key")
AUTH_COOKIE_EXPIRY_DAYS = int(os.getenv("AUTH_COOKIE_EXPIRY_DAYS", "30"))

# Log startup info
print(f"Starting app with SQL server: {SQL_SERVER}")

# Helper function to check if a password is already hashed
def is_hashed(password):
    return password and password.startswith("$2b$") and len(password) > 50

# Helper function to hash a password if it's not already hashed
def hash_password_if_needed(password):
    if not password:
        return None
    if is_hashed(password):
        return password
    else:
        return stauth.Hasher([password]).generate()[0]

# Create a credentials dictionary from environment variables with fallbacks
try:
    # Get user credentials
    user1_username = os.getenv("USER1_USERNAME", "")
    user1_name = os.getenv("USER1_NAME", "")
    user1_password = os.getenv("USER1_PASSWORD", "")
    
    user2_username = os.getenv("USER2_USERNAME", "")
    user2_name = os.getenv("USER2_NAME", "")
    user2_password = os.getenv("USER2_PASSWORD", "")
    
    # Hash passwords if needed
    user1_password = hash_password_if_needed(user1_password)
    user2_password = hash_password_if_needed(user2_password)
    
    print(f"User 1 username: {user1_username}, name: {user1_name}")
    print(f"User 2 username: {user2_username}, name: {user2_name}")
    
    # Create credentials dictionary
    credentials = {
        "usernames": {}
    }
    
    # Add users to credentials dictionary
    if user1_username and user1_name and user1_password:
        credentials["usernames"][user1_username] = {
            "name": user1_name,
            "password": user1_password
        }
        
    if user2_username and user2_name and user2_password:
        credentials["usernames"][user2_username] = {
            "name": user2_name,
            "password": user2_password
        }
    
    # Ensure we have at least one valid user
    if not credentials["usernames"]:
        st.warning("No valid users found in environment variables! Adding a default test user.")
        # Hash a default password
        default_password = hash_password_if_needed("password")
        credentials["usernames"]["admin"] = {
            "name": "Admin User",
            "password": default_password
        }
        st.info("Default credentials: username = 'admin', password = 'password'")
    
    print(f"Available users: {list(credentials['usernames'].keys())}")
    
except Exception as e:
    st.error(f"Error setting up credentials: {e}")
    # Create a default admin user with a properly hashed password
    default_password = hash_password_if_needed("password")
    credentials = {
        "usernames": {
            "admin": {
                "name": "Admin",
                "password": default_password
            }
        }
    }
    st.info("Using default credentials due to error: username = 'admin', password = 'password'")

# Create a cookie dictionary from environment variables
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
try:
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
except Exception as e:
    st.error(f"Authentication error: {e}")
    st.stop()

# Handle login - with proper return value checking
try:
    col1, col2 = st.columns(2)
    with col1:
        st.title("💾 Software Data To Excel")
        st.write("Connect to SQL Server and convert data to CSV or Excel")
    # Returns (name, authentication_status, username) or None if not submitted
    with col2:
        login_result = authenticator.login("Login", "main")
    
    if login_result is None:
        st.warning("Please enter your credentials")
        st.stop()  # Stop execution if form not submitted
    
    name, authentication_status, username = login_result
    print(f"Login attempt - username: {username}, status: {authentication_status}")

except Exception as e:
    st.error(f"Login error: {e}")
    st.stop()

# Handle Authentication Status
if authentication_status is False:
    st.error("❌ Username/password is incorrect")
    st.stop()
elif authentication_status is None:
    st.warning("⌨️ Please enter your username and password")
    st.stop()
elif authentication_status:
    # Get the real name from environment variables based on username
    if username == os.getenv("USER1_USERNAME"):
        display_name = os.getenv("USER1_NAME")
    elif username == os.getenv("USER2_USERNAME"):
        display_name = os.getenv("USER2_NAME")
    else:
        display_name = name  # Fallback to the name from authenticator
        
    st.sidebar.success(f"👋 Welcome, *{display_name}*!")
    authenticator.logout("Logout", "sidebar")
    
    # ✅ Your main app content goes here
    st.title("Secure Dashboard")
    st.write("You are successfully logged in!")
    # Your app code goes below

    # Setup logging config
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # File handler
    try:
        file_handler = logging.FileHandler("query_log.log")
        file_handler.setLevel(logging.DEBUG)

        # Console handler (optional)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    except Exception as e:
        st.warning(f"Logging setup error (non-critical): {e}")
        # Create a basic logger that just prints to console
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        logger.addHandler(handler)

    # Set up Streamlit app
    
    # Database selection from environment variables or defaults
    database_selecttion = {
        os.getenv("DB1_NAME", "Pharma Solution"): os.getenv("DB1_VALUE", "PS_TRADE"),
        os.getenv("DB2_NAME", "Hussain Trader"): os.getenv("DB2_VALUE", "Pharma_solution")
    }

    # Invoice Type Selection query
    invoice_type_selection = {
        "All": "",
        "Remaining": os.getenv("INVOICE_REMAINING", "AND DATEDIFF(DAY, refDate, GETDATE()) < DAYs"),
        "Over Credit": os.getenv("INVOICE_OVER_CREDIT", "AND DATEDIFF(DAY, refDate, GETDATE()) > DAYs"),
        "No Credit": os.getenv("INVOICE_NO_CREDIT", "AND TR.PaymentTerms = 'No Credit'"),
        "Removed Remaining": os.getenv("INVOICE_REMOVED_REMAINING", "AND NOT DATEDIFF(DAY, refDate, GETDATE()) < DAYs"),
        "Remove Over Credit": os.getenv("INVOICE_REMOVED_OVER_CREDIT", "AND NOT DATEDIFF(DAY, refDate, GETDATE()) > DAYs"),
        "Remove No Credit": os.getenv("INVOICE_REMOVED_NO_CREDIT", "AND NOT TR.PaymentTerms = 'No Credit'")
    }

    payment_terms_selection = {
        "All": "",
        "Cash": os.getenv("PAYMENT_CASH", "AND TR.Terms = 'CASH'"),
        "Cheque": os.getenv("PAYMENT_CHEQUE", "AND TR.Terms = 'cheque'")
    }

    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["SQL Data", "File Converter"])

    with tab1:
        st.header("SQL Server Connection")
        
        # SQL Server connection params
        with st.expander("Connection Settings"):
            col1, col2 = st.columns(2)
            with col1:
                server = st.text_input("Server", value=SQL_SERVER,disabled=True)
                selected_Db = st.selectbox("Select Database", list(database_selecttion.keys()))
                database = database_selecttion[selected_Db]
            with col2:
                username = st.text_input("Username", value=SQL_USER,disabled=True)
                password = st.text_input("Password", value=SQL_PASSWORD, type="password" ,disabled=True)
    
        # Date range selection
        st.subheader("Select Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now())
        with col2:
            end_date = st.date_input("End Date", datetime.now())
    
        # Additional parameters
        st.subheader("Additional Parameters")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            invoice_type_selected = st.selectbox("Invoice Record Type", list(invoice_type_selection.keys()))
            Invoice_type = invoice_type_selection[invoice_type_selected]
        with col2:
            peyment_terms_selected = st.selectbox("Payment Terms", list(payment_terms_selection.keys()))
            payment_terms = payment_terms_selection[peyment_terms_selected]
        with col3:
            acc2 = st.text_input("First Product Code ", os.getenv("FIRST_PRODUCT_CODE", "0001"),disabled=True)
        with col4:
            acc3 = st.text_input("Last Product Code", os.getenv("LAST_PRODUCT_CODE", "989801"),disabled=True)
        with col5:
            acc1 = st.text_input("ACC1", "",disabled=True)
        
        
        # Execute query button
        if st.button("Fetch Data"):
            try:
                # Validate connection parameters
                if not server or not database or not username:
                    st.error("Server, database, and username are required.")
                    st.stop()
                
                # Construct connection string
                conn_str = (
                    f"DRIVER={{SQL Server}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={username};"
                    f"PWD={password};"
                )
                
                # Format dates for SQL query
                start_date_str = start_date.strftime("%d-%b-%Y")
                end_date_str = end_date.strftime("%d-%b-%Y")
                
                # Connect to database
                with st.spinner("Connecting to database..."):
                    try:
                        conn = pyodbc.connect(conn_str)
                    except pyodbc.Error as e:
                        st.error(f"SQL Server Connection Error: {e}")
                        st.info("Note: If you're running in Streamlit Cloud, make sure your SQL Server is accessible from the internet.")
                        st.stop()
                    
                    # Modify the query with parameters
                    query = f"""
                    SELECT 
                        acc4 INST_Code,
                        tr.Company as Institute_Name,
                        HTPersonName HT_Person,
                        personName Related_Person,
                        tr.Id INVOICE_NO,
                        format(refDate,'dd-MMM-yyyy') as INV_Date,
                        format(AmtPayable,'N2') NET_AMT,
                        format(AmtReceived,'N2') RECVD_AMT,
                        format(SUM(AmtPayable - AmtReceived),'N2') AS Balance,
                        remarks REMARKS,
                        DATEDIFF(DAY, refDate, GETDATE()) AS Day_Passed,
                        CASE 
                            WHEN TR.CR_Days = 0 THEN DAYs 
                            ELSE TR.CR_Days 
                        END AS Day_LIMIT
                    FROM 
                        OUTSTANDINGLISTING_NEW('{start_date_str}','{end_date_str}','{acc1}','{acc2}','{acc3}') AS TR
                    LEFT JOIN 
                        M_PARTY ON TR.ACC4 = M_PARTY.Id
                    WHERE 
                        ReportType = 'Sales Invoices'
                            {Invoice_type} {payment_terms}
                    GROUP BY 
                        refDate,acc4, tr.Company, HTPersonName, personName, tr.Id, AmtPayable, AmtReceived, remarks,
                        creditLimit, Days,TR.CR_Days
                    """
                    logger.info(f"Running query on DB: {database}, From: {start_date_str} To: {end_date_str}, InvoiceType: {invoice_type_selected}, PaymentTerms: {peyment_terms_selected}")
                    logger.debug(f"SQL Query: {query}")
                    # Execute query
                    with st.spinner("Executing query..."):
                        try:
                            df = pd.read_sql(query, conn)
                            st.session_state.sql_df = df
                        except Exception as e:
                            st.error(f"Query execution error: {e}")
                            st.stop()
                        
                    st.success(f"Retrieved {len(df)} records")
                    
                    # Display data
                    df.columns = [col.replace("_", " ").title() for col in df.columns]
                    st.subheader("Query Results")
                    st.dataframe(df)
                    
                    # Download options
                    st.subheader("Download Options")
                    col1, col2 = st.columns(2)
                    
                    # Excel download
                    with col1:
                        buffer = BytesIO()
                        df.to_excel(buffer, index=False)
                        buffer.seek(0)
                        st.download_button(
                            label="Download as Excel",
                            data=buffer,
                            file_name=f"{selected_Db}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    # CSV download
                    with col2:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name=f"sql_data_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    
            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                st.error(f"Error: {str(e)}")

    with tab2:
        # File uploader
        uploaded_files = st.file_uploader("Upload Your File (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

        if uploaded_files:  # Ensures at least one file is uploaded
            for file in uploaded_files:
                file_ext = os.path.splitext(file.name)[-1].lower()

                # Read file into a DataFrame
                try:
                    if file_ext == ".csv":
                        df = pd.read_csv(file, encoding="cp1252")
                    elif file_ext == ".xlsx":
                        df = pd.read_excel(file)
                    else:
                        st.error(f"Unsupported file type: {file_ext}")
                        continue
                except Exception as e:
                    st.error(f"Error reading file {file.name}: {str(e)}")
                    continue
                    
                # store dataframe in session to persist updated data
                if "df" not in st.session_state:
                    st.session_state.df = df
                    
                # Display file details
                st.write(f"*File Name:* {file.name}")
                st.write(f"*File Size:* {file.size / 1024:.2f} KB")

                # Show file preview
                st.write("Current Preview of the DataFrame:")
                st.dataframe(df.head(20))

                # Data Cleaning Options
                st.subheader(f"Data Cleaning Options for {file.name}")
                if st.checkbox(f"Clean Data for {file.name}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(f"Remove Duplicates From {file.name}"):
                            st.session_state.df.drop_duplicates(inplace=True)
                            st.write("Removed Duplicates")

                    with col2:
                        if st.button(f"Fill Missing Values for {file.name}"):
                            numeric_cols = st.session_state.df.select_dtypes(include=['number']).columns
                            if len(numeric_cols) > 0:
                                st.session_state.df[numeric_cols] = st.session_state.df[numeric_cols].fillna(df[numeric_cols].mean())
                                st.write("Missing Values have been Filled")
                            else:
                                st.warning("No numeric columns found for filling missing values")
                            
                    st.write("Updated Preview of the DataFrame:")        
                    st.write(st.session_state.df)
                           
                # Choose Specific Columns to convert or Keep
                st.header("Select Columns to Convert")
                columns = st.multiselect(f"Choose Columns for {file.name}", st.session_state.df.columns, default=st.session_state.df.columns)
                st.session_state.df = st.session_state.df[columns]

                # Create some visualization
                st.header("📊 Data Visualization")
                if st.checkbox(f"Show Visualization for {file.name}"):
                    numeric_cols = st.session_state.df.select_dtypes(include='number')
                    if not numeric_cols.empty and numeric_cols.shape[1] >= 1:
                        st.bar_chart(numeric_cols.iloc[:,:2])
                    else:
                        st.warning("No numeric columns available for visualization")

                # Convert the file -> CSV to Excel 
                st.header("🔄 Conversion Options")
                conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
                if st.button(f"Convert {file.name}"):
                    buffer = BytesIO()
                    try:
                        if conversion_type == "CSV":
                            st.session_state.df.to_csv(buffer, index=False)
                            file_name = file.name.replace(file_ext, ".csv")
                            mime_type = "text/csv"
                        
                        elif conversion_type == "Excel":
                            st.session_state.df.to_excel(buffer, index=False)
                            file_name = file.name.replace(file_ext, ".xlsx")
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        buffer.seek(0)
                        
                        # Download Button
                        st.download_button(
                            label=f"Download {file.name} as {conversion_type}",
                            data=buffer,
                            file_name=file_name,
                            mime=mime_type
                        )
                        
                        st.success("🎉 Files Processed!")
                    except Exception as e:
                        st.error(f"Error converting file: {str(e)}")