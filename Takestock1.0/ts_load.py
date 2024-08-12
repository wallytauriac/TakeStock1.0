import pandas as pd
import mysql.connector
from mysql.connector import errorcode


def populate_mysql_table(csv_file_path, db_config, table_name):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)

        # Get column names from the CSV file
        columns = df.columns.tolist()
        col_num = 4
        # Ensure there are correct number of columns
        if len(columns) != col_num:
            raise ValueError(f"CSV file must have exactly {col_num} columns")

        # Establish the MySQL connection
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        # Create the table with column names from the CSV
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns[0]} int NOT NULL AUTO_INCREMENT,
            {columns[1]} VARCHAR(20),
            {columns[2]} VARCHAR(50),
            {columns[3]} VARCHAR(100),
            PRIMARY KEY (`id`)
        )
        """
        cursor.execute(create_table_query)

        # Insert data into the table
        insert_query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES (%s, %s, %s, %s)
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
table_name = 'address'
populate_mysql_table('address.csv', db_config, table_name)

if __name__ == "__main__":
    print("Bye")