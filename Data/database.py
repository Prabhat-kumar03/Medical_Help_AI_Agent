import os
import dotenv
import mysql.connector

dotenv.load_dotenv(".env")

# fetch data from Database
def get_patient_by_name(patient_name: str):
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("HOST"),
            user=os.environ.get("USER"),
            password=os.environ.get("PASSWORD"),
            database=os.environ.get("DATABASE"),
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database.")
            sql_query = "SELECT * FROM patient_reports WHERE name = %s"
            cursor = connection.cursor()
            cursor.execute(sql_query, (patient_name,))
            records = cursor.fetchall()
            if records:
                return records
            return None
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")

    finally:
        if "cursor" in locals() and cursor:
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()


