import logging
import luigi
import pandas as pd
import time
import sqlalchemy
from datetime import datetime
from pipeline.utils.db_connect import dwh_db_connection
from pipeline.utils.read_sql import read_sql_file
from pipeline.extract import ExtractData
import os
from dotenv import load_dotenv

load_dotenv()

DIR_ROOT_PROJECT = os.getenv("DIR_ROOT_PROJECT", default=os.getcwd())
DIR_TEMP_LOG = os.getenv("DIR_TEMP_LOG")
DIR_EXTRACT_QUERY = os.getenv("DIR_EXTRACT_QUERY")
DIR_TEMP_DATA = os.getenv("DIR_TEMP_DATA")
DIR_LOAD_QUERY = os.getenv("DIR_LOAD_QUERY")


class LoadData(luigi.Task):

    tables = ['public.aircrafts',
              'public.airlines',
              'public.airports',
              'public.customers',
              'public.hotel',
              'public.flight_bookings',
              'public.hotel_bookings']
    
    def requires(self):
        return ExtractData()

    def run(self):
        try:
            # Set up logging
            logging.basicConfig(level = logging.INFO,
                                filename=f'{DIR_TEMP_LOG}/logs.log',
                                format='%(asctime)s - %(levelname)s - %(message)s')
            
            # connect db
            try:
                dwh_engine = dwh_db_connection()
                logging.info("Connected to DWH database successfully.")
            except Exception as e:
                logging.error(f"Failed to connect to DWH database: {e}")
                return
            
            # truncate tables
            try:
                for table in self.tables:
                    table_name = table.split(".")[1]
                    with dwh_engine.connect() as conn:
                        cursor = conn.connection.cursor()
                        cursor.execute(f"TRUNCATE TABLE pactravel.{table_name} CASCADE;")
                        conn.commit()
                logging.info("Truncate tables - SUCCESS")

            except Exception as e:
                logging.error(f"Truncate tables - FAILED: {e}")
                raise
            
            # load data into source schema (copied as is from extracted data)
            start_time = time.time()
            logging.info('----------Start loading data to pactravel schema----------')
            
            try:
                for idx, table in enumerate(self.tables):
                    table_name = table.split(".")[1]
                    logging.info(f'starting to load data into table {table_name}...')
                    # reading data from csv file into dataframe
                    df = pd.read_csv(f'{DIR_TEMP_DATA}/{table_name}.csv')

                    # load data into target database
                    df.to_sql(table_name, 
                              dwh_engine, 
                              if_exists='append', 
                              index=False,
                              schema='pactravel')
                    
                    logging.info(f"Data loaded successfully into table {table_name}.")

                logging.info('----------Data loading to pactravel schema completed successfully----------')

            except Exception as e:
                logging.error(f"Error loading data into pactravel schema: {e}")
                raise Exception(f"Error loading data into pactravel schema: {e}")

            # record execution time and write to summary csv      
            end_time = time.time()
            execution_time = end_time - start_time
            logging.info(f"Data loading process completed in {execution_time:.2f} seconds.")

            summary_data = {
                'timestamp': [datetime.now()],
                'task': ['LoadData'],
                'status': ['Success'],
                'execution_time': [execution_time]
            }

            summary = pd.DataFrame(summary_data)

            summary.to_csv(f'{DIR_TEMP_DATA}/load_summary.csv', index=False)

        except Exception as e:

            summary_data = {
                'timestamp': [datetime.now()],
                'task': ['LoadData'],
                'status': ['Failed'],
                'execution_time': [0]
            }
            summary = pd.DataFrame(summary_data)

            summary.to_csv(f'{DIR_TEMP_DATA}/load_summary.csv', index=False)

            logging.error(f"Error in LoadData task")
            raise Exception(f"Error in LoadData task: {e}")


    def output(self):
        return [luigi.LocalTarget(f'{DIR_TEMP_LOG}/logs.log'),
                luigi.LocalTarget(f'{DIR_TEMP_DATA}/load_summary.csv')]