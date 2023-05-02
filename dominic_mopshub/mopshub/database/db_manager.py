import sqlite3
import time
from datetime import datetime

class DBManager:
    """description of class"""

    def __init__(self, directory=None, filename=None):

        self.file = filename
        self.dir = directory

        try:
            self.db_connection = sqlite3.connect('database/mopshub_readout.db')
            self.cursor = self.db_connection.cursor()
            print("Connected to DB")
        except Error as e:
            print(e)

        try:
            self.cursor.execute("DROP TABLE mops_readout")
            print("table dropped")
        except Exception as e:
            print(e)

    def create_table(self):
        readout_table = """CREATE TABLE IF NOT EXISTS mops_readout (
                                    readout_time time,
                                    cic_id integer,
                                    bus_id integer NOT NULL,
                                    mops_id integer NOT NULL,
                                    adc_channel integer,
                                    adc_value integer,
                                    adc_desc TEXT
                                );"""
        try:
            self.cursor.execute(readout_table)
        except Error as e:
            print(e)

    def write_to_db(self, readout_time, cic_id, bus_id, mops_id, adc_channel, adc_value, adc_desc):
        sqlite_insert_query = """INSERT INTO mops_readout
                                  (readout_time, cic_id, bus_id, mops_id, adc_channel, adc_value, adc_desc) 
                                   VALUES 
                                  (?, ?, ?, ?, ?, ?, ?)"""
        data = (readout_time, cic_id, bus_id, mops_id, adc_channel, adc_value, adc_desc)
        try:
            self.cursor.execute(sqlite_insert_query, data)
            self.db_connection.commit()
        except Exception as e:
            print(e)
