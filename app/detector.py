import configparser
from os.path import exists
import numpy as np
import cv2


class lanedetector:

    def __init__(self, file="settings.ini",w=640,h=480):
        self.width = w
        self.height = h
        self.detected = False
        self.settingsFileName = file
        self.settings = configparser.ConfigParser()
        print(self.loadsettings(self.settingsFileName))
        self.setPoints(self.settings.getint('Warping','top-x-dist'),
                       self.settings.getint('Warping','top-y-dist'),
                       self.settings.getint('Warping','bottom-x-dist'),
                       self.settings.getint('Warping','bottom-y-dist'))

    def loadsettings(self,file):
        returnval = ""
        if exists(file):
            print("DetectorSettings: file" + self.settingsFileName +" found.")
            self.settingsFilename = file
            try:
                self.settings.read(self.settingsFileName)
                returnval = "DetectorSettings: " + self.settingsFileName +"sucessfully loaded."
            except:
                returnval = "DetectorSettings: " + self.settingsFileName +"loading failed."

            
        else:
            # settings-default
            print("File" + file + " not found. Creating with values." )
            self.settings.add_section("General")
            self.settings.set('General','OP_Width',str(640))
            self.settings.set('General','OP_Heigth',str(480))
            self.settings.add_section('Input')
            self.settings.set('Input','source',"Resources/20230129_162107_02.mp4")
            self.settings.set('Input','rotate',str(0))
            self.settings.set('Input','capture_width',str(640))
            self.settings.set('Input','capture_height',str(480))
            self.settings.set('Input','capture_fps',str(30))
            self.settings.add_section("Warping")
            self.settings.set('Warping','top-x-dist',str(50))
            self.settings.set('Warping','top-y-dist',str(30))
            self.settings.set('Warping','bottom-x-dist',str(90))
            self.settings.set('Warping','bottom-y-dist',str(90))
            self.settings.add_section("Thresholding")
            self.settings.set('Thresholding','minTHval',str(152))
            self.settings.set('Thresholding','maxTHval',str(255))
            self.settings.add_section("Phase 1")
            self.settings.set('Phase 1','mode',"hsvS")
            self.settings.set('Phase 1','invertp1',"False")
            self.settings.set('Phase 1','p1combine','False')
            self.settings.set('Phase 1','p1combine1' , 'rgbG')
            self.settings.set('Phase 1','p1combine2','hsvS')
            self.settings.set('Phase 1','p1combinem','AND')
            self.settings.write(self.settingsFileName)
            returnval="New file ("+file+") created and saved."
        return returnval


    def detectlane():
        return None
    
    def setPoints(self,top_x,top_y,bot_x,bot_y,v=0):
        w=self.width
        h=self.height
        top_ydist = int(self.map(top_y,0,100,0,h))
        bottom_ydist = int(self.map(bot_y,0,100,0,h))

        top_xdist = int(self.map(top_x,0,100,0,w)/2)
        bottom_xdist = int(self.map(bot_x,0,100,0,w)/2)
        p1= [int(w/2-top_xdist+v),top_ydist]
        p2= [int(w/2+top_xdist+v),top_ydist]
        p3= [int(w/2-bottom_xdist+v),bottom_ydist]
        p4= [int(w/2+bottom_xdist+v),bottom_ydist]
        self.points = [p1,p2,p3,p4]

        return self.points
    
    def map(self,x,in_max,in_min,out_max,out_min):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    def intmap(self,x,in_max,in_min,out_max,out_min):
        return int(self.map(x,in_max,in_min,out_max,out_min))
    

    def getHistogram(self,img,minPer=0.1,display=True,region=1):
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
    
    def getPNG(self,img):
        return cv2.imencode(img,"*.png")

    def getJPG(self,img):
        return cv2.imencode(img,"*.jpg")
    
    def getcontours(self,img,drawonimg=True,getnullimg=True):
        if getnullimg:
            outimg = self.getnullimg(img.shape[0],img.shape[1])
        else:
            outimg = img
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        linefound = False
        cx = 555
        cy = 555
        # mask = cv2.inRange(frame, high_b, low_b)
        # contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)
        if len(contours) > 0 :
            linefound = True
            self.detected=True
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
                if drawonimg:
                    cv2.circle(outimg, (cx,cy), 5, (255,255,255), -1)
                    cv2.circle(outimg, (cx,450), 5, (255,255,255), -1)

                if drawonimg:
                    cv2.drawContours(outimg, c, -1, (0,255,128), 1)
            return linefound,cx,cy,self.intmap(cx,img.shape[1],0,100,-100),self.intmap(cy,img.shape[0],0,100,-100),outimg
        else :
            # print("I don't see the line")
            linefound = False
            self.detected = False
        
        
        return linefound,555,555,0,0,img

    def getnullimg(w,h):
            img = np.zeros((w,h,3),np.uint8)
            return img