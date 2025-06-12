import pandas as pd 
import mysql.connector


#Abrir y leer el archivo con la información
print("Extrayendo la información del archivo de datos")
df_financial_transactions = pd.read_csv('financial_transactions.csv')
#Se ajustan los tipos de datos: la columna date a formato fecha (yyyy-mm-dd), type y description a cadena
print('Ajustando los tipos de datos antes de introducir a la base de datos')
df_financial_transactions['date'] = pd.to_datetime(df_financial_transactions['date'])
#Se normaliza la fecha para que sea formato de año, mes y día 
df_financial_transactions['date'] = df_financial_transactions['date'].dt.normalize()
df_financial_transactions['type'] = df_financial_transactions['type'].astype("string")
df_financial_transactions['description'] = df_financial_transactions['description'].astype("string")

#Eliminar registros del 2018
print('Eliminando registros del 2018')
df_financial_transactions =df_financial_transactions[df_financial_transactions['date'].dt.year != 2018]

print(df_financial_transactions.dtypes)

#Pasos para conexión, creación e inserción a la base de datos

#1 Conexión a la base de datos
print('Creando conexión a Base de Datos')
conn = mysql.connector.connect(
  
  host="db",
  user="usuarioprueba",
  password="prueba",
  database="BancoBase"
  
)
cur = conn.cursor()

#2 Crear la tabla en caso de no existir

print('Creando tabla....')

cur.execute("""
            CREATE TABLE IF NOT EXISTS financialtransactions (
              
              transaction_id INT PRIMARY KEY, 
              date DATE, 
              customer_id INT, 
              amount FLOAT, 
              type VARCHAR(50), 
              description TEXT
            );
            
            """)

#3 Insertar los datos actualizados

print('Insertando datos')
for i, (_, row) in enumerate(df_financial_transactions.iterrows(), start=1):
  
  print(f"Insertando fila {i} con transaction_id {row['transaction_id']}")
  cur.execute("""
              INSERT INTO financialtransactions (transaction_id, date, customer_id, amount, type, description)
              VALUES (%s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE
                date = VALUES(date),
                customer_id = VALUES(customer_id),
                amount = VALUES(amount),
                type = VALUES(type),
                description = VALUES(description) 
              """, (
                int(row['transaction_id']), 
                row['date'].date(),
                int(row['customer_id']),
                float(row['amount']), 
                row['type'],
                row['description']
              ))
  
#4 Confirmar e insertar los datos en la tabla
conn.commit()
cur.close()
conn.close()
print("Datos insertados correctamente")