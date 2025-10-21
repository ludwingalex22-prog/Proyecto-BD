import pyodbc

try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=sqldatabbase.database.windows.net,1433;'
        'DATABASE=ProyectoBD;'
        'UID=sqladmin;'
        'PWD=ProyectoBD2025;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;',
        timeout=10
    )
    print("✅ Conexión exitosa a Azure SQL Server.")
except Exception as e:
    print("❌ Error al conectar:", e)