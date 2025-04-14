# Imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO 
import openpyxl
import pyodbc
from datetime import datetime, timedelta
import streamlit.components.v1 as components  # ✅ Make sure this line is here
import logging
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import streamlit_authenticator as stauth
from dotenv import load_dotenv
import os


load_dotenv()
st.set_page_config(page_title="💾 SQL TO EXCEL", layout="wide")

# Define passwords and hash them

passwords = [os.getenv("USER1_PASSWORD"), os.getenv("USER2_PASSWORD")]
hashed_passwords = stauth.Hasher(passwords).generate()
# Users and authentication setup
names = [os.getenv("USER1_NAME"), os.getenv("USER2_NAME")]
usernames = [os.getenv("USER1_USERNAME"), os.getenv("USER2_USERNAME")]

authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    "my_app",  # app name (for cookie)
    "auth",    # cookie key
    cookie_expiry_days=1
)

# Layout: Two columns
col1, col2 = st.columns(2)

with col1:
    st.title("💾 Software Data To Excel")
    st.write("Connect to SQL Server and convert data to CSV or Excel")

with col2:
    name, authentication_status, username = authenticator.login("Login", "main")

# Auth logic
if authentication_status == False:
    st.error("❌ Incorrect username or password")

elif authentication_status == None:
    st.warning("🔐 Please enter your username and password")

elif authentication_status: 
    
    st.sidebar.success(f"Welcome, {name} 👋")
    
    # 👉 Your app main content starts here
    st.success("You're logged in! 🎉")
    # Your app code goes below

#setup loging config

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # File handler
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

    # Set up Streamlit app
    
    # database selection
    database_selecttion ={"Pharma Solution": "PS_TRADE",
    "Hussain Trader":"Pharma_solution"}

    # Invocie Type Selection query
    invoice_type_selection ={"All":"","Remaining":"AND DATEDIFF(DAY, refDate, GETDATE()) < DAYs","Over Credit":"AND DATEDIFF(DAY, refDate, GETDATE()) > DAYs",
    "No Credit":"AND TR.PaymentTerms = 'No Credit'","Removed Remaining":"AND NOT DATEDIFF(DAY, refDate, GETDATE()) < DAYs",
    "Remove Over Credit":"AND NOT DATEDIFF(DAY, refDate, GETDATE()) > DAYs","Remove No Credit":"AND NOT TR.PaymentTerms = 'No Credit'"}

    payment_terms_selection = {"All":"","Cash":"AND  TR.Terms = 'CASH'","Cheque":"AND  TR.Terms = 'cheque'"}
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["SQL Data", "File Converter"])

    with tab1:
        st.header("SQL Server Connection")
        
        # SQL Server connection params
        with st.expander("Connection Settings"):
            col1, col2 = st.columns(2)
            with col1:
                server = st.text_input("Server", value=os.getenv("SQL_SERVER"), disabled=True)
                selected_Db =st.selectbox("Select Database", list(database_selecttion.keys()))
                database = database_selecttion[selected_Db]
            with col2:
                username = st.text_input("Username", value=os.getenv("SQL_USER"), disabled=True)
                password = st.text_input("Password", value=os.getenv("SQL_PASSWORD"), type="password", disabled=True)
    
        # Date range selection
        st.subheader("Select Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now())
        with col2:
            end_date = st.date_input("End Date", datetime.now())
    
        # Additional parameters
        st.subheader("Additional Parameters")
        col1, col2, col3,col4,col5 = st.columns(5)
        with col1 :
            invoice_type_selected =st.selectbox("Invoice Record Type",list(invoice_type_selection.keys()))
            Invoice_type = invoice_type_selection[invoice_type_selected]
        with col2:
            peyment_terms_selected =st.selectbox("Payment Terms",list(payment_terms_selection.keys()))
            payment_terms =payment_terms_selection[peyment_terms_selected]
        with col3:
            acc2 = st.text_input("First Product Code ", "0001", disabled=True)
        with col4:
            acc3 = st.text_input("Last Product Code", "989801", disabled=True)
        with col5:
            acc1 = st.text_input("ACC1", "", disabled=True)
        
        
        # Execute query button
        if st.button("Fetch Data"):
            try:
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
                    conn = pyodbc.connect(conn_str)
                    
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
                        df = pd.read_sql(query, conn)
                        st.session_state.sql_df = df
                        
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
                logging.error(f"Error fetching data: {e}")
                st.error(f"Error: {str(e)}")
                st.error(f"Error: {str(e)}")

    with tab2:
        # File uploader
        uploaded_files = st.file_uploader("Upload Your File (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

        if uploaded_files:  # Ensures at least one file is uploaded
            for file in uploaded_files:
                file_ext = os.path.splitext(file.name)[-1].lower()

                # Read file into a DataFrame
                if file_ext == ".csv":
                    df = pd.read_csv(file, encoding="cp1252")
                elif file_ext == ".xlsx":
                    df = pd.read_excel(file)
                else:
                    st.error(f"Unsupported file type: {file_ext}")
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
                            st.session_state.df[numeric_cols] = st.session_state.df[numeric_cols].fillna(df[numeric_cols].mean())
                            st.write("Missing Values have been Filled")
                            
                    st.write("Updated Preview of the DataFrame:")        
                    st.write(st.session_state.df)           
                # Choose Specific Columns to convert or Keep
                st.header("Select Columns to Convert")
                columns = st.multiselect(f"Choose Columns for {file.name}", st.session_state.df.columns, default=st.session_state.df.columns)
                st.session_state.df = st.session_state.df[columns]

                #create some visualization
                st.header("📊 Data Visualization")
                if st.checkbox(f"Show Visualization for {file.name}"):
                    st.bar_chart(st.session_state.df.select_dtypes(include='number').iloc[:,:2])

                # Convert the file -> CSV to Excel 
                st.header("🔄 Conversion Options")
                conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
                if st.button(f"Convert {file.name}"):
                    buffer = BytesIO()
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

    authenticator.logout("Logout", "sidebar")