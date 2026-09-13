from ts_database import *
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from datetime import datetime, date
from wtforms import Form
from app_factory import create_app, mysql
from flask_mysqldb import MySQL
import re
import random
import decimal

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


class StockMgr:
    def __init__(self):
        self.table_name = "stocks"
        self.column_names = []
        self.stock_data = {
            'stock_count': 100,
            'stock_value': decimal.Decimal('0.00'),
            'stock_description': " ",
            'stock_cost': decimal.Decimal('0.00')
            }

    def set_position(self, row1: int, row2: int):
        rng = random.Random()
        position = rng.randint(row1, row2)
        return position

    def get_stock_row(self, row: int):
        status, result, column_names = db.get_table_row(self.table_name, row)
        if status == "NOK":
            raise RuntimeError(f"TakeStock {self.table_name} table read failure or key not found.")
        self.column_names = column_names
        return result[0]  # unwrap here, once

    def build_stock_array(self, stock_row, player_number):
        stock_array = []

        for column, value in stock_row.items():
            if column != "id":
                amt = decimal.Decimal(value)
                entry = self.stock_data.copy()  # start with all current fields
                entry['stock_value'] = amt
                entry['stock_cost'] = amt * 100
                entry['stock_description'] = column
                stock_array.append(entry)

        return stock_array

    def store_investment(self, stock_data, req_id, player_number):
        stat = "NOK"
        ndx = int(req_id) - 1
        new_value = decimal.Decimal(stock_data[ndx]['stock_cost']) * decimal.Decimal('1.10')
        invest_data = {
            'invest_type': "STCK",
            'invest_count': stock_data[ndx]['stock_count'],
            'invest_amount': decimal.Decimal(stock_data[ndx]['stock_cost']),
            'invest_description': stock_data[ndx]['stock_description'],
            'player_number': player_number,
            'invest_value': decimal.Decimal(new_value)
        }

        stat = db.insert_investments_from_sale(invest_data)
        return stat

