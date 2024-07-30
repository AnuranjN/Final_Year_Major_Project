from Constants import connString
import pyodbc
import datetime
import uuid
from Constants import contract_address
from web3 import Web3, HTTPProvider
import json
import pprint
        
class RoleModel:
    def __init__(self, roleID = 0,roleName = '',canRole = False,canUser = False,canDatasetInfo = False,canIoTData = False,canAreaVsSeason = False,canEnergyVsCost = False,canEnergyVsDistance = False,canCostVsDistance = False,canCsvToDatabase = False):
        self.roleID = roleID
        self.roleName = roleName
        self.canRole = canRole
        self.canUser = canUser
        self.canDatasetInfo = canDatasetInfo
        self.canIoTData = canIoTData
        self.canAreaVsSeason = canAreaVsSeason
        self.canEnergyVsCost = canEnergyVsCost
        self.canEnergyVsDistance = canEnergyVsDistance
        self.canCostVsDistance = canCostVsDistance
        self.canCsvToDatabase = canCsvToDatabase
       
        

    @staticmethod
    def get_all():
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT * FROM Role ORDER BY roleName"
        cursor.execute(sqlcmd1)
        records = []
        for dbrow in cursor.fetchall():
            row = RoleModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10])
            records.append(row)
        cursor.close()
        conn.close()
        return records

    @staticmethod
    def get_name_id():
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT roleID, roleName FROM Role ORDER BY roleName"
        cursor.execute(sqlcmd1)
        records = []
        for dbrow in cursor.fetchall():
            row = RoleModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10])
            records.append(row)
        cursor.close()
        conn.close()
        return records
        
    @staticmethod
    def get_by_id(unique_id):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT * FROM Role WHERE roleID = ?"
        cursor.execute(sqlcmd1, unique_id)
        record = None
        for dbrow in cursor.fetchall():
            record = RoleModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10])
        cursor.close()
        conn.close()
        return record
    
    @staticmethod
    def insert(obj):
        obj.roleID = str(uuid.uuid4())
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "INSERT INTO Role (roleName,canRole,canUser,canDatasetInfo,canIoTData,canAreaVsSeason,canEnergyVsCost,canEnergyVsDistance,canCostVsDistance,canCsvToDatabase) VALUES(?,?,?,?,?,?,?,?,?,?)"
        cursor.execute(sqlcmd1, (obj.roleName,obj.canRole,obj.canUser,obj.canDatasetInfo,obj.canIoTData,obj.canAreaVsSeason,obj.canEnergyVsCost,obj.canEnergyVsDistance,obj.canCostVsDistance,obj.canCsvToDatabase))
        cursor.close()
        conn.close()
        

        w3 = Web3(HTTPProvider('http://localhost:7545'))

        
        compiled_contract_path = '../../../BlockchainIIoT-Truffle/build/contracts/IoTDataContract.json'
        deployed_contract_address = contract_address
        
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)
            contract_abi = contract_json["abi"]
        
        contract = w3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        
        accounts = w3.eth.accounts
    
        
        tx_hash = contract.functions.perform_transactions().transact({'from': accounts[0]})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction receipt mined:")
        pprint.pprint(dict(receipt))
        print("\nWas transaction successful?")
        pprint.pprint(receipt["status"])
        
        
        
    
    @staticmethod
    def update(obj):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "UPDATE Role SET roleName = ?,canRole = ?,canUser = ?,canDatasetInfo = ?,canIoTData = ?,canAreaVsSeason = ?,canEnergyVsCost = ?,canEnergyVsDistance = ?,canCostVsDistance = ?,canCsvToDatabase = ? WHERE roleID = ?"
        cursor.execute(sqlcmd1,  (obj.roleName,obj.canRole,obj.canUser,obj.canDatasetInfo,obj.canIoTData,obj.canAreaVsSeason,obj.canEnergyVsCost,obj.canEnergyVsDistance,obj.canCostVsDistance,obj.canCsvToDatabase,obj.roleID))
        cursor.close()
        conn.close()
    
    @staticmethod
    def delete(unique_id):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "DELETE FROM Role WHERE roleID = ?"
        cursor.execute(sqlcmd1, (unique_id))
        cursor.close()
        conn.close()

