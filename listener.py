#!/bin/python

from __future__ import print_function
from gevent.pywsgi import WSGIServer
import sys, qrcode, base64
import sqlite3
from sqlite3 import Error
from flask import Flask, request, send_from_directory
app = Flask(__name__)

listening_port = 9000

## Main Flask Function to Serve Up Images and Accept Input via Web Parameters
@app.route("/img.png")
def hello():
    agentid = request.args.get("id")
    agentname = request.args.get("name")
    cmdresult = request.args.get("result")
    if cmdresult == "":
       cmdresult = "check in"
    
    filename = agentid + '.png'
    path = 'img/' + filename
    
    with open('img/agent.png', 'rb') as f:
        data = f.read()

    with open(path, 'wb') as f:
        f.write(data)
    
    ip = request.remote_addr
    #print('New Agent Online: ' + agentid + ' (' + agentname + ') from ' + ip, file=sys.stderr)
    query(agentid, agentname, cmdresult, ip)
    return send_from_directory('img',filename)

def query(id, name, cmd, ipaddress):
    database = r"agents.db"
    
    # create a database connection
    conn = create_connection(database)
    with conn:
        # create a new project
        select_agent(conn, id, name, ipaddress)
        select_command(conn, id, cmd)

def create_qr(command, id):
    #b64cmd = base64.b64encode(command)
    #string_bytes = command.encode("ascii") 
    #base64_bytes = base64.b64encode(string_bytes) 
    #b64cmd = base64_bytes.decode("ascii")
    img = qrcode.make(command)
    filename = id + '.png'
    path = 'img/' + filename
    img.save(path)
    return
    
## Creates a Connection to the SQLite Database
def create_connection(db_file):

    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

## If Agent Checks in Update Friendly Name and Last Seen Timestamp
def update_agent(conn, id, name, ipaddress):

    cur = conn.cursor()
    cur.execute("UPDATE agents SET LastSeen = strftime('%Y-%m-%d %H:%M:%S','now'), Name = ?, IP = ? WHERE ID = ?;", (name,ipaddress,id,))

## If Agent Hasn't Been Seen Before Add to Database    
def insert_agent(conn, id, name, ipaddress):

    cur = conn.cursor()
    cur.execute("INSERT INTO agents (ID, LastSeen, Name, Active, IP) VALUES (?, strftime('%Y-%m-%d %H:%M:%S','now'), ?, 1, ?);", (id,name,ipaddress,))
    print('\r\nNew Agent Online: ' + id + ' (' + name + ') from ' + ipaddress + '\r\n', file=sys.stderr)

## Select Agent from ID via Web Request
def select_agent(conn, id, name, ipaddress):

    cur = conn.cursor()
    cur.execute("SELECT * FROM agents WHERE ID = ?", (id,))

    rows = cur.fetchall()
    
    rowlength = len(rows)
    
    if rowlength > 0:
        update_agent(conn, id, name, ipaddress)
    else:
        insert_agent(conn, id, name, ipaddress)

    return

## Look Up Commands and Decide What Image to Display
def select_command(conn, id, cmdresult):
  
    if cmdresult != "check in":
        cur = conn.cursor()
        cur.execute("UPDATE commands SET Result = ? WHERE AgentID = ?;", (cmdresult,id,))
 
    cur2 = conn.cursor()
    cur2.execute("SELECT Command FROM commands WHERE AgentID = ? AND Result IS NULL;", (id,))
    rows2 = cur2.fetchall()
    rowlength2 = len(rows2)
       
    if rowlength2 > 0:
        command = rows2[0][0]
        create_qr(command, id)
    return

http_server = WSGIServer(('0.0.0.0', listening_port), app, log=None)
http_server.serve_forever()