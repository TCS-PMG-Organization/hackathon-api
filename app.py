from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
from dateutil.relativedelta import relativedelta
import json, urllib3, requests, random, smtplib, os, sys

app = Flask(__name__)
CORS(app)

#MONGODB_USER = os.environ.get('MONGODB_USER')
#MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
#MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE')
#MONGODB_DOMAIN = os.environ.get('MONGODB_DOMAIN')
#MONGODB_PORT = os.environ.get('MONGODB_PORT')
#WSO2_DOMAIN = os.environ.get('WSO2_DOMAIN')
#WSO2_PORT = os.environ.get('WSO2_PORT')
#WSO2_API_VERSION = os.environ.get('WSO2_API_VERSION')
MONGODB_USER = "admin"
MONGODB_PASSWORD = "admin"
MONGODB_DATABASE = "Edge_BankDB"
MONGODB_DOMAIN = "45a49dbf-us-east.lb.appdomain.cloud"
MONGODB_PORT = "27017"

# print(os.environ)
#print('MONGODB_USER = '+str(os.environ.get('MONGODB_USER')))
#print('MONGODB_PASSWORD = '+str(os.environ.get('MONGODB_PASSWORD')))
#print('MONGODB_DATABASE = '+str(os.environ.get('MONGODB_DATABASE')))
#print('MONGODB_DOMAIN = '+str(os.environ.get('MONGODB_DOMAIN')))
#print('MONGODB_PORT = '+str(os.environ.get('MONGODB_PORT')))
#print('WSO2_DOMAIN = '+str(os.environ.get('WSO2_DOMAIN')))
#print('WSO2_PORT = '+str(os.environ.get('WSO2_PORT')))
#print('WSO2_API_VERSION = '+str(os.environ.get('WSO2_API_VERSION')))
print('MONGODB_USER = '+str(MONGODB_USER))
print('MONGODB_PASSWORD = '+str(MONGODB_PASSWORD))
print('MONGODB_DATABASE = '+str(MONGODB_DATABASE))
print('MONGODB_DOMAIN = '+str(MONGODB_DOMAIN))
print('MONGODB_PORT = '+str(MONGODB_PORT))

try:
    if(MONGODB_USER == None or MONGODB_PASSWORD == None):
        MONGODB_URL = "mongodb://"+MONGODB_DOMAIN+":"+MONGODB_PORT
    else:
        MONGODB_URL = "mongodb://"+MONGODB_USER+":"+MONGODB_PASSWORD+"@"+MONGODB_DOMAIN+":"+MONGODB_PORT

    Edge_Client = MongoClient(MONGODB_URL)
    #Edge_Client = MongoClient('mongodb://158.176.180.100:27017')
    #Edge_Client = MongoClient('mongodb://localhost:27017')
except Exception as e:
    print(e)
    print("Something wrong in MongoDB connection URL!!! Check Environment Variables values\nLeave \"MONGODB_USER\" and \"MONGODB_PASSWORD\" blank if not needed\nProvide \"MONGODB_DOMAIN\" and \"MONGODB_PORT\" correctly")
    sys.exit(0)

try:
    Edge_BankDB = Edge_Client[MONGODB_DATABASE]
    #Edge_BankDB = Edge_Client['Edge_BankDB']
except Exception as e:
    print(e)
    print("Cannot connect to the bank database!!! Check value of the Environment Variable \"MONGODB_DATABASE\". This cannot be left blank.")
    sys.exit(0)

'''
try:
    test_url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/xyz/"+WSO2_API_VERSION
except Exception as e:
    print(e)
    print("Check the values of WSO2 environment variables!!! They cannot be left blank. Neither will incorrect values work properly.")
    sys.exit(0)
'''

Edge_Accounts = Edge_BankDB['Edge_Accounts']
Edge_Dormant_Accounts = Edge_BankDB['Edge_Dormant_Accounts']
Edge_Cheque_Books = Edge_BankDB['Edge_Cheque_Books']
Edge_Credit_Cards = Edge_BankDB['Edge_Credit_Cards']
Edge_Users = Edge_BankDB['Edge_Users']
Edge_Passwords = Edge_BankDB['Edge_Passwords']
Edge_Config_Obj = Edge_BankDB['Edge_Config_Obj']
Edge_Render_Context = Edge_BankDB['Edge_Render_Context']
Edge_Account_Open_Form_Fields = Edge_BankDB['Edge_Account_Open_Form_Fields']
Edge_Master_Config = Edge_BankDB['Edge_Master_Config']
Edge_Login_OTP = Edge_BankDB['Edge_Login_OTP']

#-UTILITY FUNCTIONS AND API'S-#############################################################################################################
def get_otp():
    data = "0123456789abcdefghijklmnopqrstuvwxyz"
    data_len = len(data)

    otp=""

    for i in range(6):
        otp += data[int(random.random()*data_len)]

    return otp

@app.route("/")
def hello_world():
    return ("hello world \nMONGODB_URL = " + MONGODB_URL)

@app.route("/login", methods=['POST'])
def login():
    msg = ""
    login_data = request.get_json()
    
    username = str(login_data["username"])
    password = str(login_data["password"])
    
    print(username)
    print(password)

    username_query = {"user_name" : username}
    password_query = {"user_password" : password}
    
    if (Edge_Users.count_documents(username_query) == 1) and (Edge_Passwords.count_documents(password_query) == 1) :
        data = Edge_Users.find_one(username_query)
        
        msg = {"error" : "false",
            "errorMsg" : "User found",
            "role" : data['role'],
            "bank_id" : data['bank_id'],
            "country_id" : data['country_id'],
            "token" : "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ik5UZG1aak00WkRrM05qWTBZemM1TW1abU9EZ3dNVEUzTVdZd05ERTVNV1JsWkRnNE56YzRaQT09In0.eyJhdWQiOiJodHRwOlwvXC9vcmcud3NvMi5hcGltZ3RcL2dhdGV3YXkiLCJzdWIiOiJhZG1pbkBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6ImFkbWluIiwidGllclF1b3RhVHlwZSI6InJlcXVlc3RDb3VudCIsInRpZXIiOiIxMFBlck1pbiIsIm5hbWUiOiJ0ZXN0IiwiaWQiOjIsInV1aWQiOm51bGx9LCJzY29wZSI6ImFtX2FwcGxpY2F0aW9uX3Njb3BlIGRlZmF1bHQiLCJpc3MiOiJodHRwczpcL1wvbG9jYWxob3N0Ojk0NDNcL29hdXRoMlwvdG9rZW4iLCJ0aWVySW5mbyI6eyJHb2xkIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjowLCJzcGlrZUFycmVzdFVuaXQiOm51bGx9fSwia2V5dHlwZSI6IlBST0RVQ1RJT04iLCJzdWJzY3JpYmVkQVBJcyI6W3sic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJmZXRjaF9tYXN0ZXJfY29uZmlnIiwiY29udGV4dCI6IlwvZmV0Y2hfbWFzdGVyX2NvbmZpZ1wvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoidXBkYXRlX2RhdGFfdG9fY29uZmlnX29iaiIsImNvbnRleHQiOiJcL3VwZGF0ZV9kYXRhX3RvX2NvbmZpZ19vYmpcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImNyZWF0ZV9iYW5rX2FjY291bnQiLCJjb250ZXh0IjoiXC9jcmVhdGVfYmFua19hY2NvdW50XC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJmZXRjaF9jb25maWdfb2JqIiwiY29udGV4dCI6IlwvZmV0Y2hfY29uZmlnX29ialwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoidXBkYXRlX2RhdGFfdG9fbWFzdGVyX2NvbmZpZyIsImNvbnRleHQiOiJcL3VwZGF0ZV9kYXRhX3RvX21hc3Rlcl9jb25maWdcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImZldGNoX2FjY291bnRfZm9ybV9kZXRhaWxzIiwiY29udGV4dCI6IlwvZmV0Y2hfYWNjb3VudF9mb3JtX2RldGFpbHNcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImdldF9wcm9jZXNzZWRfaW5kaWNhdG9yX2NvdW50IiwiY29udGV4dCI6IlwvZ2V0X3Byb2Nlc3NlZF9pbmRpY2F0b3JfY291bnRcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImNyZWF0ZV9kb3JtYW50X2FjY291bnRfcmVxdWVzdCIsImNvbnRleHQiOiJcL2NyZWF0ZV9kb3JtYW50X2FjY291bnRfcmVxdWVzdFwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiZmV0Y2hfZG9ybWFudF9hY2NvdW50X2Zvcm0iLCJjb250ZXh0IjoiXC9mZXRjaF9kb3JtYW50X2FjY291bnRfZm9ybVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiZmV0Y2hfZG9ybWFudF9jb25maWdfb2JqIiwiY29udGV4dCI6IlwvZmV0Y2hfZG9ybWFudF9jb25maWdfb2JqXC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJ1cGRhdGVfZG9ybWFudF9jb25maWdfb2JqX2RhdGEiLCJjb250ZXh0IjoiXC91cGRhdGVfZG9ybWFudF9jb25maWdfb2JqX2RhdGFcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImdldF9kb3JtYW50X3Byb2Nlc3NlZF9jb3VudCIsImNvbnRleHQiOiJcL2dldF9kb3JtYW50X3Byb2Nlc3NlZF9jb3VudFwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiY3JlYXRlX2NoZXF1ZV9ib29rX3JlcXVlc3QiLCJjb250ZXh0IjoiXC9jcmVhdGVfY2hlcXVlX2Jvb2tfcmVxdWVzdFwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiZmV0Y2hfY2hlcXVlX2Jvb2tfZm9ybSIsImNvbnRleHQiOiJcL2ZldGNoX2NoZXF1ZV9ib29rX2Zvcm1cLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImZldGNoX2NoZXF1ZV9ib29rX2NvbmZpZyIsImNvbnRleHQiOiJcL2ZldGNoX2NoZXF1ZV9ib29rX2NvbmZpZ1wvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoidXBkYXRlX2NoZXF1ZV9ib29rX2NvbmZpZyIsImNvbnRleHQiOiJcL3VwZGF0ZV9jaGVxdWVfYm9va19jb25maWdcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImdldF9jaGVxdWVfcHJvY2Vzc2VkX2NvdW50IiwiY29udGV4dCI6IlwvZ2V0X2NoZXF1ZV9wcm9jZXNzZWRfY291bnRcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImNyZWF0ZV9jcmVkaXRfY2FyZF9yZXF1ZXN0IiwiY29udGV4dCI6IlwvY3JlYXRlX2NyZWRpdF9jYXJkX3JlcXVlc3RcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImZldGNoX2NyZWRpdF9jYXJkX2Zvcm0iLCJjb250ZXh0IjoiXC9mZXRjaF9jcmVkaXRfY2FyZF9mb3JtXC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJmZXRjaF9jcmVkaXRfY2FyZF9jb25maWciLCJjb250ZXh0IjoiXC9mZXRjaF9jcmVkaXRfY2FyZF9jb25maWdcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6InVwZGF0ZV9jcmVkaXRfY2FyZF9jb25maWciLCJjb250ZXh0IjoiXC91cGRhdGVfY3JlZGl0X2NhcmRfY29uZmlnXC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJnZXRfY3JlZGl0X3Byb2Nlc3NlZF9jb3VudCIsImNvbnRleHQiOiJcL2dldF9jcmVkaXRfcHJvY2Vzc2VkX2NvdW50XC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9XSwiY29uc3VtZXJLZXkiOiJBTVQwQ1RqWFVaRXdPcm8zOWJMRF9SV3dnUlFhIiwiZXhwIjozNzQ5NzAzMTE4LCJpYXQiOjE2MDIyMTk0NzEsImp0aSI6Ijg1MmQxMmQxLTE2NjktNGNkNC1iYmY1LTY1MzVlOWMwYjZmNSJ9.pBmV7wGJigzKM10mkciGPyef09AHsBclHVjWMU4I6EYyrPrr8ej4qiCxYDMkZxh-4u3NCxIP8FKAdHk2D5Xuz5SzgqYVhstjntr5cOOonCmUY0de3-iiGigS2exCum2LNpoJ88AnwRkiy6PDROtrhd4FHucwyJWBKKM88KaGP0ZeVTgV42hjo4lsarN4yaPv7cGYoui-5LBrAaP5Fc4s7T6cBoKzL85Pt4roVFmIfchSKguZo6OFGOklDLCu6Ou715l0m_0BJ7Pf_3rPYo0GodZ7XVHO8mrbACkaxppvMT_l5kcJe-8d3WqogFv8glYDAdxh5VHxwM5FpLD2zPB8KA"}
            
    else :
        msg = {"error" : "true",
            "errorMsg" : "User not found",
            "bank_id" : "null",
            "country_id" : "null",
            "token" : "null"}
            
    return jsonify(msg)

@app.route("/request_otp",methods=['POST'])
def request_otp():
    request_data = request.get_json()
    print(request_data)

    MY_ADDRESS = "cma.edge.banking@gmail.com"
    PASSWORD = "Welcome@123"

    #request_data = {'email': "cma.edge.banking@gmail.com"}

    otp = str(get_otp())

    if(Edge_Login_OTP.count_documents({"email":request_data['email']}) > 0):
        Edge_Login_OTP.update_one({'email' : request_data['email']},{"$set" : {"otp": otp}})
    else:
        Edge_Login_OTP.insert_one({"email": request_data['email'], "otp": otp})

    message = "Your Login OTP is "+otp

    s = smtplib.SMTP(host="smtp.gmail.com", port=587)
    s.ehlo()
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    msg = MIMEMultipart()

    msg['From']="Edge Bank "+MY_ADDRESS
    msg['To']="You "+request_data['email']
    msg['Subject']="Login OTP"

    msg.attach(MIMEText(message, 'plain'))

    print(msg)

    s.sendmail(MY_ADDRESS, request_data['email'], str(msg))

    del msg

    s.quit()

    return jsonify({"error":"false", "errorMsg":'', "successMsg":"Otp has been sent to your email"})

@app.route("/validate_otp", methods=['POST'])
def validate_otp():
    request_data = request.get_json()
    print(request_data)

    data = Edge_Login_OTP.find_one({"email" : request_data['email']})
    print(data)

    if(str(request_data['otp']) == str(data['otp'])):
        msg = {"error" : "false",
            "errorMsg" : "User found",
            "role" : "verify",
            "bank_id" : "ICICI",
            "country_id" : "IND",
            "token" : "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ik5UZG1aak00WkRrM05qWTBZemM1TW1abU9EZ3dNVEUzTVdZd05ERTVNV1JsWkRnNE56YzRaQT09In0.eyJhdWQiOiJodHRwOlwvXC9vcmcud3NvMi5hcGltZ3RcL2dhdGV3YXkiLCJzdWIiOiJhZG1pbkBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6ImFkbWluIiwidGllclF1b3RhVHlwZSI6InJlcXVlc3RDb3VudCIsInRpZXIiOiIxMFBlck1pbiIsIm5hbWUiOiJ0ZXN0IiwiaWQiOjIsInV1aWQiOm51bGx9LCJzY29wZSI6ImFtX2FwcGxpY2F0aW9uX3Njb3BlIGRlZmF1bHQiLCJpc3MiOiJodHRwczpcL1wvbG9jYWxob3N0Ojk0NDNcL29hdXRoMlwvdG9rZW4iLCJ0aWVySW5mbyI6eyJHb2xkIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjowLCJzcGlrZUFycmVzdFVuaXQiOm51bGx9fSwia2V5dHlwZSI6IlBST0RVQ1RJT04iLCJzdWJzY3JpYmVkQVBJcyI6W3sic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJmZXRjaF9tYXN0ZXJfY29uZmlnIiwiY29udGV4dCI6IlwvZmV0Y2hfbWFzdGVyX2NvbmZpZ1wvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoidXBkYXRlX2RhdGFfdG9fY29uZmlnX29iaiIsImNvbnRleHQiOiJcL3VwZGF0ZV9kYXRhX3RvX2NvbmZpZ19vYmpcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImNyZWF0ZV9iYW5rX2FjY291bnQiLCJjb250ZXh0IjoiXC9jcmVhdGVfYmFua19hY2NvdW50XC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJmZXRjaF9jb25maWdfb2JqIiwiY29udGV4dCI6IlwvZmV0Y2hfY29uZmlnX29ialwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoidXBkYXRlX2RhdGFfdG9fbWFzdGVyX2NvbmZpZyIsImNvbnRleHQiOiJcL3VwZGF0ZV9kYXRhX3RvX21hc3Rlcl9jb25maWdcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImZldGNoX2FjY291bnRfZm9ybV9kZXRhaWxzIiwiY29udGV4dCI6IlwvZmV0Y2hfYWNjb3VudF9mb3JtX2RldGFpbHNcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImdldF9wcm9jZXNzZWRfaW5kaWNhdG9yX2NvdW50IiwiY29udGV4dCI6IlwvZ2V0X3Byb2Nlc3NlZF9pbmRpY2F0b3JfY291bnRcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImNyZWF0ZV9kb3JtYW50X2FjY291bnRfcmVxdWVzdCIsImNvbnRleHQiOiJcL2NyZWF0ZV9kb3JtYW50X2FjY291bnRfcmVxdWVzdFwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiZmV0Y2hfZG9ybWFudF9hY2NvdW50X2Zvcm0iLCJjb250ZXh0IjoiXC9mZXRjaF9kb3JtYW50X2FjY291bnRfZm9ybVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiZmV0Y2hfZG9ybWFudF9jb25maWdfb2JqIiwiY29udGV4dCI6IlwvZmV0Y2hfZG9ybWFudF9jb25maWdfb2JqXC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJ1cGRhdGVfZG9ybWFudF9jb25maWdfb2JqX2RhdGEiLCJjb250ZXh0IjoiXC91cGRhdGVfZG9ybWFudF9jb25maWdfb2JqX2RhdGFcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImdldF9kb3JtYW50X3Byb2Nlc3NlZF9jb3VudCIsImNvbnRleHQiOiJcL2dldF9kb3JtYW50X3Byb2Nlc3NlZF9jb3VudFwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiY3JlYXRlX2NoZXF1ZV9ib29rX3JlcXVlc3QiLCJjb250ZXh0IjoiXC9jcmVhdGVfY2hlcXVlX2Jvb2tfcmVxdWVzdFwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiZmV0Y2hfY2hlcXVlX2Jvb2tfZm9ybSIsImNvbnRleHQiOiJcL2ZldGNoX2NoZXF1ZV9ib29rX2Zvcm1cLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImZldGNoX2NoZXF1ZV9ib29rX2NvbmZpZyIsImNvbnRleHQiOiJcL2ZldGNoX2NoZXF1ZV9ib29rX2NvbmZpZ1wvMS4wIiwicHVibGlzaGVyIjoiYWRtaW4iLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IkdvbGQifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoidXBkYXRlX2NoZXF1ZV9ib29rX2NvbmZpZyIsImNvbnRleHQiOiJcL3VwZGF0ZV9jaGVxdWVfYm9va19jb25maWdcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImdldF9jaGVxdWVfcHJvY2Vzc2VkX2NvdW50IiwiY29udGV4dCI6IlwvZ2V0X2NoZXF1ZV9wcm9jZXNzZWRfY291bnRcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImNyZWF0ZV9jcmVkaXRfY2FyZF9yZXF1ZXN0IiwiY29udGV4dCI6IlwvY3JlYXRlX2NyZWRpdF9jYXJkX3JlcXVlc3RcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6ImZldGNoX2NyZWRpdF9jYXJkX2Zvcm0iLCJjb250ZXh0IjoiXC9mZXRjaF9jcmVkaXRfY2FyZF9mb3JtXC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJmZXRjaF9jcmVkaXRfY2FyZF9jb25maWciLCJjb250ZXh0IjoiXC9mZXRjaF9jcmVkaXRfY2FyZF9jb25maWdcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiJHb2xkIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6InVwZGF0ZV9jcmVkaXRfY2FyZF9jb25maWciLCJjb250ZXh0IjoiXC91cGRhdGVfY3JlZGl0X2NhcmRfY29uZmlnXC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJnZXRfY3JlZGl0X3Byb2Nlc3NlZF9jb3VudCIsImNvbnRleHQiOiJcL2dldF9jcmVkaXRfcHJvY2Vzc2VkX2NvdW50XC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiR29sZCJ9XSwiY29uc3VtZXJLZXkiOiJBTVQwQ1RqWFVaRXdPcm8zOWJMRF9SV3dnUlFhIiwiZXhwIjozNzQ5NzAzMTE4LCJpYXQiOjE2MDIyMTk0NzEsImp0aSI6Ijg1MmQxMmQxLTE2NjktNGNkNC1iYmY1LTY1MzVlOWMwYjZmNSJ9.pBmV7wGJigzKM10mkciGPyef09AHsBclHVjWMU4I6EYyrPrr8ej4qiCxYDMkZxh-4u3NCxIP8FKAdHk2D5Xuz5SzgqYVhstjntr5cOOonCmUY0de3-iiGigS2exCum2LNpoJ88AnwRkiy6PDROtrhd4FHucwyJWBKKM88KaGP0ZeVTgV42hjo4lsarN4yaPv7cGYoui-5LBrAaP5Fc4s7T6cBoKzL85Pt4roVFmIfchSKguZo6OFGOklDLCu6Ou715l0m_0BJ7Pf_3rPYo0GodZ7XVHO8mrbACkaxppvMT_l5kcJe-8d3WqogFv8glYDAdxh5VHxwM5FpLD2zPB8KA"}
            
    else:
        msg = {"error" : "true",
            "errorMsg" : "Invalid OTP",
            "bank_id" : "null",
            "country_id" : "null",
            "token" : "null"}

    return jsonify(msg)

#-SYNCING API'S-##########################################################################################################################

@app.route("/get_unprocessed_account")
def get_unprocessed_account():
    if(Edge_Accounts.count_documents({"processed_indicator" : "NI"}) != 0):
        unprocessed_account = Edge_Accounts.find_one({"processed_indicator" : "NI"})
        print(type(unprocessed_account))
        print(unprocessed_account)
        msg = { "data" : unprocessed_account["account_info"],
            "_id" : str(unprocessed_account.get('_id')),
            "number_of_unprocessed" : Edge_Accounts.count_documents({"processed_indicator" : "NI"})}

    else:
        msg = { "data" : "null",
            "_id" : "null",
            "number_of_unprocessed" : Edge_Accounts.count_documents({"processed_indicator" : "NI"})}
    
    return jsonify(msg)

@app.route("/update_edgedb_from_maindb", methods=['POST'])
def update_edgedb_from_maindb():
    request_data = request.get_json()
    print(request_data)
    objId = request_data['objId']

    Edge_Accounts.update_one({'_id' : ObjectId(objId)},{"$set" : {'processed_indicator' : "I"}}, upsert=True)

    return jsonify({"error" : "false"})

@app.route("/get_unprocessed_dormant_acnt")
def get_unprocessed_dormant_acnt():
    if(Edge_Dormant_Accounts.count_documents({"processed_indicator" : "NI"}) != 0):
        unprocessed_account = Edge_Dormant_Accounts.find_one({"processed_indicator" : "NI"})
        print(type(unprocessed_account))
        print(unprocessed_account)
        msg = { "data" : unprocessed_account["account_info"],
            "_id" : str(unprocessed_account.get('_id')),
            "number_of_unprocessed" : Edge_Dormant_Accounts.count_documents({"processed_indicator" : "NI"})}

    else:
        msg = { "data" : "null",
            "_id" : "null",
            "number_of_unprocessed" : Edge_Dormant_Accounts.count_documents({"processed_indicator" : "NI"})}
    
    return jsonify(msg)

@app.route("/update_edge_dormant_from_main", methods=['POST'])
def update_edge_dormant_from_main():
    request_data = request.get_json()
    print(request_data)
    objId = request_data['objId']

    Edge_Dormant_Accounts.update_one({'_id' : ObjectId(objId)},{"$set" : {'processed_indicator' : "I"}}, upsert=True)

    return jsonify({"error" : "false"})

@app.route("/get_unprocessed_cheque_books")
def get_unprocessed_cheque_books():
    if(Edge_Cheque_Books.count_documents({"processed_indicator" : "NI"}) != 0):
        unprocessed_account = Edge_Cheque_Books.find_one({"processed_indicator" : "NI"})
        print(type(unprocessed_account))
        print(unprocessed_account)
        msg = { "data" : unprocessed_account["account_info"],
            "_id" : str(unprocessed_account.get('_id')),
            "number_of_unprocessed" : Edge_Cheque_Books.count_documents({"processed_indicator" : "NI"})}

    else:
        msg = { "data" : "null",
            "_id" : "null",
            "number_of_unprocessed" : Edge_Cheque_Books.count_documents({"processed_indicator" : "NI"})}
    
    return jsonify(msg)

@app.route("/update_edge_cheque_from_main", methods=['POST'])
def update_edge_cheque_from_main():
    request_data = request.get_json()
    print(request_data)
    objId = request_data['objId']

    Edge_Cheque_Books.update_one({'_id' : ObjectId(objId)},{"$set" : {'processed_indicator' : "I"}}, upsert=True)

    return jsonify({"error" : "false"})

@app.route("/get_unprocessed_credit_cards")
def get_unprocessed_credit_cards():
    if(Edge_Credit_Cards.count_documents({"processed_indicator" : "NI"}) != 0):
        unprocessed_account = Edge_Credit_Cards.find_one({"processed_indicator" : "NI"})
        print(type(unprocessed_account))
        print(unprocessed_account)
        msg = { "data" : unprocessed_account["account_info"],
            "_id" : str(unprocessed_account.get('_id')),
            "number_of_unprocessed" : Edge_Credit_Cards.count_documents({"processed_indicator" : "NI"})}

    else:
        msg = { "data" : "null",
            "_id" : "null",
            "number_of_unprocessed" : Edge_Credit_Cards.count_documents({"processed_indicator" : "NI"})}
    
    return jsonify(msg)

@app.route("/update_edge_ccard_from_main", methods=['POST'])
def update_edge_ccard_from_main():
    request_data = request.get_json()
    print(request_data)
    objId = request_data['objId']

    Edge_Credit_Cards.update_one({'_id' : ObjectId(objId)},{"$set" : {'processed_indicator' : "I"}}, upsert=True)

    return jsonify({"error" : "false"})

#-MASTER DATA CONFIGURATION API'S-######################################################################################################

@app.route("/fetch_master_config", methods=['POST'])
def fetch_master_config():
    master_config_data = Edge_Master_Config.find_one()
    msg = {"error" : "flase",
            "errorMsg" : "Configuration Found",
            "dropDownData" : master_config_data['dropDownData']
    }
    return jsonify(msg)

@app.route("/call_fetch_master_config_api", methods=['POST'])
def call_fetch_master_config_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = dict(request.headers)

    print("/call_fetch_master_config_api")
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/fetch_master_config/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/fetch_config_obj", headers=headers, verify=False)

    print(response.json)
    return response.json()

@app.route("/update_data_to_master_config", methods=['POST'])
def update_data_to_master_config():
    master_config_data = Edge_Master_Config.find_one()
    request_data = request.get_json()

    try:
        for x in master_config_data['dropDownData']:
            if(x['country'] == request_data['country']):
                x['groupingData'] = request_data['groupingData']
        Edge_Master_Config.update_one({},{"$set" : {"dropDownData" : master_config_data["dropDownData"]}})
        msg = {"error" : "false",
            "errorMsg" : "Push Successful"
        }
    except Exception as e:
        print(e)
        msg = {"error" : "true",
            "errorMsg" : "Push Unsuccessful"
        }
    return jsonify(msg)

@app.route("/call_update_data_to_master_config_api", methods=['POST'])
def call_update_data_to_master_config_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_update_data_to_master_config_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/update_data_to_master_config/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/update_data_to_config_obj",headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

#-NEW ACCOUNT CREATION API'S-#############################################################################################################
@app.route("/create_bank_account", methods=['POST'])
def create_bank_account():
    msg = ""
    try:
        data = request.get_json()
        print("/create_bank_account")
        print(type(data))
        print(data)
        Edge_Accounts.insert_one(data)
        msg = {"error" : "false",
            "errorMsg" : "null",
            "successMsg" : "Your Account has been created successfully !!!"}

    except:
        msg = {"error" : "true",
            "errorMsg" : "Your Account could not be created due to link failure...!!!",
            "successMsg" : "null"}        	

    return jsonify(msg)

@app.route("/call_create_bank_account_api", methods=['POST'])
def call_create_bank_account_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_create_bank_account_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/create_bank_account/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/create_bank_account", headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/fetch_account_form_details", methods=['POST'])
def fetch_account_form_details():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "new_account"})

    form_data = request.get_json()
    
    bank_id = str(form_data["bank_id"])
    country_id = str(form_data["country_id"])

    for x in config_obj_data['allData']:
        if(x['bank'] == bank_id and x['country'] == country_id):
            msg = {"error" : "false",
                "errorMsg" : "Configuration found",
                "formData" : {"data" : x["groupingData"]},
                "bank_id" : x["bank"],
                "country_id" : x["country"]
            }
            break
        else :
            msg = {"error" : "true",
                "errorMsg" : "Configuration not found",
                "formData" : "null"
            }
            
    return jsonify(msg)

@app.route("/call_fetch_account_form_details_api", methods=['POST'])
def call_fetch_account_form_details_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_fetch_account_form_details_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/fetch_account_form_details/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/fetch_account_form_details", headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/fetch_config_obj", methods=['POST'])
def fetch_config_obj():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "new_account"})
    master_config_data = Edge_Master_Config.find_one()
    msg = { "error" : "false",
        "errorMsg" : "Schema Found",
        "allData" : config_obj_data["allData"],
        "dropDownData" : master_config_data['dropDownData']
    }
    return jsonify(msg)

@app.route("/call_fetch_config_obj_api", methods=['POST'])
def call_fetch_config_obj_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = dict(request.headers)

    print("/call_fetch_config_obj_api")
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/fetch_config_obj/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/fetch_config_obj", headers=headers, verify=False)

    print(response.json)
    return response.json()

@app.route("/update_data_to_config_obj", methods=['POST'])
def update_data_to_config_obj():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "new_account"})

    request_data = request.get_json()
    print(type(request_data))
    print(request_data)

    try:
        for x in config_obj_data["allData"]:
            if(x['bank'] == request_data['bank'] and x['country'] == request_data['country']):
                x['groupingData'] = request_data['groupingData']
        Edge_Config_Obj.update_one({"purpose" : "new_account"},{"$set" : {"allData" : config_obj_data["allData"]}})
        msg = {"error" : "false",
            "errorMsg" : "Push Successful"
        }
    except:
        msg = {"error" : "true",
            "errorMsg" : "Push Unsuccessful"
        }
    return jsonify(msg)

@app.route("/call_update_data_to_config_obj_api", methods=['POST'])
def call_update_data_to_config_obj_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_update_data_to_config_obj_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/update_data_to_config_obj/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/update_data_to_config_obj",headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/get_processed_indicator_count",methods=['POST'])
def get_processed_indicator_count():
    date_limit = date.today() + relativedelta(months=-12)
    date_limit = str(date_limit)
    date_limit = date_limit[:8]+"01"

    month_dict = {
        "01" : "Jan",
        "02" : "Feb",
        "03" : "Mar",
        "04" : "Apr",
        "05" : "May",
        "06" : "Jun",
        "07" : "Jul",
        "08" : "Aug",
        "09" : "Sep",
        "10" : "Oct",
        "11" : "Nov",
        "12" : "Dec"
    }
    barData = []
    previous_month = current_month = "xyz"
    synced, nonsynced, first_dict = 0,0,1

    for j in Edge_Accounts.find({"current_date":{'$gte': date_limit}}):
    
        current_month = j['current_date'][5:7]
        current_month = month_dict[current_month]

        if(previous_month != current_month and first_dict != 1):
            barData.append({"month" : previous_month, "Synced" : synced, "NonSynced" : nonsynced})
            previous_month=current_month
            synced = 0
            nonsynced = 0
        if(previous_month != current_month and first_dict == 1):
            previous_month=current_month
            first_dict = 0

        if(j['processed_indicator'] == "NI"):
            nonsynced += 1
        else:
            synced += 1
            
    barData.append({"month" : previous_month, "Synced" : synced, "NonSynced" : nonsynced})

    msg = {"barchartInfo" :{"barData" : barData}}
    return jsonify(msg)

@app.route("/call_get_processed_indicator_count_api", methods=['POST'])
def call_get_processed_indicator_count_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = dict(request.headers)

    print("/call_get_processed_indicator_count_api")
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/get_processed_indicator_count/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/get_processed_indicator_count", headers=headers, verify=False)

    print(response.json)
    return response.json()

#-DORMANT ACCOUNT PROCESSING API'S-###########################################################################################################
@app.route("/create_dormant_account_request", methods=['POST'])
def create_dormant_account_request():
    msg = ""
    try:
        data = request.get_json()
        print("/create_dormant_account_request")
        print(type(data))
        print(data)
        Edge_Dormant_Accounts.insert_one(data)
        msg = {"error" : "false",
            "errorMsg" : "null",
            "successMsg" : "Your Dormant Account Request has been registered successfully !!!"}

    except:
        msg = {"error" : "true",
            "errorMsg" : "Your Dormant Account Request could not be registered due to link failure...!!!",
            "successMsg" : "null"}        	

    return jsonify(msg)

@app.route("/call_create_dormant_account_request_api", methods=['POST'])
def call_create_dormant_account_request_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_create_dormant_account_request_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/create_dormant_account_request/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/create_dormant_account_request", headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/fetch_dormant_account_form", methods=['POST'])
def fetch_dormant_account_form():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "dormant_account"})

    form_data = request.get_json()
    
    bank_id = str(form_data["bank_id"])
    country_id = str(form_data["country_id"])

    for x in config_obj_data['allData']:
        if(x['bank'] == bank_id and x['country'] == country_id):
            msg = {"error" : "false",
                "errorMsg" : "Configuration found",
                "formData" : {"data" : x["groupingData"]},
                "bank_id" : x["bank"],
                "country_id" : x["country"]
            }
            break
        else :
            msg = {"error" : "true",
                "errorMsg" : "Configuration not found",
                "formData" : "null"
            }        
    
    return jsonify(msg)

@app.route("/call_fetch_dormant_account_form_api", methods=['POST'])
def call_fetch_dormant_account_form_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_fetch_dormant_account_form_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/fetch_dormant_account_form/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/fetch_dormant_account_form", headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/fetch_dormant_config_obj", methods=['POST'])
def fetch_dormant_config_obj():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "dormant_account"})
    master_config_data = Edge_Master_Config.find_one()
    msg = { "error" : "false",
        "errorMsg" : "Schema Found",
        "allData" : config_obj_data["allData"],
        "dropDownData" : master_config_data['dropDownData']
    }
    return jsonify(msg)

@app.route("/call_fetch_dormant_config_obj_api", methods=['POST'])
def call_fetch_dormant_config_obj_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = dict(request.headers)

    print("/call_fetch_dormant_config_obj_api")
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/fetch_dormant_config_obj/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/fetch_dormant_config_obj", headers=headers, verify=False)

    print(response.json)
    return response.json()

@app.route("/update_dormant_config_obj_data", methods=['POST'])
def update_dormant_config_obj_data():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "dormant_account"})

    request_data = request.get_json()
    print(type(request_data))
    print(request_data)

    try:
        for x in config_obj_data["allData"]:
            if(x['bank'] == request_data['bank'] and x['country'] == request_data['country']):
                x['groupingData'] = request_data['groupingData']
        Edge_Config_Obj.update_one({"purpose" : "dormant_account"},{"$set" : {"allData" : config_obj_data["allData"]}})
        msg = {"error" : "false",
            "errorMsg" : "Push Successful"
        }
    except:
        msg = {"error" : "true",
            "errorMsg" : "Push Unsuccessful"
        }
    return jsonify(msg)

@app.route("/call_update_dormant_config_obj_data_api", methods=['POST'])
def call_update_dormant_config_obj_data_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_update_dormant_config_obj_data_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/update_dormant_config_obj_data/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/update_dormant_config_obj_data",headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/get_dormant_processed_count",methods=['POST'])
def get_dormant_processed_count():
    date_limit = date.today() + relativedelta(months=-12)
    date_limit = str(date_limit)
    date_limit = date_limit[:8]+"01"

    month_dict = {
        "01" : "Jan",
        "02" : "Feb",
        "03" : "Mar",
        "04" : "Apr",
        "05" : "May",
        "06" : "Jun",
        "07" : "Jul",
        "08" : "Aug",
        "09" : "Sep",
        "10" : "Oct",
        "11" : "Nov",
        "12" : "Dec"
    }
    barData = []
    previous_month = current_month = "xyz"
    synced, nonsynced, first_dict = 0,0,1

    for j in Edge_Dormant_Accounts.find({"current_date":{'$gte': date_limit}}):
    
        current_month = j['current_date'][5:7]
        current_month = month_dict[current_month]

        if(previous_month != current_month and first_dict != 1):
            barData.append({"month" : previous_month, "Synced" : synced, "NonSynced" : nonsynced})
            previous_month=current_month
            synced = 0
            nonsynced = 0
        if(previous_month != current_month and first_dict == 1):
            previous_month=current_month
            first_dict = 0

        if(j['processed_indicator'] == "NI"):
            nonsynced += 1
        else:
            synced += 1
            
    barData.append({"month" : previous_month, "Synced" : synced, "NonSynced" : nonsynced})

    msg = {"barchartInfo" :{"dormantBarData" : barData}}
    return jsonify(msg)

@app.route("/call_get_dormant_processed_count_api", methods=['POST'])
def call_get_dormant_processed_count_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = dict(request.headers)

    print("/call_get_dormant_processed_count_api")
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/get_dormant_processed_count/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/get_dormant_processed_count", headers=headers, verify=False)

    print(response.json)
    return response.json()

#-CHEQUE BOOK REQUEST API'S-#############################################################################################################
@app.route("/create_cheque_book_request", methods=['POST'])
def create_cheque_book_request():
    msg = ""
    try:
        data = request.get_json()
        print("/create_cheque_book_request")
        print(type(data))
        print(data)
        Edge_Cheque_Books.insert_one(data)
        msg = {"error" : "false",
            "errorMsg" : "null",
            "successMsg" : "Your Cheque Book request has been submitted successfully !!!"}

    except:
        msg = {"error" : "true",
            "errorMsg" : "Your Cheque Book request could not be submitted due to link failure...!!!",
            "successMsg" : "null"}        	

    return jsonify(msg)

@app.route("/call_create_cheque_book_request_api", methods=['POST'])
def call_create_cheque_book_request_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_create_cheque_book_request_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/create_cheque_book_request/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/create_cheque_book_request", headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/fetch_cheque_book_form", methods=['POST'])
def fetch_cheque_book_form():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "cheque_book"})

    form_data = request.get_json()
    
    bank_id = str(form_data["bank_id"])
    country_id = str(form_data["country_id"])

    for x in config_obj_data['allData']:
        if(x['bank'] == bank_id and x['country'] == country_id):
            msg = {"error" : "false",
                "errorMsg" : "Configuration found",
                "formData" : {"data" : x["groupingData"]},
                "bank_id" : x["bank"],
                "country_id" : x["country"]
            }
            break
        else :
            msg = {"error" : "true",
                "errorMsg" : "Configuration not found",
                "formData" : "null"
            }
            
    return jsonify(msg)

@app.route("/call_fetch_cheque_book_form_api", methods=['POST'])
def call_fetch_cheque_book_form_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_fetch_cheque_book_form_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/fetch_cheque_book_form/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/fetch_cheque_book_form", headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/fetch_cheque_book_config", methods=['POST'])
def fetch_cheque_book_config():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "cheque_book"})
    master_config_data = Edge_Master_Config.find_one()
    msg = { "error" : "false",
        "errorMsg" : "Schema Found",
        "allData" : config_obj_data["allData"],
        "dropDownData" : master_config_data['dropDownData']
    }
    return jsonify(msg)

@app.route("/call_fetch_cheque_book_config_api", methods=['POST'])
def call_fetch_cheque_book_config_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = dict(request.headers)

    print("/call_fetch_cheque_book_config_api")
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/fetch_cheque_book_config/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/fetch_cheque_book_config", headers=headers, verify=False)

    print(response.json)
    return response.json()

@app.route("/update_cheque_book_config", methods=['POST'])
def update_cheque_book_config():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "cheque_book"})

    request_data = request.get_json()
    print(type(request_data))
    print(request_data)

    try:
        for x in config_obj_data["allData"]:
            if(x['bank'] == request_data['bank'] and x['country'] == request_data['country']):
                x['groupingData'] = request_data['groupingData']
        Edge_Config_Obj.update_one({"purpose" : "cheque_book"},{"$set" : {"allData" : config_obj_data["allData"]}})
        msg = {"error" : "false",
            "errorMsg" : "Push Successful"
        }
    except:
        msg = {"error" : "true",
            "errorMsg" : "Push Unsuccessful"
        }
    return jsonify(msg)

@app.route("/call_update_cheque_book_config_api", methods=['POST'])
def call_update_cheque_book_config_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_update_cheque_book_config_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/update_cheque_book_config/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/update_cheque_book_config",headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/get_cheque_processed_count",methods=['POST'])
def get_cheque_processed_count():
    date_limit = date.today() + relativedelta(months=-12)
    date_limit = str(date_limit)
    date_limit = date_limit[:8]+"01"

    month_dict = {
        "01" : "Jan",
        "02" : "Feb",
        "03" : "Mar",
        "04" : "Apr",
        "05" : "May",
        "06" : "Jun",
        "07" : "Jul",
        "08" : "Aug",
        "09" : "Sep",
        "10" : "Oct",
        "11" : "Nov",
        "12" : "Dec"
    }
    barData = []
    previous_month = current_month = "xyz"
    synced, nonsynced, first_dict = 0,0,1

    for j in Edge_Cheque_Books.find({"current_date":{'$gte': date_limit}}):
    
        current_month = j['current_date'][5:7]
        current_month = month_dict[current_month]

        if(previous_month != current_month and first_dict != 1):
            barData.append({"month" : previous_month, "Synced" : synced, "NonSynced" : nonsynced})
            previous_month=current_month
            synced = 0
            nonsynced = 0
        if(previous_month != current_month and first_dict == 1):
            previous_month=current_month
            first_dict = 0

        if(j['processed_indicator'] == "NI"):
            nonsynced += 1
        else:
            synced += 1
            
    barData.append({"month" : previous_month, "Synced" : synced, "NonSynced" : nonsynced})

    msg = {"barchartInfo" :{"chequeBarData" : barData}}
    return jsonify(msg)

@app.route("/call_get_cheque_processed_count_api", methods=['POST'])
def call_get_cheque_processed_count_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = dict(request.headers)

    print("/call_get_cheque_processed_count_api")
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/get_cheque_processed_count/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/get_cheque_processed_count", headers=headers, verify=False)

    print(response.json)
    return response.json()

#-CREDIT CARD REQUEST API'S-#############################################################################################################
@app.route("/create_credit_card_request", methods=['POST'])
def create_credit_card_request():
    msg = ""
    try:
        data = request.get_json()
        print("/create_cheque_book_request")
        print(type(data))
        print(data)
        Edge_Credit_Cards.insert_one(data)
        msg = {"error" : "false",
            "errorMsg" : "null",
            "successMsg" : "Your Credit Card request has been submitted successfully !!!"}

    except:
        msg = {"error" : "true",
            "errorMsg" : "Your Credit Card request could not be submitted due to link failure...!!!",
            "successMsg" : "null"}        	

    return jsonify(msg)

@app.route("/call_create_credit_card_request_api", methods=['POST'])
def call_create_credit_card_request_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_create_credit_card_request_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/create_credit_card_request/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/create_credit_card_request", headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/fetch_credit_card_form", methods=['POST'])
def fetch_credit_card_form():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "credit_card"})

    form_data = request.get_json()
    
    bank_id = str(form_data["bank_id"])
    country_id = str(form_data["country_id"])

    for x in config_obj_data['allData']:
        if(x['bank'] == bank_id and x['country'] == country_id):
            msg = {"error" : "false",
                "errorMsg" : "Configuration found",
                "formData" : {"data" : x["groupingData"]},
                "bank_id" : x["bank"],
                "country_id" : x["country"]
            }
            break
        else :
            msg = {"error" : "true",
                "errorMsg" : "Configuration not found",
                "formData" : "null"
            }
            
    return jsonify(msg)

@app.route("/call_fetch_credit_card_form_api", methods=['POST'])
def call_fetch_credit_card_form_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_fetch_credit_card_form_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/fetch_credit_card_form/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/fetch_credit_card_form", headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/fetch_credit_card_config", methods=['POST'])
def fetch_credit_card_config():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "credit_card"})
    master_config_data = Edge_Master_Config.find_one()
    msg = { "error" : "false",
        "errorMsg" : "Schema Found",
        "allData" : config_obj_data["allData"],
        "dropDownData" : master_config_data['dropDownData']
    }
    return jsonify(msg)

@app.route("/call_fetch_credit_card_config_api", methods=['POST'])
def call_fetch_credit_card_config_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = dict(request.headers)

    print("/call_fetch_credit_card_config_api")
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/fetch_credit_card_config/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/fetch_credit_card_config", headers=headers, verify=False)

    print(response.json)
    return response.json()

@app.route("/update_credit_card_config", methods=['POST'])
def update_credit_card_config():
    config_obj_data = Edge_Config_Obj.find_one({"purpose" : "credit_card"})

    request_data = request.get_json()
    print(type(request_data))
    print(request_data)

    try:
        for x in config_obj_data["allData"]:
            if(x['bank'] == request_data['bank'] and x['country'] == request_data['country']):
                x['groupingData'] = request_data['groupingData']
        Edge_Config_Obj.update_one({"purpose" : "credit_card"},{"$set" : {"allData" : config_obj_data["allData"]}})
        msg = {"error" : "false",
            "errorMsg" : "Push Successful"
        }
    except:
        msg = {"error" : "true",
            "errorMsg" : "Push Unsuccessful"
        }
    return jsonify(msg)

@app.route("/call_update_credit_card_config_api", methods=['POST'])
def call_update_credit_card_config_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = request.get_json()
    headers = dict(request.headers)

    print("/call_update_credit_card_config_api")
    print(type(body))
    print(body)
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/update_credit_card_config/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, json=body, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/update_credit_card_config",headers=headers, json=body, verify=False)

    print(response.json)
    return response.json()

@app.route("/get_credit_processed_count",methods=['POST'])
def get_credit_processed_count():
    date_limit = date.today() + relativedelta(months=-12)
    date_limit = str(date_limit)
    date_limit = date_limit[:8]+"01"

    month_dict = {
        "01" : "Jan",
        "02" : "Feb",
        "03" : "Mar",
        "04" : "Apr",
        "05" : "May",
        "06" : "Jun",
        "07" : "Jul",
        "08" : "Aug",
        "09" : "Sep",
        "10" : "Oct",
        "11" : "Nov",
        "12" : "Dec"
    }
    barData = []
    previous_month = current_month = "xyz"
    synced, nonsynced, first_dict = 0,0,1

    for j in Edge_Credit_Cards.find({"current_date":{'$gte': date_limit}}):
    
        current_month = j['current_date'][5:7]
        current_month = month_dict[current_month]

        if(previous_month != current_month and first_dict != 1):
            barData.append({"month" : previous_month, "Synced" : synced, "NonSynced" : nonsynced})
            previous_month=current_month
            synced = 0
            nonsynced = 0
        if(previous_month != current_month and first_dict == 1):
            previous_month=current_month
            first_dict = 0

        if(j['processed_indicator'] == "NI"):
            nonsynced += 1
        else:
            synced += 1
            
    barData.append({"month" : previous_month, "Synced" : synced, "NonSynced" : nonsynced})

    msg = {"barchartInfo" :{"creditBarData" : barData}}
    return jsonify(msg)

@app.route("/call_get_credit_processed_count_api", methods=['POST'])
def call_get_credit_processed_count_api():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = dict(request.headers)

    print("/call_get_credit_processed_count_api")
    print(type(headers))
    print(headers)

    #url = "https://"+WSO2_DOMAIN+":"+WSO2_PORT+"/get_credit_processed_count/"+WSO2_API_VERSION
    #response = requests.post(url, headers=headers, verify=False)
    response = requests.post("http://edge-open-api-fs-cloud-app-test-open-banking.mgmt-pot01-cluster-1fa025a294811d2b43b68d6ffd4c8b58-i000.us-east.containers.appdomain.cloud/get_credit_processed_count", headers=headers, verify=False)

    print(response.json)
    return response.json()

############################################################################################################################################
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
