import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-TI9LKAR;"  # ← aici pui serverul tau
    "DATABASE=FactoryQualityDB;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM Identifiers")

rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()