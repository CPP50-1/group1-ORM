import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the variables (matching the names in your .env file)
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST", "localhost")  # Defaults to localhost if not in .env
DB_PORT = os.getenv("DB_PORT", "5432")       # Defaults to 5432 if not in .env

try:
    # Pass the variables directly to the connection string parameters
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        password=DB_PASS,
        port=DB_PORT
    )
except (Exception, psycopg2.DatabaseError) as error:
    print(f"I am unable to connect to the database: {error}")
    # Exit the script if the connection fails
    exit(1)

# we use a context manager to scope the cursor session
with conn.cursor() as curs:

    try:
        # simple single row system query
        curs.execute("SELECT version()")

        # returns a single row as a tuple
        single_row = curs.fetchone()

        # use an f-string to print the single tuple returned
        print(f"{single_row}")

        # simple multi row system query
        curs.execute("SELECT query, backend_type FROM pg_stat_activity")

        # a default install should include this query and some backend workers
        many_rows = curs.fetchmany(5)

        # use the * unpack operator to print many_rows which is a Python list
        print(*many_rows, sep="\n")

    # a more robust way of handling errors
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)