from flask import Flask, render_template
from flask import request
import mysql.connector

app = Flask(__name__)

data1 = [ {"code": "SC2", "id": 1, "type": "exp", "short_description": "On Sale", "long_description": "Bedroom set various colors and styles", "INVITES": "Audreys Furniture", "amount": -3500, "count": 5},
{"code": "SC2", "id": 2, "type": "exp", "short_description": "On Sale", "long_description": "Armoirs cabinet of various colors and styles", "INVITES": "Audreys Furniture", "amount": -1000, "count": 1},
{"code": "SC2", "id": 3, "type": "exp", "short_description": "On Sale", "long_description": "Cloth or Leather chairs of various colors and styles", "INVITES": "Audreys Furniture", "amount": -500, "count": 1},
{"code": "SC2", "id": 4, "type": "exp", "short_description": "On Sale", "long_description": "Cloth or leather sofas with end tables", "INVITES": "Audreys Furniture", "amount": -950, "count": 3},
{"code": "SC2", "id": 5, "type": "exp", "short_description": "On Sale", "long_description": "Pendulum clocks of various designs", "INVITES": "Audreys Furniture", "amount": -800, "count": 1},
{"code": "SC2", "id": 6, "type": "exp", "short_description": "On Sale", "long_description": "Office space desks in different styles", "INVITES": "Audreys Furniture", "amount": -700, "count": 2},
{"code": "SC2", "id": 7, "type": "exp", "short_description": "On Sale", "long_description": "Kitchen or Dining room tables of various colors and styles", "INVITES": "Audreys Furniture", "amount": -900, "count": 5}
]

def get_data(data1):
    data = []
    for row in data1:
        x = row['short_description'] + ": " + str(row['count']) + "-piece deal"
        row['short_description'] = x
        x = abs(row['amount'])
        row['amount'] = str(x)
        data.append(row)
    return data

@app.route('/')
def display():
    data = get_data(data1)
    return render_template('display.html', data=data)

@app.route('/process_selection', methods=['POST'])
def process_selection():
    selected_items = request.form.getlist('selected_items')
    # Process the selected items
    print(selected_items)
    return "Items processed: " + ", ".join(selected_items)


if __name__ == '__main__':
    app.run(debug=True)
