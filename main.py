from UserInterface import *

if __name__ == "__main__":
    # Database connection details
    user = "system"
    password = "1234"
    dsn = "localhost:1521/xe"  # e.g., "hostname:port/service_name"

    db = OracleDatabase(user, password, dsn)
    db.connect()

    app = QApplication(sys.argv)
    viewer = DatabaseViewer(db)
    viewer.show()
    app.exec_()

    db.close()