
#from plantcv import plantcv as pcv
import libtools

libtools.installupdate("numpy")

import argparse
hasGui = False
hasOutput = False
verbosity = 0
parser = argparse.ArgumentParser(description="The companion app")
parser.add_argument('--gui',action=argparse.BooleanOptionalAction,default=False,help="enable graphical output")
parser.add_argument('--output',action=argparse.BooleanOptionalAction,default=False,help="craete an outputfile named output.mp4")
parser.add_argument('-v',action='count',default=0,help="logging verbosity")
parser.add_argument('-f',default="settings.ini",help="F = settings file")
args = parser.parse_args()

hasGui = args.gui
hasOutput = args.output
verbosity = args.v
settingsFileName = args.f 
if(verbosity>0):
    print("Starting with GUI : ",hasGui)
    print("Creating output.mp4 : ",hasOutput)
    print("Output verbosity: ",verbosity)
    print("Settings-Filename: ",settingsFileName)


import cv2
import numpy as np
import utilities
import configparser
from os.path import exists
import time
import asyncio
import wsutils
import threading, time
import json
import detector
import sys
import webserver
wsutils.wsthread.start()
webserver.websthread.start()

#cap = cv2.VideoCapture('Resources/20230124_133841.mp4')
settings = configparser.ConfigParser()



def initsettings():    
    
    if exists(settingsFileName):
        settings.read(settingsFileName)
        if(verbosity>0):
          print("Settings: file found and read")
        
    else:
        # settings-default
        if(verbosity>0):
          print("Settingsfile not found. Initiating with default values.")
        settings.add_section("General")
        settings.set('General','OP_Width',str(640))
        settings.set('General','OP_Heigth',str(480))
        settings.set('General','WebPort',str(8001))
        settings.add_section('Input')
        settings.set('Input','source',"Resources/20230129_162107_02.mp4")
        settings.set('Input','rotate',str(0))
        settings.set('Input','capture_width',str(640))
        settings.set('Input','capture_height',str(480))
        settings.set('Input','capture_fps',str(30))
        settings.add_section("Warping")
        settings.set('Warping','top-x-dist',str(50))
        settings.set('Warping','top-y-dist',str(30))
        settings.set('Warping','bottom-x-dist',str(90))
        settings.set('Warping','bottom-y-dist',str(90))
        settings.add_section("Thresholding")
        settings.set('Thresholding','minTHval',str(152))
        settings.set('Thresholding','maxTHval',str(255))
        settings.set('Thresholding','thinvert',"False")
        settings.add_section("Phase 1")
        settings.set('Phase 1','mode',"hsvS")
        settings.set('Phase 1','invertp1',"False")
        settings.set('Phase 1','p1combine','False')
        settings.set('Phase 1','p1combine1' , 'rgbG')
        settings.set('Phase 1','p1combine2','hsvS')
        settings.set('Phase 1','p1combinem','AND')
        save_settings()
#

def save_settings():
    cfgfile = open(settingsFileName,'w')
    settings.write(cfgfile)
    cfgfile.close()
    if(verbosity>0):
        print("Settings saved.")


def getpoints():
    return utilities.getPoints(settings.getint('Warping','top-x-dist'),settings.getint('Warping','top-y-dist'),settings.getint('Warping','bottom-x-dist'),settings.getint('Warping','bottom-y-dist'),w,h)


initsettings()

w = settings.getint('General','op_width')
h = settings.getint('General','op_heigth')


cap = cv2.VideoCapture(settings.get('Input','source'))
#cap = cv2.VideoCapture("Resources/20230129_162107_02.mp4")

#result = cv2.VideoWriter('output.mjpg', cv2.VideoWriter_fourcc(*'MJPG'),25,(w,h))

frameCounter = 0

#points = utilities.getPoints(settings.getint('Warping','top-x-dist'),settings.getint('Warping','top-y-dist'),settings.getint('Warping','bottom-x-dist'),settings.getint('Warping','bottom-y-dist'),w,h)
points = getpoints()
if(verbosity>2):
    print(points)
lasttime = time.time()
curveList = []
avgVal = 10

def detectlane(frame,points,showresult=True):
    frame = cv2.resize(frame,[w,h])
    
    low_b = np.uint8([200,220,200])
    high_b = np.uint8([00,100,00])

    imgray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    #cv2.imshow("Frame",hsv)
    brightLAB = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    hsvH,hsvS,hsvV = cv2.split(hsv)
    rgbB,rgbG,rgbR = cv2.split(frame)
    
    # imgray = abs(255-imgray)    
    phase1img = utilities.getphase1(frame,settings.get("Phase 1","mode"),settings.getboolean("Phase 1","invertp1"))

    warp = utilities.warpimg(phase1img,points,320,240)

    imblur = cv2.blur(warp,[15,15])
   
    ret, thresh = cv2.threshold(imblur, settings.getint('Thresholding','minTHval'),settings.getint('Thresholding','maxTHval'), cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15,15))
    morph = cv2.erode(thresh, kernel)
    morph = cv2.dilate(morph, kernel)
    
    if settings.getboolean("Thresholding","thinvert"):
        morph = abs(255-morph)
    if(verbosity>2):
        print(utilities.getcontours(warp))
    #cv2.imshow("Blur",morph)
    i=0
    for point in points:
        i+=1
        cv2.circle(frame,point,5,(0,0,255),-1)
        #cv2.putText(frame,str(i),point,cv2.FONT_HERSHEY_COMPLEX,2,(255,255,255),1)    
    
        
        
    
    midpoint, imgHistbottom = utilities.getHistogram(morph,minPer=0.5,display=False,region=4)
    basepoint, imgHist = utilities.getHistogram(morph,minPer=0.9,display=False,region=1)
    curveRaw = basepoint-midpoint
    curveList.append(curveRaw)
    if len(curveList) > avgVal:
        curveList.pop(0)
    curveAvg = np.average(curveList)
    
    
    curtime = time.time()
    fps = 1/(curtime-lasttime)
    # print(fps)
    x=int(utilities.map(int(fps),0,60,0,w))
    if x> w:
        x=w
    
   
    # print(f"curveraw: ",curveRaw)
   
    try:
        if(hasGui):
            cv2.circle(frame, (int(utilities.map(curveAvg,100,-100,0,w)),h-20), 7, (0,255,0), -1)
            # cv2.circle(frame, (int(utilities.map(basepoint,100,-100,0,w)),h-10), 7, (0,255,0), -1)
            cv2.line(frame,(int(w/2),h),(int(w/2),h-50),(200,200,200),2)
            cv2.rectangle(frame,[0,5],[utilities.getCurframe_x(frameCounter,maxframes,w),10],[0,255,0],-1)
            cv2.rectangle(frame,[0,0],[x,5],[0,255,0],-1)
    except:
        print("ups")
    wsutils.imgFrame = frame
    wsutils.imgWarp = warp
    wsutils.imgHist = imgHist
    wsutils.rgbR = rgbR
    wsutils.rgbG = rgbG
    wsutils.rgbB = rgbB
    wsutils.hsvH = hsvH
    wsutils.hsvS = hsvS
    wsutils.hsvV = hsvV
    wsutils.morphimg = morph
    wsutils.blurimg = imblur
    wsutils.thresholdimg = thresh

    
    
    for command in wsutils.CMDS:
        if(verbosity>2):
            print(command)
        if command == "init":
            settingsgroups = settings.sections()
            # print(settingsgroups)
            for group in settingsgroups:
                wsutils.PUBSUB.append(wsutils.getsettingsgrpjson(group))
                for item in settings[group]:
                    if group == "warp":
                        itemtype="range"
                    else:
                        itemtype="text"

                    wsutils.PUBSUB.append(wsutils.getsettingsitemjson(item,group,settings.get(group,item),type=itemtype))
        elif command == "save":
            save_settings()
                    
        else:
            if(command['item']=="p1select"):
                settings.set("Phase 1","mode",str(command['value']))
            if(command['item']=="top-x-dist"):
                settings.set('Warping','top-x-dist',str(command['value']))
                points = getpoints()
            if(command['item']=="top-y-dist"):
                settings.set('Warping','top-y-dist',str(command['value']))
                points = getpoints()
            if(command['item']=="bottom-x-dist"):
                settings.set('Warping','bottom-x-dist',str(command['value']))
                points = getpoints()    
            if(command['item']=="bottom-y-dist"):    
                settings.set('Warping','bottom-y-dist',str(command['value']))   
                points = getpoints()
            if(command['item']=="invertp1"):
                settings.set("Phase 1","invertp1",str(command['value']))
            if(command['item']=="minthval"):
                settings.set("Thresholding",'minThval',str(command['value']))#
            if(command['item']=="maxthval"):
                settings.set("Thresholding",'maxThval',str(command['value']))
            if(command['item']=="thinvert"):
                settings.set("Thresholding",'thinvert',str(command['value']))
    wsutils.CMDS.clear()
    if showresult:
        hists = np.concatenate((imgHistbottom, imgHist), axis=1)
        oneimg = np.concatenate((frame, hists), axis=0)
        if(hasGui):
          cv2.imshow("Final",oneimg)
        #cv2.imshow("Frame",frame)
        # result.write(frame)
        #cv2.imshow("hist",hists)
    return curveAvg,frame

    


if __name__ == "__main__":
  if(hasOutput):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640,480))

  initsettings()
  points = getpoints()
  mydetector = detector.lanedetector()
  while True:
    frameCounter += 1
    maxframes = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if maxframes == frameCounter:
        cap.set(cv2.CAP_PROP_POS_FRAMES,0)
        frameCounter = 0
    retok, frame = cap.read()
    if not retok:
        break

    xdist , img = detectlane(frame,points)
    if(hasOutput):
      out.write(img)
    lasttime=time.time()    
    if cv2.waitKey(1) & 0xff == ord('q'):   # 1 is the time in ms
        cv2.destroyAllWindows()
        save_settings()
        cap.release()
        if(hasOutput):
            out.release()
        sys.exit(0)
        break
  cap.release()
  if(hasOutput):
      out.release()
  #result.release()
  save_settings()
  cv2.destroyAllWindows()
  sys.exit(0)