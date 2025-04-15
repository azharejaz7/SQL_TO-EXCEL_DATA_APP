# SQL to Excel Converter App

A Streamlit application that connects to SQL Server databases, executes queries, and allows downloading results as Excel or CSV files. The app also includes file conversion functionality and secure user authentication.

## Features

- Secure user authentication with password protection
- SQL Server database connection and query execution
- Data filtering and parameter selection
- Excel and CSV file export
- File upload and conversion between formats
- Data visualization and cleaning options

## Deployment on Streamlit Cloud

### 1. Push Code to GitHub

First, push your code to a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

### 2. Setup Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch, and main file (app.py)
5. Click "Deploy"

### 3. Configure Environment Variables

In Streamlit Cloud:
1. Go to your app settings
2. Click on "Secrets"
3. Add the following secrets in TOML format:

```toml
# SQL Server Connection
SQL_SERVER = "your_server_name"
SQL_USER = "your_username"
SQL_PASSWORD = "your_password"

# Authentication
AUTH_COOKIE_NAME = "auth_cookie"
AUTH_COOKIE_KEY = "your_cookie_key"
AUTH_COOKIE_EXPIRY_DAYS = 30

# User Credentials
USER1_NAME = "Azhar Ejaz"
USER1_USERNAME = "azharejaz7"
USER1_PASSWORD = "your_hashed_password"

USER2_NAME = "Salman Amin"
USER2_USERNAME = "salman7"
USER2_PASSWORD = "your_hashed_password"

# Database Selection
DB1_NAME = "Pharma Solution"
DB1_VALUE = "PS_TRADE"
DB2_NAME = "Hussain Trader"
DB2_VALUE = "Pharma_solution"
```

> **Note on SQL Server Connectivity**: Streamlit Cloud might have limitations connecting to external SQL Server databases. Ensure your database is accessible from the internet with proper security measures.

### 4. Special Considerations for SQL Server

For SQL Server connectivity on Streamlit Cloud:

1. You might need to install ODBC drivers using a `packages.txt` file:
   ```
   unixodbc
   unixodbc-dev
   ```

2. Consider using alternative connection methods like REST APIs or cloud database services if direct SQL Server connection doesn't work.

## Local Development

To run the app locally:

1. Create a `.env` file with the environment variables listed above
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`

## Troubleshooting

- If you experience SQL Server connection issues, ensure your server allows remote connections
- For authentication issues, verify that your credentials in the environment variables are correct
- Check Streamlit Cloud logs for any deployment errors 