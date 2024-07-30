from Constants import connString
import pyodbc
import datetime
import uuid

class DatasetInfoModel:
    def __init__(self, datasetID = 0,datasetNameFile = ''):
        self.datasetID = datasetID
        self.datasetNameFile = datasetNameFile
       
        

    @staticmethod
    def get_all():
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT * FROM DatasetInfo ORDER BY datasetNameFile"
        cursor.execute(sqlcmd1)
        records = []
        for dbrow in cursor.fetchall():
            row = DatasetInfoModel(dbrow[0],dbrow[1])
            records.append(row)
        cursor.close()
        conn.close()
        return records

    @staticmethod
    def get_name_id():
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT datasetID, datasetNameFile FROM DatasetInfo ORDER BY datasetNameFile"
        cursor.execute(sqlcmd1)
        records = []
        for dbrow in cursor.fetchall():
            row = DatasetInfoModel(dbrow[0],dbrow[1])
            records.append(row)
        cursor.close()
        conn.close()
        return records
        
    @staticmethod
    def get_by_id(unique_id):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT * FROM DatasetInfo WHERE datasetID = ?"
        cursor.execute(sqlcmd1, unique_id)
        record = None
        for dbrow in cursor.fetchall():
            record = DatasetInfoModel(dbrow[0],dbrow[1])
        cursor.close()
        conn.close()
        return record
    
    @staticmethod
    def insert(obj):
        obj.datasetID = str(uuid.uuid4())
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "INSERT INTO DatasetInfo (datasetNameFile) VALUES(?)"
        cursor.execute(sqlcmd1, (obj.datasetNameFile))
        cursor.close()
        conn.close()
        
    
    @staticmethod
    def update(obj):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "UPDATE DatasetInfo SET datasetNameFile = ? WHERE datasetID = ?"
        cursor.execute(sqlcmd1,  (obj.datasetNameFile,obj.datasetID))
        cursor.close()
        conn.close()
    
    @staticmethod
    def delete(unique_id):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "DELETE FROM DatasetInfo WHERE datasetID = ?"
        cursor.execute(sqlcmd1, (unique_id))
        cursor.close()
        conn.close()

