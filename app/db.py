import pandas as pd
import mysql.connector  # type: ignore

from utils.constants import REQUIRED_COLUMNS
from utils.helpers import EXAMPLE_DATA

# --- Connection ---


def get_connection(conn_info=None):
    """
    Establishes a MySQL connection using provided config or defaults.
    """
    if conn_info is None:
        raise ValueError("Missing connection info")

    return mysql.connector.connect(
        host=conn_info["host"],
        port=conn_info["port"],
        user=conn_info["user"],
        password=conn_info["password"],
        database=conn_info["database"]
    )

# --- Table creation logic ---


def ensure_schema_exists(conn_info):
    """Creates the necessary tables if they don't exist based on REQUIRED_COLUMNS."""
    conn = get_connection(conn_info)
    cursor = conn.cursor()

    table_definitions = {
        "cases": f"""
            CREATE TABLE IF NOT EXISTS cases (
                CaseID INT PRIMARY KEY,
                PartyID INT,
                `Case Title` VARCHAR(255),
                `Case Number` VARCHAR(100),
                `Court System` VARCHAR(100),
                Location VARCHAR(100),
                `Case Type` VARCHAR(100),
                `Filing Date` DATE,
                `Case Status` VARCHAR(50),
                `Judicial Officer` VARCHAR(100),
                eligible BOOLEAN DEFAULT FALSE
            )
        """,
        "charges": f"""
            CREATE TABLE IF NOT EXISTS charges (
                ChargeID INT PRIMARY KEY,
                CaseID INT,
                `Charge No` INT,
                `CJIS Code` VARCHAR(50),
                `Statute Code` VARCHAR(50),
                `Charge Description` VARCHAR(255),
                `Charge Class` VARCHAR(100),
                `Offense Date` DATE,
                `Agency Name` VARCHAR(255),
                Plea VARCHAR(100),
                `Plea Date` DATE,
                Disposition VARCHAR(100),
                `Disposition Date` DATE,
                `Jail Term (Years)` INT,
                `Probation (Years)` INT
            )
        """,
        "parties": f"""
            CREATE TABLE IF NOT EXISTS parties (
                PartyID INT PRIMARY KEY,
                Name VARCHAR(255),
                Race VARCHAR(50),
                Sex VARCHAR(10),
                DOB DATE,
                Address VARCHAR(255),
                City VARCHAR(100),
                State VARCHAR(10),
                `Zip Code` VARCHAR(20),
                Aliases VARCHAR(255)
            )
        """
    }

    for table, ddl in table_definitions.items():
        cursor.execute(ddl)

    conn.commit()
    cursor.close()
    conn.close()


def fetch_all_tables(conn_info):
    conn = get_connection(conn_info)
    cursor = conn.cursor(dictionary=True)

    def fetch(table):
        cursor.execute(f"SELECT * FROM {table}")
        return pd.DataFrame(cursor.fetchall())

    parties = fetch("parties")
    cases = fetch("cases")
    charges = fetch("charges")

    cursor.close()
    conn.close()

    return parties, cases, charges


def mark_case_eligible(conn_info, case_number):
    conn = get_connection(conn_info)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cases SET eligible = TRUE WHERE `Case Number` = %s", (
            case_number,)
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_eligible_cases(conn_info, case_df):
    eligible_cases = case_df[case_df["Eligibility"].str.startswith(
        "✅ Eligible", na=False)]

    for _, row in eligible_cases.iterrows():
        mark_case_eligible(conn_info, row["Case Number"])

