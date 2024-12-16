import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QComboBox, QTableWidget,
    QTableWidgetItem, QWidget, QMessageBox, QScrollArea, QPushButton, QDialog, QFormLayout, QLineEdit, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from OracleDatabase import OracleDatabase  # Import the backend class


import matplotlib.pyplot as plt

class GraphDialog(QDialog):
    """Popup dialog for selecting graph options and displaying graphs."""
    def __init__(self, db, table_name, columns):
        super().__init__()
        self.db = db
        self.table_name = table_name
        self.columns = columns
        self.setWindowTitle("Create Graph")
        self.setGeometry(300, 300, 400, 300)

        # Layout for graph options
        self.layout = QFormLayout()

        # Graph type selection
        self.graph_type = QComboBox()
        self.graph_type.addItems(["Bar Chart", "Pie Chart", "Line Chart"])
        self.layout.addRow("Graph Type:", self.graph_type)

        # X-axis column selection
        self.x_axis_column = QComboBox()
        self.x_axis_column.addItems(columns)
        self.layout.addRow("X-Axis:", self.x_axis_column)

        # Y-axis column selection (optional for pie chart)
        self.y_axis_column = QComboBox()
        self.y_axis_column.addItems(columns)
        self.layout.addRow("Y-Axis:", self.y_axis_column)

        # Create Graph button
        self.create_button = QPushButton("Create Graph")
        self.create_button.clicked.connect(self.create_graph)
        self.layout.addRow(self.create_button)

        self.setLayout(self.layout)

    def create_graph(self):
        """Fetch data and generate the selected graph."""
        graph_type = self.graph_type.currentText()
        x_column = self.x_axis_column.currentText()
        y_column = self.y_axis_column.currentText()

        try:
            # Fetch table data
            rows, columns = self.db.get_table_data(self.table_name)
            x_index = columns.index(x_column)
            y_index = columns.index(y_column)

            x_data = [row[x_index] for row in rows]
            y_data = [row[y_index] for row in rows]

            # Generate the graph
            plt.figure(figsize=(10, 6))
            if graph_type == "Bar Chart":
                plt.bar(x_data, y_data)
                plt.xlabel(x_column)
                plt.ylabel(y_column)
                plt.title(f"{y_column} vs {x_column}")
            elif graph_type == "Pie Chart":
                plt.pie(y_data, labels=x_data, autopct='%1.1f%%')
                plt.title(f"{y_column} Distribution")
            elif graph_type == "Line Chart":
                plt.plot(x_data, y_data, marker='o')
                plt.xlabel(x_column)
                plt.ylabel(y_column)
                plt.title(f"{y_column} vs {x_column}")

            plt.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate graph: {e}")


class EditEntryDialog(QDialog):
    """Popup dialog for editing an entry."""
    def __init__(self, db, table_name, columns, entry_id, current_values):
        super().__init__()
        self.db = db
        self.table_name = table_name
        self.columns = columns
        self.entry_id = entry_id
        self.setWindowTitle("Edit Entry")
        self.setGeometry(300, 300, 400, 400)

        # Layout for form inputs
        self.layout = QFormLayout()
        self.inputs = {}

        # Create input fields, pre-filled with current values
        for column, value in zip(columns, current_values):
            line_edit = QLineEdit(str(value))  # Pre-fill with current value
            self.inputs[column] = line_edit
            self.layout.addRow(column, line_edit)

        # Add save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addRow(self.save_button)

        self.setLayout(self.layout)

    def save_changes(self):
        """Collect data and save the changes."""
        updates = {column: self.inputs[column].text() for column in self.columns}
        try:
            self.db.edit_entry(self.table_name, self.entry_id, updates)
            QMessageBox.information(self, "Success", "Entry updated successfully!")
            self.accept()  # Close the dialog
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not update entry: {e}")


class AddEntryDialog(QDialog):
    """Popup dialog for adding a new entry."""
    def __init__(self, db, table_name, columns):
        super().__init__()
        self.db = db
        self.table_name = table_name
        self.columns = columns
        self.setWindowTitle("Add New Entry")
        self.setGeometry(300, 300, 400, 400)

        # Layout for form inputs
        self.layout = QFormLayout()
        self.inputs = {}

        for column in columns:
            line_edit = QLineEdit()
            self.inputs[column] = line_edit
            self.layout.addRow(column, line_edit)

        # Add buttons
        self.add_button = QPushButton("Add Entry")
        self.add_button.clicked.connect(self.add_entry)
        self.layout.addRow(self.add_button)

        self.setLayout(self.layout)

    def add_entry(self):
        """Collect data and add the entry."""
        data = {column: self.inputs[column].text() for column in self.columns}
        try:
            self.db.add_entry(self.table_name, data)
            QMessageBox.information(self, "Success", "Entry added successfully!")
            self.accept()  # Close the dialog
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not add entry: {e}")


class DatabaseViewer(QMainWindow):
    def __init__(self, db: OracleDatabase):
        super().__init__()
        self.db = db
        self.db.connect()

        self.setWindowTitle("Oracle Database Viewer")
        self.setGeometry(100, 100, 1000, 800)

        # Central widget and layout
        container = QWidget()
        self.setCentralWidget(container)
        self.main_layout = QVBoxLayout()
        container.setLayout(self.main_layout)

        # Dropdown for table selection
        self.table_selector = QComboBox()
        self.table_selector.setFont(QFont("Arial", 12))
        self.main_layout.addWidget(self.table_selector)
        self.table_selector.currentIndexChanged.connect(self.setup_table_and_filters)

        # Scroll area for filters
        self.filters_container = QScrollArea()
        self.filters_container_widget = QWidget()
        self.filters_layout = QVBoxLayout()
        self.filters_container_widget.setLayout(self.filters_layout)
        self.filters_container.setWidget(self.filters_container_widget)
        self.filters_container.setWidgetResizable(True)
        self.main_layout.addWidget(self.filters_container)

        # Table widget to display data
        self.table_widget = QTableWidget()
        self.table_widget.setSortingEnabled(True)  # Enable sorting by clicking headers
        self.main_layout.addWidget(self.table_widget)

        # Add, Edit, and Delete Buttons
        self.add_button = QPushButton("Add Entry")
        self.add_button.clicked.connect(self.open_add_entry_dialog)
        self.main_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Selected Entry")
        self.edit_button.clicked.connect(self.open_edit_entry_dialog)
        self.main_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Selected Entry")
        self.delete_button.clicked.connect(self.delete_selected_entry)
        self.main_layout.addWidget(self.delete_button)

        self.graph_button = QPushButton("Create Graph")
        self.graph_button.clicked.connect(self.open_graph_dialog)
        self.main_layout.addWidget(self.graph_button)

        # Apply styling
        self.apply_styles()

        # Load initial table list
        self.refresh_table_list()

    def apply_styles(self):
        """Applies QSS styles to modernize the UI."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QComboBox, QLineEdit {
                padding: 5px;
                border: 2px solid #0078d7;
                border-radius: 5px;
                font-size: 14px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #0078d7;
                selection-background-color: #0078d7;
                selection-color: #ffffff;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005cbf;
            }
            QHeaderView::section {
                background-color: #0078d7;
                color: white;
                font-size: 14px;
                padding: 5px;
                border: none;
                cursor: pointer;
            }
        """)

    def refresh_table_list(self):
        """Refreshes the list of tables in the dropdown."""
        self.table_selector.clear()
        try:
            tables = self.db.get_table_names()
            self.table_selector.addItems(tables)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not fetch table list: {e}")

    def setup_table_and_filters(self):
        """Set up filters and load table entries when a new table is selected."""
        selected_table = self.table_selector.currentText()
        if not selected_table:
            return

        # Fetch and display table entries
        self.load_table_data(selected_table)

        # Clear and set up filter inputs dynamically based on the table's attributes
        self.setup_filter_inputs(selected_table)

    def setup_filter_inputs(self, table_name):
        """Set up filter inputs dynamically based on the table's attributes."""
        try:
            # Clear existing filters
            while self.filters_layout.count():
                widget = self.filters_layout.takeAt(0).widget()
                widget.deleteLater()

            # Fetch table attributes
            columns = self.db.get_table_attributes(table_name)

            # Create input fields for each attribute
            self.filters = {}
            for column in columns:
                label = QLabel(column)
                label.setFont(QFont("Arial", 12))
                line_edit = QLineEdit()
                line_edit.setFont(QFont("Arial", 12))
                line_edit.textChanged.connect(self.apply_filters)
                self.filters[column] = line_edit
                self.filters_layout.addWidget(label)
                self.filters_layout.addWidget(line_edit)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not fetch attributes for table {table_name}: {e}")

    def open_add_entry_dialog(self):
        """Open the add entry popup dialog."""
        selected_table = self.table_selector.currentText()
        if not selected_table:
            QMessageBox.warning(self, "Warning", "No table selected.")
            return

        try:
            columns = self.db.get_table_attributes(selected_table)
            dialog = AddEntryDialog(self.db, selected_table, columns)
            if dialog.exec_():
                self.load_table_data(selected_table)  # Reload table data after adding entry
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open add entry dialog: {e}")

    def open_edit_entry_dialog(self):
        """Open the edit entry popup dialog."""
        selected_table = self.table_selector.currentText()
        if not selected_table:
            QMessageBox.warning(self, "Warning", "No table selected.")
            return

        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "No entry selected.")
            return

        # Get the ID and current values of the selected row
        entry_id = self.table_widget.item(selected_row, 0).text()
        current_values = [self.table_widget.item(selected_row, col).text() for col in
                          range(self.table_widget.columnCount())]

        try:
            # Fetch table attributes
            columns = self.db.get_table_attributes(selected_table)
            # Open the EditEntryDialog
            dialog = EditEntryDialog(self.db, selected_table, columns, entry_id, current_values)
            if dialog.exec_():
                self.load_table_data(selected_table)  # Reload table data after editing entry
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open edit entry dialog: {e}")

    def delete_selected_entry(self):
        """Delete the selected entry from the table."""
        selected_table = self.table_selector.currentText()
        if not selected_table:
            QMessageBox.warning(self, "Warning", "No table selected.")
            return

        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "No entry selected.")
            return

        # Get the ID of the selected row (assuming 'ID' is the first column)
        entry_id = self.table_widget.item(selected_row, 0).text()
        try:
            self.db.remove_entry(selected_table, entry_id)
            QMessageBox.information(self, "Success", "Entry deleted successfully!")
            self.load_table_data(selected_table)  # Reload table data after deleting entry
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete entry: {e}")

    def load_table_data(self, table_name, filters=None, sort_column=None, sort_order="ASC"):
        """Loads the data from the selected table into the table widget."""
        try:
            rows, columns = self.db.get_table_data(table_name, filters, sort_column, sort_order)

            # Populate the table widget
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)
            self.table_widget.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                for col_idx, cell_data in enumerate(row_data):
                    self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))

            # Adjust column widths
            self.table_widget.horizontalHeader().setStretchLastSection(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not fetch data from table {table_name}: {e}")

    def apply_filters(self):
        """Applies filters dynamically as text is entered in the filter boxes."""
        selected_table = self.table_selector.currentText()
        if not selected_table:
            return

        # Collect filters from the input fields
        filters = {}
        for column, input_field in self.filters.items():
            if input_field.text():
                filters[column] = input_field.text()

        # Reload the table data with the filters
        self.load_table_data(selected_table, filters=filters)

    def open_graph_dialog(self):
        """Open the graph selection popup dialog."""
        selected_table = self.table_selector.currentText()
        if not selected_table:
            QMessageBox.warning(self, "Warning", "No table selected.")
            return

        try:
            columns = self.db.get_table_attributes(selected_table)
            dialog = GraphDialog(self.db, selected_table, columns)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open graph dialog: {e}")

