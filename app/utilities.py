import cv2
import numpy as np

def warpimg(img,points,w,h,invert=False):
    pts1 = np.float32(points)
    pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]])
    if invert:
        matrix = cv2.getPerspectiveTransform(pts2,pts1)
    else:
        matrix = cv2.getPerspectiveTransform(pts1,pts2)
    
    imgWarp = cv2.warpPerspective(img,matrix,(w,h))
    #imgWarp = cv2.flip(imgWarp,0)
    return imgWarp

def getCurframe_x(frame,maxframes,w):
    x = frame  * w / maxframes 
    return int(x)

def map(x,in_max,in_min,out_max,out_min):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def getPoints(top_x,top_y,bot_x,bot_y,w,h,v=0):
    top_ydist = int(map(top_y,0,100,0,h))
    bottom_ydist = int(map(bot_y,0,100,0,h))

    top_xdist = int(map(top_x,0,100,0,w)/2)
    bottom_xdist = int(map(bot_x,0,100,0,w)/2)
    p1= [int(w/2-top_xdist+v),top_ydist]
    p2= [int(w/2+top_xdist+v),top_ydist]
    p3= [int(w/2+bottom_xdist+v),bottom_ydist]
    p4= [int(w/2-bottom_xdist+v),bottom_ydist]
    points = [p1,p2,p4,p3]

    return points

def getHistogram(img,minPer=0.1,display=True,region=1):
    """getHistogram _summary_

    _extended_summary_

    Args:
        img (_type_): _description_
        minPer (float, optional): _description_. Defaults to 0.1.
        display (bool, optional): _description_. Defaults to True.
        region (int, optional): _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """
    if region == 1:
        histValues = np.sum(img,axis=0)
    else:
        histValues = np.sum(img[int(img.shape[0]/region):,:],axis=0)
  
    maxValue = np.max(histValues)
    minValue = minPer * maxValue
    indexArray = np.where(histValues >= minValue)
    basePoint = int(np.average(indexArray))

    imgHist = np.zeros((img.shape[0],img.shape[1],3),np.uint8)
    for x, intensity in enumerate(histValues):
        cv2.line(imgHist,(x,img.shape[0]),(x,img.shape[0]-int((intensity/255/region))),(255,0,255),1)
    cv2.circle(imgHist,(basePoint,img.shape[0]),10,(0,255,255),cv2.FILLED)
    basePoint = int(map(basePoint,img.shape[0]/2,-img.shape[0]/2,100,-100))

    return basePoint,imgHist

def getphase1(img,mode,invert=False):
    if "hsv" in mode:
        hsvimg = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        himg,simg,vimg = cv2.split(hsvimg)
        if mode == "hsvH":
            retimg = himg
        elif mode == "hsvS":
            retimg = simg
        elif mode == "hsvV":
            retimg = vimg
    if "rgb" in mode:
        bimg,gimg,rimg = cv2.split(img)
        if mode == "rgbR":
            retimg = rimg
        elif mode == "rgbG":
            retimg = gimg
        elif mode == "rgbB":
            retimg = bimg
    if  invert == True:
        retimg = abs(255-retimg)
    return retimg            

def getcontours(img):    
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    linefound = False
    cx = 555
    cy = 555
    # mask = cv2.inRange(frame, high_b, low_b)
    # contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
    if len(contours) > 0 :
        linefound = True
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] !=0 :
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            #print("CX : "+str(cx)+"  CY : "+str(cy))
            if cx >= 340 :
                # print("Turn Right")
                rightarr = True
            if cx < 340 and cx > 300 :
                print("On Track!")

            if cx <=300 :
                # print("Turn Left")
                leftarr = True
            cv2.circle(img, (cx,cy), 5, (255,255,255), -1)
            cv2.circle(img, (cx,450), 5, (255,255,255), -1)
            #cv2.drawContours(warp, c, -1, (0,255,128), 1)
    else :
        # print("I don't see the line")
        i=0
    
    return linefound,cx,cy,int(map(cx,img.shape[1],0,100,-100)),int(map(cy,img.shape[0],0,100,-100))