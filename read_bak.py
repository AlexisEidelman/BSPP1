# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 12:50:58 2016

@author: sgmap
"""

# imports
import pyodbc

# define the backup paths
server_backup_path = 'c:\\mssql_backup\\'
client_backup_path = 'z:\\mssql_backup\\'

# Connection object (notice that i dont include the database name)
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=SERVER\\DATAINSTANCE;Trusted_Connection=yes', autocommit=True)

# List databases function
def list_databases(conn_obj):
  dbs = []
  cur = conn_obj.cursor()
  result = cur.execute('SELECT name from sysdatabases').fetchall()
  cur.close()
  for db in result:
    dbs.append(db[0])
  return dbs

# backup database function, please notice that the function gets 2 paths, one from the server's point of view
# and one from the clients point of view aka network drive
def backup_db(conn_obj, db_name, server_backup_path, client_backup_path):
  try:
    # you need to remove the previous file because it just appends the information every time you run the
    # backup function, i am using try/except because the first time the file doesnt exist.
    os.remove(client_backup_path + db_name + r'_sql.bak')
  except:
    print db_name + ' doesnt exist yet...'
  cur = conn_obj.cursor()
  try:
    # here i am using try/except because some system databases cant be backed up such as tempdb or 
    # a database might be problematic for any reason, perhaps an exclude mechanism is better, its
    # up to you.
    cur.execute('BACKUP DATABASE ? TO DISK=?', [db_name, server_backup_path + db_name + r'_sql.bak'])
    while cur.nextset(): 
      pass
    cur.close()
  except:
    print 'cant backup: ' + db_name

# take the list
dbs = list_databases(conn)

# take backup for each database
for db in dbs:
  backup_db(conn, db, server_backup_path, client_backup_path)

# close the connection