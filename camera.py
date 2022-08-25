from re import S
from urllib import request
import cv2
import requests
import base64
faceDetect = cv2.CascadeClassifier('haar.xml')
class Video(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.save_jpg = None
        self.queue = []
        self.has_face = None
    def __del__(self):
        self.video.release()
    def get_frame(self):
        if(self.has_face):
            return (cv2.imencode('.jpg' , self.save_jpg)[1]).tobytes()
        ret , frame = self.video.read()
        frame = cv2.flip(frame , 1)
        centerH = frame.shape[0] // 2
        centerW = frame.shape[1] // 2
        
        sizeboxW = 350
        sizeboxH = 350
        cv2.rectangle(frame, (centerW - sizeboxW // 2, centerH - sizeboxH // 2),
                    (centerW + sizeboxW // 2, centerH + sizeboxH // 2), (255, 255, 255), 4)
        
        gray = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)
        faces = faceDetect.detectMultiScale(gray, 1.3 , 5 )
        for (x,y,w,h) in faces:
            crop = gray[y:y+h , x: x+w]
            # crop_flip = cv2.flip(crop,1)
            retval, buffer = cv2.imencode('.jpg', crop)
            jpg_as_text = base64.b64encode(buffer)
            response = requests.post(url = 'http://testphanquyen.drabiz.net:8000/api/method/erpnext.hr.doctype.employee_image.employee_image.detect',
            headers={'Authorization' : "token 2850d97206bd945:b8fca0ea4c894da" , 'accept': 'application/json'} , data={'cv_img' : jpg_as_text})
            face_location , face_name = (response.json()['message'])
            print(face_name)
            if(len(self.queue) <= 4):
                self.queue.append(face_name)
                break
            if(len(self.queue) == 5 ):
                if self.queue[0] != [] and self.queue[0] != ['Unknown'] and (all((x==self.queue[0]) for x in self.queue)):
                    self.has_face = face_name[0]
                    self.save_jpg = frame
                self.queue.pop(0)
            else:
                self.queue.pop(0)
        ret , jpg = cv2.imencode('.jpg' , frame)
        return jpg.tobytes()
    
    def getStatus(self):
        return self.has_face

    

    def resetVideo(self):
        self.save_jpg = None
        self.queue = []
        self.has_face = None

    def submitVideo(self):
        response = requests.post(url = "http://testphanquyen.drabiz.net:8000/api/resource/Attendance Image" , 
        headers={'Authorization' : "token 2850d97206bd945:b8fca0ea4c894da" , 'accept': 'application/json'}, 
        json = {"employee" : self.has_face})
        self.resetVideo()
        return response.json()

