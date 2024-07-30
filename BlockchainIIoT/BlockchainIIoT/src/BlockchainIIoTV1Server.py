
from flask import Flask, request, render_template, redirect, url_for
import os
import pyodbc
import uuid
import time
from datetime import datetime
from Constants import connString

from DatasetInfoModel import DatasetInfoModel
from IoTDataModel import IoTDataModel
from RoleModel import RoleModel
from UsersModel import UsersModel


import pandas as pd
import matplotlib.pyplot as plt


app = Flask(__name__)
app.secret_key = "MySecret"
ctx = app.app_context()
ctx.push()

with ctx:
    pass
user_id = ""
emailid = ""
role_object = None
message = ""
msgType = ""

def initialize():
    global message, msgType
    message = ""
    msgType = ""

def process_role(option_id):
    
    
    if option_id == 0:
        if role_object.canDatasetInfo == False:
            return False
        
    if option_id == 1:
        if role_object.canIoTData == False:
            return False
        
    if option_id == 2:
        if role_object.canRole == False:
            return False
        

    if option_id == 4:
        if role_object.canAreaVsSeason == False:
            return False

    if option_id == 5:
        if role_object.canEnergyVsCost == False:
            return False

    if option_id == 6:
        if role_object.canEnergyVsDistance == False:
            return False

    if option_id == 7:
        if role_object.canCostVsDistance == False:
            return False

    if option_id == 8:
        if role_object.canCsvToDatabase == False:
            return False


    return True



@app.route("/")
def index():
    global user_id, emailid
    return render_template("Login.html")

@app.route("/processLogin", methods=["POST"])
def processLogin():
    global user_id, emailid, role_object
    emailid = request.form["emailid"]
    password = request.form["password"]
    conn1 = pyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM Users WHERE emailid = '" + emailid + "' AND password = '" + password + "' AND isActive = 1";
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()

    cur1.commit()
    if not row:
        return render_template("Login.html", processResult="Invalid Credentials")
    user_id = row[0]

    cur2 = conn1.cursor()
    sqlcmd2 = "SELECT * FROM Role WHERE RoleID = '" + str(row[6]) + "'"
    cur2.execute(sqlcmd2)
    row2 = cur2.fetchone()

    if not row2:
        return render_template("Login.html", processResult="Invalid Role")

    role_object = RoleModel(row2[0], row2[1], row2[2], row2[3], row2[4], row2[5], row2[6], row2[7], row2[8], row2[9], row2[10])

    return render_template("Dashboard.html")


@app.route("/ChangePassword")
def changePassword():
    global user_id, emailid
    return render_template("ChangePassword.html")


@app.route("/ProcessChangePassword", methods=["POST"])
def processChangePassword():
    global user_id, emailid
    oldPassword = request.form["oldPassword"]
    newPassword = request.form["newPassword"]
    confirmPassword = request.form["confirmPassword"]
    conn1 = pyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM User WHERE emailid = '" + emailid + "' AND password = '" + oldPassword + "'";
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if not row:
        return render_template("ChangePassword.html", msg="Invalid Old Password")

    if newPassword.strip() != confirmPassword.strip():
        return render_template("ChangePassword.html", msg="New Password and Confirm Password are NOT same")

    conn2 = pyodbc.connect(connString, autocommit=True)
    cur2 = conn2.cursor()
    sqlcmd2 = "UPDATE User SET password = '" + newPassword + "' WHERE emailid = '" + emailid + "'";
    cur1.execute(sqlcmd2)
    cur2.commit()
    return render_template("ChangePassword.html", msg="Password Changed Successfully")


@app.route("/Dashboard")
def Dashboard():
    global user_id, emailid
    return render_template("Dashboard.html")


@app.route("/Information")
def Information():
    global message, msgType
    return render_template("Information.html", msgType=msgType, message=message)


@app.route("/DatasetInfoListing")
def DatasetInfo_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canDatasetInfo = process_role(0)

    if canDatasetInfo == False:
        message = "You Don't Have Permission to Access DatasetInfo"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = DatasetInfoModel.get_all()

    return render_template("DatasetInfoListing.html", records=records)

@app.route("/DatasetInfoOperation")
def DatasetInfo_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canDatasetInfo = process_role(0)

    if not canDatasetInfo:
        message = "You Don't Have Permission to Access DatasetInfo"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = DatasetInfoModel("", "")

    DatasetInfo = DatasetInfoModel.get_all()

    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = DatasetInfoModel.get_by_id(unique_id)

    return render_template("DatasetInfoOperation.html", row=row, operation=operation, DatasetInfo=DatasetInfo, )

@app.route("/ProcessDatasetInfoOperation", methods=["POST"])
def process_DatasetInfo_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canDatasetInfo = process_role(0)
    if not canDatasetInfo:
        message = "You Don't Have Permission to Access DatasetInfo"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = DatasetInfoModel("", "")

    if operation != "Delete":
       obj.datasetID = request.form['datasetID']
       if len(request.files) != 0 :
        
                file = request.files['datasetNameFile']
                if file.filename != '':
                    datasetNameFile = file.filename
                    obj.datasetNameFile = datasetNameFile
                    f = os.path.join('static/UPLOADED_FILES', datasetNameFile)
                    file.save(f)
                else:
                    obj.datasetNameFile = request.form['hdatasetNameFile']
                

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.datasetID = request.form["datasetID"]
        obj.update(obj)

    if operation == "Delete":
        datasetID = request.form["datasetID"]
        obj.delete(datasetID)
        

    return redirect(url_for("DatasetInfo_listing"))
                
@app.route("/IoTDataListing")
def IoTData_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canIoTData = process_role(1)

    if canIoTData == False:
        message = "You Don't Have Permission to Access IoTData"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = IoTDataModel.get_all()

    return render_template("IoTDataListing.html", records=records)

@app.route("/IoTDataOperation")
def IoTData_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canIoTData = process_role(1)

    if not canIoTData:
        message = "You Don't Have Permission to Access IoTData"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = IoTDataModel("", "")

    IoTData = IoTDataModel.get_all()

    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = IoTDataModel.get_by_id(unique_id)

    return render_template("IoTDataOperation.html", row=row, operation=operation, IoTData=IoTData, )

@app.route("/ProcessIoTDataOperation", methods=["POST"])
def process_IoTData_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canIoTData = process_role(1)
    if not canIoTData:
        message = "You Don't Have Permission to Access IoTData"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = IoTDataModel("", "")

    if operation != "Delete":
       obj.uniqueID = request.form['uniqueID']
       obj.demandResponse = request.form['demandResponse']
       obj.area = request.form['area']
       obj.season = request.form['season']
       obj.energy = request.form['energy']
       obj.cost = request.form['cost']
       obj.pairNo = request.form['pairNo']
       obj.distance = request.form['distance']
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.uniqueID = request.form["uniqueID"]
        obj.update(obj)

    if operation == "Delete":
        uniqueID = request.form["uniqueID"]
        obj.delete(uniqueID)
        

    return redirect(url_for("IoTData_listing"))
                
@app.route("/RoleListing")
def Role_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canRole = process_role(2)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = RoleModel.get_all()

    return render_template("RoleListing.html", records=records)

@app.route("/RoleOperation")
def Role_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canRole = process_role(2)

    if not canRole:
        message = "You Don't Have Permission to Access Role"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = RoleModel("", "")

    Role = RoleModel.get_all()

    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = RoleModel.get_by_id(unique_id)

    return render_template("RoleOperation.html", row=row, operation=operation, Role=Role, )

@app.route("/ProcessRoleOperation", methods=["POST"])
def process_Role_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canRole = process_role(2)
    if not canRole:
        message = "You Don't Have Permission to Access Role"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = RoleModel("", "")

    if operation != "Delete":
       obj.roleID = request.form['roleID']
       obj.roleName = request.form['roleName']
       obj.canRole = 0 
       if request.form.get("canRole") != None : 
              obj.canRole = 1       
       obj.canUser = 0 
       if request.form.get("canUser") != None : 
              obj.canUser = 1       
       obj.canDatasetInfo = 0 
       if request.form.get("canDatasetInfo") != None : 
              obj.canDatasetInfo = 1       
       obj.canIoTData = 0 
       if request.form.get("canIoTData") != None : 
              obj.canIoTData = 1       
       obj.canAreaVsSeason = 0 
       if request.form.get("canAreaVsSeason") != None : 
              obj.canAreaVsSeason = 1       
       obj.canEnergyVsCost = 0 
       if request.form.get("canEnergyVsCost") != None : 
              obj.canEnergyVsCost = 1       
       obj.canEnergyVsDistance = 0 
       if request.form.get("canEnergyVsDistance") != None : 
              obj.canEnergyVsDistance = 1       
       obj.canCostVsDistance = 0 
       if request.form.get("canCostVsDistance") != None : 
              obj.canCostVsDistance = 1       
       obj.canCsvToDatabase = 0 
       if request.form.get("canCsvToDatabase") != None : 
              obj.canCsvToDatabase = 1       
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.roleID = request.form["roleID"]
        obj.update(obj)

    if operation == "Delete":
        roleID = request.form["roleID"]
        obj.delete(roleID)
        

    return redirect(url_for("Role_listing"))
                
@app.route("/UsersListing")
def Users_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canUsers = process_role(3)

    if canUsers == False:
        message = "You Don't Have Permission to Access Users"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = UsersModel.get_all()

    return render_template("UsersListing.html", records=records)

@app.route("/UsersOperation")
def Users_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canUsers = process_role(3)

    if not canUsers:
        message = "You Don't Have Permission to Access Users"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = UsersModel("", "")

    Users = UsersModel.get_all()

    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = UsersModel.get_by_id(unique_id)

    return render_template("UsersOperation.html", row=row, operation=operation, Users=Users, )

@app.route("/ProcessUsersOperation", methods=["POST"])
def process_Users_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canUsers = process_role(3)
    if not canUsers:
        message = "You Don't Have Permission to Access Users"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = UsersModel("", "")

    if operation != "Delete":
       obj.userID = request.form['userID']
       obj.userName = request.form['userName']
       obj.emailid = request.form['emailid']
       obj.password = request.form['password']
       obj.contactNo = request.form['contactNo']
       obj.isActive = 0 
       if request.form.get("isActive") != None : 
              obj.isActive = 1       
       obj.roleID = request.form['roleID']
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.userID = request.form["userID"]
        obj.update(obj)

    if operation == "Delete":
        userID = request.form["userID"]
        obj.delete(userID)
        

    return redirect(url_for("Users_listing"))
                


import hashlib
import json


@app.route("/BlockChainGeneration")
def BlockChainGeneration():

    conn = pyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM IoTData WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    sqlcmd = "SELECT COUNT(*) FROM IoTData WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksNotCreated = dbrow[0]
    return render_template('BlockChainGeneration.html', blocksCreated=blocksCreated, blocksNotCreated=blocksNotCreated)


@app.route("/ProcessBlockchainGeneration", methods=['POST'])
def ProcessBlockchainGeneration():

    conn = pyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM IoTData WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    blocksCreated = 0
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    prevHash = ""
    if blocksCreated != 0:
        connx = pyodbc.connect(connString, autocommit=True)
        cursorx = connx.cursor()
        sqlcmdx = "SELECT * FROM IoTData WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY sequenceNumber"
        cursorx.execute(sqlcmdx)
        dbrowx = cursorx.fetchone()
        if dbrowx:
            uniqueID = dbrowx[0]
            conny = pyodbc.connect(connString, autocommit=True)
            cursory = conny.cursor()
            sqlcmdy = "SELECT hash FROM IoTData WHERE sequenceNumber < '" + str(uniqueID) + "' ORDER BY sequenceNumber DESC"
            cursory.execute(sqlcmdy)
            dbrowy = cursory.fetchone()
            if dbrowy:
                prevHash = dbrowy[0]
            cursory.close()
            conny.close()
        cursorx.close()
        connx.close()
    conn = pyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT * FROM IoTData WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY sequenceNumber"
    cursor.execute(sqlcmd)

    while True:
        sqlcmd1 = ""
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        unqid = str(dbrow[11])
        
        bdata = str(dbrow[1]) + str(dbrow[2]) + str(dbrow[3]) + str(dbrow[4]) + str(dbrow[5])
        block_serialized = json.dumps(bdata, sort_keys=True).encode('utf-8')
        block_hash = hashlib.sha256(block_serialized).hexdigest()

        conn1 = pyodbc.connect(connString, autocommit=True)
        cursor1 = conn1.cursor()
        sqlcmd1 = "UPDATE IoTData SET isBlockChainGenerated = 1, hash = '" + block_hash + "', prevHash = '" + prevHash + "' WHERE sequenceNumber = '" + unqid + "'"
        cursor1.execute(sqlcmd1)
        cursor1.close()
        conn1.close()
        prevHash = block_hash
    return render_template('BlockchainGenerationResult.html')


@app.route("/BlockChainReport")
def BlockChainReport():

    conn = pyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()

    sqlcmd1 = "SELECT * FROM IoTData WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd1)
    conn2 = pyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM IoTData ORDER BY sequenceNumber DESC"
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = IoTDataModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10])
        records.append(row)
    return render_template('BlockChainReport.html', records=records)         
        
        


@app.route("/AreaVsSeasonGenerate")
def AreaVsSeason_generate():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canAreaVsSeason = process_role(4)
    
    if not canAreaVsSeason:
        message = "You Don't Have Permission to Access AreaVsSeason"
        msgType = "Error"
        return redirect(url_for("Information"))
        
    return render_template('AreaVsSeasonGenerate.html')   
    

@app.route("/AreaVsSeasonGenerateResult")
def AreaVsSeason_generate_result():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canAreaVsSeason = process_role(4)
    
    if not canAreaVsSeason:
        message = "You Don't Have Permission to Access AreaVsSeason"
        msgType = "Error"
        return redirect(url_for("Information"))
        
    df = pd.read_csv(os.path.join('static/UPLOADED_FILES', "industrial_iot_data.csv")).head(10)
    plt.figure(figsize=(20, 10))
    plt.bar(df["Area"], df["Season"])
    plt.xlabel('Area', fontsize=5)
    plt.ylabel('Season', fontsize=5)
    plt.xticks(df["Area"], df["Season"], fontsize=5, rotation=30)
    plt.title('Area vs Season')
    plt.savefig('static/charts/AreaVsSeason.png')
    return render_template('AreaVsSeasonGenerateResult.html', heading='Area vs Season', image_file_name='AreaVsSeason.png')
             
@app.route("/EnergyVsCostGenerate")
def EnergyVsCost_generate():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canEnergyVsCost = process_role(5)
    
    if not canEnergyVsCost:
        message = "You Don't Have Permission to Access EnergyVsCost"
        msgType = "Error"
        return redirect(url_for("Information"))
        
    return render_template('EnergyVsCostGenerate.html')   
    

@app.route("/EnergyVsCostGenerateResult")
def EnergyVsCost_generate_result():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canEnergyVsCost = process_role(5)
    
    if not canEnergyVsCost:
        message = "You Don't Have Permission to Access EnergyVsCost"
        msgType = "Error"
        return redirect(url_for("Information"))
        
    df = pd.read_csv(os.path.join('static/UPLOADED_FILES', "industrial_iot_data.csv"))
    plt.figure(figsize=(20, 10))
    plt.bar(df["Energy"], df["Cost"])
    plt.xlabel('Energy', fontsize=5)
    plt.ylabel('Cost', fontsize=5)
    plt.xticks(df["Energy"], df["Cost"], fontsize=5, rotation=30)
    plt.title('Energy vs Cost')
    plt.savefig('static/charts/EnergyVsCost.png')
    return render_template('EnergyVsCostGenerateResult.html', heading='Energy vs Cost', image_file_name='EnergyVsCost.png')
             
@app.route("/EnergyVsDistanceGenerate")
def EnergyVsDistance_generate():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canEnergyVsDistance = process_role(6)
    
    if not canEnergyVsDistance:
        message = "You Don't Have Permission to Access EnergyVsDistance"
        msgType = "Error"
        return redirect(url_for("Information"))
        
    return render_template('EnergyVsDistanceGenerate.html')   
    

@app.route("/EnergyVsDistanceGenerateResult")
def EnergyVsDistance_generate_result():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canEnergyVsDistance = process_role(6)
    
    if not canEnergyVsDistance:
        message = "You Don't Have Permission to Access EnergyVsDistance"
        msgType = "Error"
        return redirect(url_for("Information"))
        
    df = pd.read_csv(os.path.join('static/UPLOADED_FILES', "industrial_iot_data.csv"))
    plt.figure(figsize=(20, 10))
    plt.bar(df["Energy"], df["Distance"])
    plt.xlabel('Energy', fontsize=5)
    plt.ylabel('Distance', fontsize=5)
    plt.xticks(df["Energy"], df["Distance"], fontsize=5, rotation=30)
    plt.title('Energy vs Distance')
    plt.savefig('static/charts/EnergyVsDistance.png')
    return render_template('EnergyVsDistanceGenerateResult.html', heading='Energy vs Distance', image_file_name='EnergyVsDistance.png')
             
@app.route("/CostVsDistanceGenerate")
def CostVsDistance_generate():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canCostVsDistance = process_role(7)
    
    if not canCostVsDistance:
        message = "You Don't Have Permission to Access CostVsDistance"
        msgType = "Error"
        return redirect(url_for("Information"))
        
    return render_template('CostVsDistanceGenerate.html')   
    

@app.route("/CostVsDistanceGenerateResult")
def CostVsDistance_generate_result():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canCostVsDistance = process_role(7)
    
    if not canCostVsDistance:
        message = "You Don't Have Permission to Access CostVsDistance"
        msgType = "Error"
        return redirect(url_for("Information"))
        
    df = pd.read_csv(os.path.join('static/UPLOADED_FILES', "industrial_iot_data.csv"))
    plt.figure(figsize=(20, 10))
    plt.bar(df["Cost"], df["Distance"])
    plt.xlabel('Cost', fontsize=5)
    plt.ylabel('Distance', fontsize=5)
    plt.xticks(df["Cost"], df["Distance"], fontsize=5, rotation=30)
    plt.title('Cost vs Distance')
    plt.savefig('static/charts/CostVsDistance.png')
    return render_template('CostVsDistanceGenerateResult.html', heading='Cost vs Distance', image_file_name='CostVsDistance.png')

import uuid
@app.route("/CsvToDatabase")
def CsvToDatabase_generate_result():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canCsvToDatabase = process_role(8)
        
    if not canCsvToDatabase:
        message = "You Don't Have Permission to Access CsvToDatabase"
        msgType = "Error"
        return redirect(url_for("Information")) 
            
    df = pd.read_csv(os.path.join('static/UPLOADED_FILES', "industrial_iot_data.csv"))

    conn1 = pyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "DELETE FROM  IoTData"
    cur1.execute(sqlcmd1)
    cur1.commit()
    conn1.close()
        
    for index, row in df.iterrows():

        obj = IoTDataModel("", "")

        obj.uniqueID = str(uuid.uuid4())
        obj.demandResponse = str(row[0])
        obj.area = str(row[1])
        obj.season = str(row[2])
        obj.energy = str(row[3])
        obj.cost = str(row[4])
        obj.pairNo = str(row[5])
        obj.distance = str(row[6])

        IoTDataModel.insert(obj)
    return render_template('CsvToDatabase.html')   
         
if __name__ == "__main__":
    app.run(port=5002)

                