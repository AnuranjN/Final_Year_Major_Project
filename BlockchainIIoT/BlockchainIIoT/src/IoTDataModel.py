from Constants import connString
import pyodbc
import datetime
import uuid
from Constants import contract_address
from web3 import Web3, HTTPProvider
import json
import pprint
import uuid
class IoTDataModel:
    def __init__(self, uniqueID = 0,demandResponse = 0,area = 0,season = 0,energy = 0,cost = 0,pairNo = 0,distance = 0,prevHash = '',hash = '',isBlockChainGenerated = False):
        self.uniqueID = uniqueID
        self.demandResponse = demandResponse
        self.area = area
        self.season = season
        self.energy = energy
        self.cost = cost
        self.pairNo = pairNo
        self.distance = distance
        self.prevHash = prevHash
        self.hash = hash
        self.isBlockChainGenerated = isBlockChainGenerated
       
        

    @staticmethod
    def get_all():
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT * FROM IoTData ORDER BY demandResponse"
        cursor.execute(sqlcmd1)
        records = []
        for dbrow in cursor.fetchall():
            row = IoTDataModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10])
            records.append(row)
        cursor.close()
        conn.close()
        return records

    @staticmethod
    def get_name_id():
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT uniqueID, demandResponse FROM IoTData ORDER BY demandResponse"
        cursor.execute(sqlcmd1)
        records = []
        for dbrow in cursor.fetchall():
            row = IoTDataModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10])
            records.append(row)
        cursor.close()
        conn.close()
        return records
        
    @staticmethod
    def get_by_id(unique_id):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT * FROM IoTData WHERE uniqueID = ?"
        cursor.execute(sqlcmd1, unique_id)
        record = None
        for dbrow in cursor.fetchall():
            record = IoTDataModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10])
        cursor.close()
        conn.close()
        return record
    
    @staticmethod
    def insert(obj):
        obj.uniqueID = str(uuid.uuid4())
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        obj.uniqueID = str(uuid.uuid4())
        sqlcmd1 = "INSERT INTO IoTData (uniqueID, demandResponse,area,season,energy,cost,pairNo,distance,prevHash,hash,isBlockChainGenerated) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
        cursor.execute(sqlcmd1, (obj.uniqueID, obj.demandResponse,obj.area,obj.season,obj.energy,obj.cost,obj.pairNo,obj.distance,obj.prevHash,obj.hash,obj.isBlockChainGenerated))
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
        sqlcmd1 = "UPDATE IoTData SET demandResponse = ?,area = ?,season = ?,energy = ?,cost = ?,pairNo = ?,distance = ?,prevHash = ?,hash = ?,isBlockChainGenerated = ? WHERE uniqueID = ?"
        cursor.execute(sqlcmd1,  (obj.demandResponse,obj.area,obj.season,obj.energy,obj.cost,obj.pairNo,obj.distance,obj.prevHash,obj.hash,obj.isBlockChainGenerated,obj.uniqueID))
        cursor.close()
        conn.close()
    
    @staticmethod
    def delete(unique_id):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "DELETE FROM IoTData WHERE uniqueID = ?"
        cursor.execute(sqlcmd1, (unique_id))
        cursor.close()
        conn.close()

