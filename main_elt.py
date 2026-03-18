import luigi
import sentry_sdk
import logging
import os
import pandas as pd
from pipeline.extract import ExtractData
from pipeline.transform import TransformData
from pipeline.load import LoadData
from pipeline.utils.copy_log import copy_log
from pipeline.utils.delete_temp_data import delete_temp
from dotenv import load_dotenv

load_dotenv()

DIR_ROOT_PROJECT = os.getenv("DIR_ROOT_PROJECT")
DIR_TEMP_LOG = os.getenv("DIR_TEMP_LOG")
DIR_TEMP_DATA = os.getenv("DIR_TEMP_DATA")
DIR_LOG = os.getenv("DIR_LOG")
SENTRY_DSN = os.getenv("SENTRY_DSN")

sentry_sdk.init(dsn = f"{SENTRY_DSN}")

if __name__ == "__main__":
    luigi.build([
        ExtractData(),
        LoadData(),
        TransformData()
    ])

    copy_log(source_file=f'{DIR_TEMP_LOG}/logs.log', destination_file=f'{DIR_LOG}/logs.log')

    delete_temp(directory=f'{DIR_TEMP_DATA}')
    delete_temp(directory=f'{DIR_TEMP_LOG}')