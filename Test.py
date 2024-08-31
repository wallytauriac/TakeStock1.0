from ts_database import *
from ts_game import *
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from datetime import datetime, date
from wtforms import Form
from flask_mysqldb import MySQL

from functools import wraps
import re


mysql = MySQL()
#test_bp = Blueprint('test_bp', __name__, template_folder="templates")
db = DB_Mgr(mysql)

status, investments = db.get_player_investment_history(1)
if status == "OK":
    for item in investments:
        print(item)
    # type = ['PPTY', 'STCK', 'BUS', 'OTHR']
    # desc = ['Personal House', 'Airline   (Count=100)', 'Partnership (Wally Mart)', 'Diamond Necklace']
    # inv = ['$  100,000',
    #        '$    1,000',
    #        '$   50,000',
    #        '$    2,000'
    #        ]
    # val = ['$  110,000',
    #        '$    2,000',
    #        '$   70,000',
    #        '$    5,000'
    #        ]

else:
    flash("DB error. Players table read error.", "error")

if __name__ == "__main__":
    print('bye')