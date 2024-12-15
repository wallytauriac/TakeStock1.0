from icecream import ic
import pandas as pd

player_status = {"Player #": [], "% of Goal": []}
player_status["STOCK COUNTS"] = []
player_status["oNg"] = []
player_status["robotics"] = []
player_status["gold"] = []
player_status["paper"] = []
player_status["utility"] = []
player_status["auto"] = []
player_status["airline"] = []
ic(player_status)

stocks = {"oNg": 1, "robotics": 2, "gold": 3, "paper": 4, "utility": 5, "auto": 6, "airline": 7}

for i, key in enumerate(stocks):
    ic(i, key)
    player_status[key].append(stocks[key])
player_status["Player #"].append(str(1))
player_status["STOCK COUNTS"].append(" ")
player_status["% of Goal"].append("45.0")


ic(player_status)

# Capitalize the keys
capitalized_player_status = {k.upper(): v for k, v in player_status.items()}
ic(capitalized_player_status)
# Create a Pandas DataFrame
df = pd.DataFrame(capitalized_player_status)
ic(df)

if __name__ == '__main__':
    print("Bye")
