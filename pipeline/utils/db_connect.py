from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')
import os

def src_db_connection():
    """
    Establishes a connection to the database using SQLAlchemy.
    Returns the database engine object.
    """
    try:
        database = os.getenv("SRC_POSTGRES_DB")
        host = os.getenv("SRC_POSTGRES_HOST")
        user = os.getenv("SRC_POSTGRES_USER")
        password = os.getenv("SRC_POSTGRES_PASSWORD")
        port = os.getenv("SRC_POSTGRES_PORT")

        conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(conn_string)
        print("Source DB connected successfully")
        return engine

    except Exception as e:
        print("Error connecting to Source DB")
        print(e)
        return None


def dwh_db_connection():
    try:
        database = os.getenv("DWH_POSTGRES_DB")
        host = os.getenv("DWH_POSTGRES_HOST")
        user = os.getenv("DWH_POSTGRES_USER")
        password = os.getenv("DWH_POSTGRES_PASSWORD")
        port = os.getenv("DWH_POSTGRES_PORT")

        conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(conn_string)
        print("DWH DB connected successfully")
        return engine

    except Exception as e:
        print("Error connecting to DWH DB")
        print(e)
        return None