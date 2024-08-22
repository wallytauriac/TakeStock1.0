import pandas as pd
import os
import mysql.connector
from mysql.connector import errorcode


def populate_mysql_table(csv_file_path, db_config, table_name):

    try:

        file_path = load_file

        if os.path.exists(file_path):
            print(f"File {load_file} exists.")
        else:
            print(f"File {load_file} does not exist.")
            exit(1)
    except:
        exit(1)

    try:
        # Read the CSV file
        if table_name == "address":
            df = pd.read_csv(csv_file_path, dtype={'Address': str})
        elif table_name == "opportunities":
            df = pd.read_csv(csv_file_path, dtype={'INVITES': str})
        else:
            df = pd.read_csv(csv_file_path)

        # Get the number of columns
        col_num = df.shape[1]

        # Get column names from the CSV file
        columns = df.columns.tolist()
        # Ensure there are correct number of columns
        if len(columns) != col_num:
            raise ValueError(f"CSV file must have exactly {col_num} columns")

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

        # Create the table with column names from the CSV
        if table_name == "address":
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {columns[0]} int NOT NULL AUTO_INCREMENT,
                {columns[1]} varchar(20) DEFAULT NULL,
                {columns[2]} varchar(50) DEFAULT NULL,
                {columns[3]} varchar(100) DEFAULT NULL,
                {columns[4]} varchar(50) DEFAULT NULL,
                {columns[5]} varchar(50) DEFAULT NULL,
                {columns[6]} decimal(14,2) DEFAULT 0,
                {columns[7]}  decimal(14,2) DEFAULT 0,
                PRIMARY KEY (`id`)
            )
            """
        elif table_name == "business":
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                `id` int NOT NULL AUTO_INCREMENT,
                  `Street` varchar(20) DEFAULT NULL,
                  `business` varchar(100) DEFAULT NULL,
                  `buy` decimal(10,0) DEFAULT 0,
                  `partner` decimal(10,0) DEFAULT 0,
                  `club` decimal(12,0) DEFAULT 0,
                  `value` decimal(14,0) DEFAULT 0,
                  PRIMARY KEY (`id`)
            )
            """
        elif table_name == "commodities":
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `Mutual` decimal(10,0) DEFAULT NULL,
                  `Diamonds` decimal(10,0) DEFAULT NULL,
                  `Grain` decimal(10,0) DEFAULT NULL,
                  `Security` decimal(10,0) DEFAULT NULL,
                  `Silver` decimal(10,0) DEFAULT NULL,
                  `Certificates` decimal(10,3) DEFAULT 0,
                  `Money` decimal(10,3) DEFAULT 0,
                  PRIMARY KEY (`id`)
            )
            """
        elif table_name == "opportunities":
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                    `code` char(5) DEFAULT "{code}",
                    `id` int NOT NULL AUTO_INCREMENT,
                    `type` varchar(10) DEFAULT NULL,
                    `OWN_code` char(5) DEFAULT " ",
                    `short_description` varchar(100) DEFAULT NULL,
                    `long_description` varchar(500) DEFAULT NULL,
                    `INVITES`  varchar(30) DEFAULT " ",
                    `amount` decimal(12,0) DEFAULT 0,
                    `count` decimal(10,0) DEFAULT 0,
                    PRIMARY KEY (`id`)
            )
            """
        elif table_name == "stockcenter":
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                    `code` char(5) DEFAULT "{code}",
                    `id` int NOT NULL AUTO_INCREMENT,
                    `type` varchar(10) DEFAULT NULL,
                    `short_description` varchar(100) DEFAULT NULL,
                    `long_description` varchar(500) DEFAULT NULL,
                    `count` decimal(10,0) DEFAULT 0,
                    `amount` decimal(10,0) DEFAULT NULL,
                    PRIMARY KEY (`id`)
            )
            """
        elif table_name == "shopping":
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                    `code` char(5) DEFAULT "{code}",
                    `id` int NOT NULL AUTO_INCREMENT,
                    `type` varchar(10) DEFAULT NULL,
                    `short_description` varchar(100) DEFAULT NULL,
                    `long_description` varchar(500) DEFAULT NULL,
                    `INVITES` varchar(30) DEFAULT " ",
                    `amount` decimal(14,0) DEFAULT NULL,
                    `count` decimal(14,0) DEFAULT 0,
                    PRIMARY KEY (`id`)
            )
            """
        else:
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                    `code` char(5) DEFAULT "{code}",
                    `id` int NOT NULL AUTO_INCREMENT,
                    `type` varchar(10) DEFAULT NULL,
                    `short_description` varchar(100) DEFAULT NULL,
                    `long_description` varchar(500) DEFAULT NULL,
                    `amount` decimal(10,0) DEFAULT NULL,
                    PRIMARY KEY (`id`)
            )
            """

        cursor.execute(create_table_query)

        # Insert data into the table
        if table_name == "address":
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        elif table_name == "business":
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        elif table_name == "commodities":
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        elif table_name == "opportunities":
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        elif table_name == "stockcenter":
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        elif table_name == "shopping":
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        else:
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES (%s, %s, %s, %s, %s, %s)
            """

        for row in df.itertuples(index=False):
            cursor.execute(insert_query, tuple(row))

        # Commit the transaction
        cnx.commit()
        cursor.close()

        print("Data inserted successfully")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'cnx' in locals():
            cnx.close()


# Example usage
db_config = {
    'user': 'root',
    'password': 'Evenodd!512',
    'host': '127.0.0.1',
    'database': 'takestock1.0'
}
code = "SC2"
table_name = 'shopping'
load_file = 'C:/Users/wally/Documents/Python/Demo/Takestock1.0/files/ts_shopping.csv'
populate_mysql_table(load_file, db_config, table_name)

if __name__ == "__main__":
    print("Bye")