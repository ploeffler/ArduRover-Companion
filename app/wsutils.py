import asyncio
 
import websockets
import json  
import time
import numpy as np
import cv2
import base64
import threading


# create handler for each connection
#with open('/home/oe6pld/ownCloud/01_my_coding/Rover_PyControl/testbild.png', 'rb') as binary_file:
#    binary_file_data = binary_file.read()
#    imgBlank = base64.b64encode(binary_file_data)
    
PUBSUB = []
CMDS = []
imgBlank = cv2.imread('/home/oe6pld/ownCloud/01_my_coding/Rover_PyControl/testbild.png',cv2.IMREAD_UNCHANGED)
imgBlank = cv2.resize(imgBlank,(640,480),interpolation = cv2.INTER_AREA)
imgFrame = imgBlank
imgWarp = imgBlank
imgHist = imgBlank
rgbR = cv2.resize(imgBlank,(160,144))
rgbG = rgbR
rgbB = rgbR
hsvH = rgbR
hsvS = rgbR
hsvV = rgbR
blurimg = rgbR
thresholdimg = rgbR
morphimg = rgbR
async def handler(websocket, path):
    async for message in websocket:
        reply = f"{message}"
        msg = json.loads(message)
        # print(msg)
        if msg['type'] == "init":
            CMDS.append("init")
        if msg['type'] == "sync":
            await websocket.send(getimgjson(creator="frame",img=imgFrame))
            await websocket.send(getimgjson(creator="warpimg",img=imgWarp))
            await websocket.send(getimgjson(creator="hist",img=imgHist))
            #await websocket.send(getimgjson(creator="hist",img=imgHist))
            
        if msg['type'] == "minsync":
            await websocket.send(getimgjson(creator="rgbR",img=cv2.resize(rgbR,(160,144))))
            await websocket.send(getimgjson(creator="rgbG",img=cv2.resize(rgbG,(160,144))))
            await websocket.send(getimgjson(creator="rgbB",img=cv2.resize(rgbB,(160,144))))
            await websocket.send(getimgjson(creator="hsvH",img=cv2.resize(rgbR,(160,144))))
            await websocket.send(getimgjson(creator="hsvS",img=cv2.resize(hsvS,(160,144))))
            await websocket.send(getimgjson(creator="hsvV",img=cv2.resize(hsvV,(160,144))))
            await websocket.send(getimgjson(creator="blured",img=cv2.resize(blurimg,(160,144))))
            await websocket.send(getimgjson(creator="thres",img=cv2.resize(thresholdimg,(160,144))))
            await websocket.send(getimgjson(creator="morph",img=cv2.resize(morphimg,(160,144))))
            #for message in PUBSUB:
            # await websocket.send(message)
            #PUBSUB.clear()
        if msg['type'] == "save":
            CMDS.append("save")
        if msg['type'] == "cmd":
            CMDS.append(msg['data'])
        for message in PUBSUB:
             await websocket.send(message)
        PUBSUB.clear()
    print(PUBSUB)
    
        

            
    
 


def watermarker1(img):
    cv2.circle(img,(int(img.shape[1]/2),int(img.shape[0]/2)),20,(255,255,0),cv2.FILLED)
    return img

def watermarker2(img):
    datetime = time.asctime()
    cv2.putText(img,datetime,(10,10),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(0,255,0),2)
    return img

def receive(data):
    jdata = json.loads(data)

 
#start_server = websockets.serve(handler, "localhost", 8080)
 
def getimgjson(creator="frame",img=imgBlank):
    retval, png = cv2.imencode('.png', img)
    #print(png)
    b64b = base64.b64encode(png)
    b64s = str(b64b,'UTF-8')
    #print(b64s)
    data = {}
    imgdata = {}
    imgdata["creator"]=creator
    imgdata["image"]=b64s
    
    data["type"]="image"
    data["data"]= imgdata

    jsondata = json.dumps(data)
    return str(jsondata)
 
def getsettingsgrpjson(groupname):
    data = {}
    data['type'] = "settingsgroup"
    data['data'] = groupname
    jsondata = json.dumps(data)
    return str(jsondata)

def getsettingsitemjson(itemname,section,value,type="text"):
    data = {}
    data['type'] = "settingsitem"

    content = {}
    content["itemname"] = itemname
    content["itemsection"] = section
    content["itemtype"]=type
    content["value"] = value

    data['data'] = content

    jsondata = json.dumps(data)
    return str(jsondata)


async def broadcast(message):
    # send()
    # print(len(PUBSUB))
    # PUBSUB.append(getimgjson(creator=message,img=watermarker2(imgBlank)))
    return

async def broadcast_messages():
    while True:
        await asyncio.sleep(1)
        message = ...  # your application logic goes here
        # await broadcast("frame")
        # await broadcast("warp")

#start_server = websockets.serve(handler, "localhost", 8080)


async def main():
    async with websockets.serve(handler, "localhost", 8080):
        await broadcast_messages()  # runs forever
        
if __name__ == "__main__":
    asyncio.run(main())


def threaded_websocket():
    asyncio.run(main())

thread = threading.Thread(target=threaded_websocket)
#thread.start()
print("Spun off thread")