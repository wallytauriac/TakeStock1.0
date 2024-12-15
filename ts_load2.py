import pandas as pd
from io import StringIO
import os
import mysql.connector
from mysql.connector import errorcode

# Manually parse each line to respect quotes and commas
def parse_lines(lines):
    parsed_data = []
    for line in lines[1:]:  # Skip header
        if line:
            parts = line.split(',', 1)  # Split only on the first comma
            if len(parts) == 2:
                col_name, value = parts
                col_name = col_name.strip()
                value = value.strip().strip('"')
                parsed_data.append([col_name, value])
            else:
                print(f"Skipping line due to unexpected format: {line}")
    return parsed_data

def populate_mysql_table(csv_file_path, db_config, table_name):
    cnx = None
    cursor = None
    try:

        file_path = csv_file_path

        if os.path.exists(file_path):
            print(f"File {csv_file_path} exists.")
        else:
            print(f"File {csv_file_path} does not exist.")
            exit(1)
    except:
        exit(1)


    # Read the CSV file
    # Read the entire file as a single string
    with open(csv_file_path, 'r') as file:
        data = file.read()

    # Split the data into lines manually
    lines = data.split('\n')

    # Establish the MySQL connection
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # SQL statement to drop a table
    sql = f"""DROP TABLE IF EXISTS {table_name}"""

    try:
        # Executing the SQL statement
        cursor.execute(sql)
        print("Table dropped successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    # Parse the lines
    parsed_data = parse_lines(lines)
    # Define columns for DataFrame
    columns = ['col_name', 'value']

    # Convert parsed data into DataFrame
    df = pd.DataFrame(parsed_data, columns=columns)

    # Add an ID column to group every 7 rows
    df['ID'] = df.index // 7

    # Manually pivot DataFrame
    reshaped_data = {}
    for index, group in df.groupby('ID'):
        row = {col: val for col, val in zip(group['col_name'], group['value'])}
        reshaped_data[index] = row

    reshaped_df = pd.DataFrame.from_dict(reshaped_data, orient='index')

    # Ensure all data is shown
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)

    # Display the reshaped DataFrame
    # print(reshaped_df)

    # Convert the DataFrame to a list of dictionaries
    data_dicts = reshaped_df.to_dict(orient='records')

    # Create the table with column names from the CSV

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        `id` int NOT NULL AUTO_INCREMENT,
        `destination` varchar(500) DEFAULT " ",
        `custom1` varchar(500) DEFAULT " ",
        `trip` varchar(500) DEFAULT " ",
        `sights` varchar(500) DEFAULT " ",
        `events` varchar(500) DEFAULT " ",
        `people` varchar(500) DEFAULT " ",
        `custom2` varchar(500) DEFAULT " ",
        PRIMARY KEY (`id`)
    )
    """
    o_columns = [
        "destination", "trip", "sights", "events", "people", "custom1", "custom2"
    ]
    o_col_num = 8
    cursor.execute(create_table_query)

    # Insert data into the table

    insert_query = f"""
    INSERT INTO {table_name} ({', '.join(o_columns)})
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        for record in data_dicts:
            # Convert each dictionary to a tuple
            data_tuple = tuple(record.values())
            cursor.execute(insert_query, data_tuple)
    except Exception as e:
            print(f"DB Player update request error: {e}")

    # Commit the transaction
    cnx.commit()
    cursor.close()

    print("Data inserted successfully")


# Example usage
db_config = {
    'user': 'root',
    'password': 'Evenodd!512',
    'host': '127.0.0.1',
    'database': 'takestock1.0'
}

table_name = 'travelreport'
load_file = 'C:/Users/wally/Documents/Python/Demo/Takestock1.0/files/ts_travelreport.csv'
populate_mysql_table(load_file, db_config, table_name)

if __name__ == "__main__":
    print("Bye")