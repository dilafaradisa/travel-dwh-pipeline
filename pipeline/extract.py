import luigi
from datetime import datetime
import logging
import time
import pandas as pd
from pipeline.utils.db_connect import src_db_connection
import os
from dotenv import load_dotenv

load_dotenv()

DIR_ROOT_PROJECT = os.getenv("DIR_ROOT_PROJECT", default=os.getcwd())
DIR_TEMP_LOG = os.getenv("DIR_TEMP_LOG")
DIR_EXTRACT_QUERY = os.getenv("DIR_EXTRACT_QUERY")
DIR_TEMP_DATA = os.getenv("DIR_TEMP_DATA")

class ExtractData(luigi.Task):
    """
    untuk ekstrak data menggunakan SQL Query lalu menyimpan hasil ekstrak sementara dalam bentuk file CSV.
    """

    tables = ['public.aircrafts',
              'public.airlines',
              'public.airports',
              'public.customers',
              'public.hotel',
              'public.flight_bookings',
              'public.hotel_bookings']
    

    def requires(self):
        pass

    def run(self):
        try:
            # Set up logging
            logging.basicConfig(level = logging.INFO,
                                filename=f'{DIR_TEMP_LOG}/logs.log',
                                format='%(asctime)s - %(levelname)s - %(message)s')
            
            '''extract data from source database'''
            # connect db
            src_engine = src_db_connection()
            
            start_time = time.time()

            logging.info("----------Starting data extraction process----------")

            for idx, table in enumerate(self.tables):
                table_name = table.split(".")[1]
                try:
                    logging.info(f'starting to extract data from table {table_name}.')
                    # reading data into dataframe
                    df = pd.read_sql(f'SELECT * FROM {table}', src_engine)

                    # save data as csv file
                    df.to_csv(f'{DIR_TEMP_DATA}/{table_name}.csv', index=False)

                    logging.info(f"Data extracted successfully from table {table_name}.")

                except Exception as e:
                    logging.error(f"Error extracting data from table {table_name}: {e}")
                    continue
            
            end_time = time.time()
            execution_time = end_time - start_time
            logging.info(f"Data extraction process completed in {execution_time:.2f} seconds.")

            # get summary
            summary_data = {
                'timestamp': [datetime.now()],
                'task': ['ExtractData'],
                'status': ['Success'],
                'execution_time': [execution_time]
            }

            # get summary data into dataframe
            summary = pd.DataFrame(summary_data)

            # save summary data as csv file
            summary.to_csv(f'{DIR_TEMP_DATA}/extract_summary.csv', index=False)

        except Exception as e:
            logging.info(f"Data extraction process failed!")

            # get summary data
            summary_data = {
                'timestamp': [datetime.now()],
                'task': ['ExtractData'],
                'status': ['Failed'],
                'execution_time': [0]
            }
            # get summary data into dataframe
            summary = pd.DataFrame(summary_data)
            # save summary data as csv file
            summary.to_csv(f'{DIR_TEMP_DATA}/extract_summary.csv', index=False)

            raise Exception(f"Data extraction process failed: {e}")
        
        logging.info("----------Data extraction process finished----------")

    def output(self):
        outputs = []

        for table in self.tables:
            outputs.append(luigi.LocalTarget(f'{DIR_TEMP_DATA}/{table.split(".")[1]}.csv'))
        
        outputs.append(luigi.LocalTarget(f'{DIR_TEMP_DATA}/extract_summary.csv'))

        return outputs

