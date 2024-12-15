from flask import Flask, render_template
import pandas as pd
from icecream import ic

app = Flask(__name__)

@app.route('/')
def home():
    # Updated sample data to ensure each list has the same length
    features = ["Features Legend:", "1) RP = Request Play", "2) TP = Triple Play", "3) IV = Invites",
                "4) SP = Single Play", "5) RN = Random Play"]
    goals = ["", "Active Game Level & Goal: Easy Play | Achieve Monetary Amount",
             "GOAL SPECIFIC:  $100,000,000 cash on hand", "Features Disabled: RP:TP", "", ""]
    player_status0 = ["", "Player Status", "Player", "% of Goal", "1", "85", "2", "25", "n", "77"]
    player_status1 = ["Player", "1", "2", "n", "", ""]
    player_status2 = ["% of Goal", "85", "25", "77", "", ""]
    player_status3 = ["-STOCK COUNT-", " ", " ", " ", "", ""]
    player_status4 = ["OnG", "15", "25", "0", "", ""]

    data = {
        "Features": features,
        "Goals": goals,
        "Player Status1": player_status1,
        "Player Status2": player_status2
    }
    ic(data['Features'], data['Goals'], data['Player Status1'], data['Player Status2'])
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Clean the lists
    player_status1 = remove_trailing_empty(player_status1)
    player_status2 = remove_trailing_empty(player_status2)
    player_status3 = remove_trailing_empty(player_status3)
    player_status4 = remove_trailing_empty(player_status4)

    # Create dictionary
    player_status = {
        player_status1[0]: player_status1[1:],
        player_status2[0]: [int(x) if x.isdigit() else x for x in player_status2[1:]],
        player_status3[0]: [int(x) if x.isdigit() else x for x in player_status3[1:]],
        player_status4[0]: [int(x) if x.isdigit() else x for x in player_status4[1:]]
    }
    ic(player_status)
    # Convert Player Status to a transposed DataFrame for better display
    player_status_df = pd.DataFrame(player_status)

    ic(player_status_df, df)
    return render_template('report.html', data=df, player_status=player_status_df)

# Function to remove trailing empty elements
def remove_trailing_empty(lst):
    return [x for x in lst if x]

if __name__ == '__main__':
    app.run(debug=True)
