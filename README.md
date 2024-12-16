# **Database Viewer and Manager**

A PyQt5-based desktop application to view, manage, and visualize data in an Oracle database. This tool allows users to interact with their database through an intuitive graphical user interface (GUI), perform CRUD operations, and generate visual representations of their data.

---

## **Features**

### 1. **Table Management**
- **View Tables**: Dynamically load and display tables from the connected Oracle database.
- **Filter Entries**: Apply dynamic filters to table entries in real-time.
- **Sort Entries**: Sort table entries by clicking column headers.

### 2. **CRUD Operations**
- **Add Entries**: Add new entries to any table using a popup form with dynamically generated fields.
- **Edit Entries**: Modify an existing entry by selecting it in the table and using a popup form pre-filled with the current values.
- **Delete Entries**: Delete a selected entry directly from the table.

### 3. **Data Visualization**
- **Graphing Capabilities**: Create various types of graphs (Bar Chart, Pie Chart, Line Chart) using data from the database.
- **Dynamic Selection**:
  - Choose the type of graph.
  - Select the columns for the X-axis and Y-axis.

---

## **Prerequisites**

1. **Python 3.7+**
2. **Oracle Database**
   - Ensure you have access to an Oracle database instance.
3. **Dependencies**:
   Install the required Python libraries:
   ```bash
   pip install PyQt5 matplotlib oracledb
    ```
   
## **Setup**

1. **Clone the Repository**:

2. **Set Up Oracle Database**:
   - Create a new user and grant necessary privileges.
   - Update the connection details in `main.py`:
```python
user = "your_username"
password = "your_password"
dsn = "your_dsn"  # e.g., "hostname:port/service_name"
```
3. **Run the Application**:
   ```bash
   python main.py
   ```


