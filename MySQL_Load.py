import csv
import mysql.connector

def create_table(cursor, table_name, columns):
    # Generate the CREATE TABLE statement
    create_table_stmt = f"CREATE TABLE {table_name} ({', '.join(columns)})"

    # Execute the CREATE TABLE statement
    cursor.execute(create_table_stmt)

def load_data(cursor, table_name, data):
    # Generate the INSERT INTO statement
    placeholders = ', '.join(['%s'] * len(data[0]))
    insert_stmt = f"INSERT INTO {table_name} VALUES ({placeholders})"

    # Execute the INSERT INTO statement for each row of data
    cursor.executemany(insert_stmt, data)

def define_database(csv_file):
    # Extract information from the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        table_name = next(reader)[0]
        columns = []
        data = []

        for row in reader:
            column_name = row[0]
            column_type = row[1]
            column_length = row[2]
            column_key = row[3]

            column_def = f"{column_name} {column_type}({column_length})"

            if column_key == 'PRIMARY KEY':
                column_def += " PRIMARY KEY"

            if column_key == 'FOREIGN':
                foreign_table = row[4]
                foreign_key = row[5]
                column_def += f", FOREIGN KEY ({column_name}) REFERENCES {foreign_table}({foreign_key})"

            columns.append(column_def)
            data.append(row[6:])

    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Evenodd!512',
        database='takestock'
    )
    cursor = conn.cursor()

    # Create the table
    create_table(cursor, table_name, columns)

    # Load the data into the table
    load_data(cursor, table_name, data)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Usage example
define_database('load.csv')
