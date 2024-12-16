import oracledb


class OracleDatabase:
    def __init__(self, user, password, dsn):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish a connection to the Oracle database."""
        try:
            self.connection = oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)
            self.cursor = self.connection.cursor()
            print("Successfully connected to Oracle Database")
        except oracledb.DatabaseError as e:
            print(f"Database connection error: {e}")

    def close(self):
        """Close the connection to the Oracle database."""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Connection closed.")

    def get_table_names(self):
        """Retrieve all table names available to the user."""
        try:
            query = "SELECT table_name FROM user_tables"
            self.cursor.execute(query)
            return [row[0] for row in self.cursor.fetchall()]
        except oracledb.DatabaseError as e:
            print(f"Error retrieving table names: {e}")
            return []

    def get_table_attributes(self, table_name):
        """
        Retrieve the column names and data types of a given table.
        :param table_name: Name of the table.
        :return: List of column names.
        """
        try:
            query = "SELECT column_name FROM user_tab_columns WHERE table_name = :table_name"
            self.cursor.execute(query, [table_name.upper()])
            return [row[0] for row in self.cursor.fetchall()]
        except oracledb.DatabaseError as e:
            print(f"Error retrieving attributes for table {table_name}: {e}")
            return []

    def get_table_data(self, table_name, filters=None, sort_column=None, sort_order="ASC"):
        """
        Retrieve table data with optional filtering and sorting.
        :param table_name: Name of the table.
        :param filters: Dictionary of column-value pairs for filtering.
        :param sort_column: Column to sort by.
        :param sort_order: Sort order ('ASC' or 'DESC').
        :return: Tuple of rows and column names.
        """
        try:
            query = f"SELECT * FROM {table_name}"
            parameters = {}
            filter_clauses = []

            # Add filtering conditions
            if filters:
                for column, value in filters.items():
                    if value:  # Only add filters with non-empty values
                        filter_clauses.append(f"UPPER({column}) LIKE UPPER(:{column})")
                        parameters[column] = f"%{value}%"

            if filter_clauses:
                query += " WHERE " + " AND ".join(filter_clauses)

            # Add sorting
            if sort_column:
                query += f" ORDER BY {sort_column} {sort_order}"

            self.cursor.execute(query, parameters)
            rows = self.cursor.fetchall()
            columns = [col[0] for col in self.cursor.description]
            return rows, columns
        except oracledb.DatabaseError as e:
            print(f"Error retrieving data from table {table_name}: {e}")
            return [], []

    def add_entry(self, table_name, data):
        """
        Add a new entry to a table.
        :param table_name: Name of the table.
        :param data: Dictionary of column-value pairs to insert.
        :return: None
        """
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join([f":{key}" for key in data.keys()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, data)
            self.connection.commit()
            print(f"Successfully added entry to table {table_name}.")
        except oracledb.DatabaseError as e:
            print(f"Error adding entry to table {table_name}: {e}")

    def edit_entry(self, table_name, entry_id, updates):
        """
        Edit an existing entry in a table.
        :param table_name: Name of the table.
        :param entry_id: ID of the entry to update.
        :param updates: Dictionary of column-value pairs to update.
        :return: None
        """
        try:
            set_clause = ", ".join([f"{column} = :{column}" for column in updates.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE ID = :entry_id"
            updates["entry_id"] = entry_id
            self.cursor.execute(query, updates)
            self.connection.commit()
            print(f"Successfully updated entry in table {table_name}.")
        except oracledb.DatabaseError as e:
            print(f"Error editing entry in table {table_name}: {e}")

    def remove_entry(self, table_name, entry_id):
        """
        Remove an entry from a table.
        :param table_name: Name of the table.
        :param entry_id: ID of the entry to remove.
        :return: None
        """
        try:
            query = f"DELETE FROM {table_name} WHERE ID = :entry_id"
            self.cursor.execute(query, {"entry_id": entry_id})
            self.connection.commit()
            print(f"Successfully removed entry from table {table_name}.")
        except oracledb.DatabaseError as e:
            print(f"Error removing entry from table {table_name}: {e}")
