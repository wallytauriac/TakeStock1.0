@echo off
set FLASK_DEBUG=True
set FLASK_APP=ts_main.py
set DEBUG=True
set SECRET_KEY=528491@JOKER
flask run || (
    echo "Failed to start Flask. Check if main.py is in the correct directory."
)
