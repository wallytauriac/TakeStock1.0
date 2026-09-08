from ts_database import *
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from datetime import datetime, date
from wtforms import Form
from app_factory import create_app, mysql
from flask_mysqldb import MySQL
import re
import random

class IndexMgr:
    def __init__(self, tablelist):
        self.index_table = {}

        for table in tablelist:
            self.table_name = table
            self.data = self.load_data()

            self.index_table[table] = {
                "low": self.data["low"],
                "high": self.data["high"],
                "current": self.data["current"],
            }

        print(f"Loaded Index Table data: {self.index_table}")

    def load_data(self):
        """
        Loads a row of data from the MySQL table into memory.
        Returns: dict: The table data loaded into memory.
        """
        q, result = db.get_positions_data(self.table_name)
        if q > 0:
            tbl_length = int(q)
            if tbl_length > 1:
                rng = random.Random()
                data = {}
                data["low"] = int(1)
                data["high"] = tbl_length
                data["current"] = rng.randint(data["low"], data["high"])
            else:
                raise Exception(f"Error Condition: Table {self.table_name} has only one row...")
        else:
            raise Exception(f"Error Condition: Table {self.table_name} has no data rows...")




        return data

    def get_table_pointer(self, table_name):
        return self.index_table[table_name]["current"]

    def reset_table_pointer(self, table_name):
        status = "NOK"
        rng = random.Random()
        low_nbr = self.index_table[table_name]["low"]
        high_nbr = self.index_table[table_name]["high"]
        nbr = int(rng.randint(low_nbr, high_nbr))
        self.index_table[table_name]["current"] = nbr
        status = "OK"
        return status


db = DB_Mgr(mysql)
tablelist = ["commodities", "address", "business", "lifecenter",
            "stockcenter", "shopping", "jobcenter", "learncenter",
            "bankercycle", "opportunities"]

_im_instance = None

def get_im():
    global _im_instance
    if _im_instance is None:
        _im_instance = IndexMgr(tablelist)   # only runs on first real call, not at import
    return _im_instance