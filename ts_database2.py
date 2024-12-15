import random
from random import randint, choice

from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt

from flask_mysqldb import MySQL
from ts_validation import ChangePasswordForm, AddMemberForm, EditForm, GameForm, GameLevelForm
import mysql
import mysql.connector
import random
from typing import Dict, Any, Optional, Tuple, Set
from mysql.connector import Error

db_config = {
    'user': 'root',
    'password': 'Evenodd!512',
    'host': 'localhost',
    'database': 'Takestock1.0'
}


class DB_Mgr:
    def __init__(self, obj):
        self.mysql = obj

    def _execute_query(self, query, params):
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query, params)
            result = cur.fetchall()
            status = "OK"
            column_names = [desc[0] for desc in cur.description]
        except Exception as e:
            print(f"Database query error: {e}")
            result = {}
            status = "NOK"
        cur.close()
        return status, result, column_names

    def get_table_row(self, table_name, pos):

        # cnx = mysql.connector.connect(**db_config)
        # cur = cnx.cursor()
        query = f'SELECT * FROM {table_name} WHERE id = %s'
        return self._execute_query(query, [pos])

