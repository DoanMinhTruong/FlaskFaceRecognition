from datetime import datetime
from email import header
from re import S
from urllib import request
import cv2
import requests
import base64
faceDetect = cv2.CascadeClassifier('haar.xml')

class API():
    def __init__(self):
        self.AUTH = {"Authorization" : "token 2850d97206bd945:b8fca0ea4c894da"}
        self.URL = "http://testphanquyen.drabiz.net:8000"
    def getListEmployee(self):
        response = requests.get(url = self.URL + '/api/resource/Employee?fields=["name","employee_name"]' , headers=self.AUTH )
        return response.json()
    def getEmployeeImage(self , employee):
        response = requests.get(url = self.URL 
        + '/api/resource/Employee Image?fields=["*"]&filters=[["employee","=","'+employee+'"]]&order_by=creation' ,
        headers = self.AUTH
         )
        return response.json()
    def createEmployeeImage(self, employee, filename ,filedata):
        response = requests.post(url = self.URL 
        + '/api/resource/Employee Image' ,
        headers = self.AUTH , json = {'employee' : employee})
        if(response.ok):
            data = response.json()
            print(data)
            response2 = requests.post(url=self.URL + '/api/method/uploadfile/', headers=self.AUTH,
            data = {'cmd' : 'uploadfile',
              'doctype'  : 'Employee Image', 
              'docname' : data['data']['name'],
              'filename' : filename,
              'filedata' : filedata ,
              'from_form' : 1})
            if(response2.ok):
                data2 = response2.json()
                print(data2)
                response3 = requests.put(url = self.URL + "/api/resource/Employee Image/" + data['data']['name'],
                headers=self.AUTH , 
                json = {"image" : data2['message']['file_url']},
                )
                return response3.json()
            return response2.json()
        return response.json()
    def getEmployee(self, face_name) :
        response = requests.get(url = self.URL + '/api/resource/Employee?fields=["*"]&filters=[["name","=","'+face_name+'"]]' , headers=self.AUTH)
        return (response.json())['data'][0]
    def uploadFileAttendanceImage(self, name , base64):
        response = requests.post(url = (self.URL + '/api/method/uploadfile/'),
        data = {'cmd' : 'uploadfile' , 'doctype' : 'Attendance Image' , 
        'docname' : name, 'filename' : (name + '.jpg'),
        'filedata' : base64 , 'from_form' : 1
        } , headers= self.AUTH
        )
        if(response.ok):
            data2 = response.json()
            response2 = requests.put(url = self.URL + '/api/resource/Attendance Image/' + name,
            headers=self.AUTH, json={'image' : data2['message']['file_url']}
            )
            return response2.json()
        return response.json()
    def deleteEmployeeImage(self , name):
        response = requests.delete(url = self.URL + '/api/resource/Employee Image/' + name , headers=self.AUTH)
        return response.json()
class Video(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.save_jpg = None
        self.queue = []
        self.has_face = None
        self.URL = "http://testphanquyen.drabiz.net:8000"
        self.AUTH = {'Authorization' : "token 2850d97206bd945:b8fca0ea4c894da" , 'accept': 'application/json'}

    def __del__(self):
        self.video.release()
    def get_frame(self):
        try:
            ret , frame = self.video.read()

            if(self.has_face):
                return (cv2.imencode('.jpg' , self.save_jpg)[1]).tobytes()
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
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                # crop_flip = cv2.flip(crop,1)
                retval, buffer = cv2.imencode('.jpg', crop)
                jpg_as_text = base64.b64encode(buffer)
                response = requests.post(url = self.URL + '/api/method/erpnext.hr.doctype.employee_image.employee_image.detect',
                headers=self.AUTH , data={'cv_img' : jpg_as_text})
                if(not response.ok):
                    break
                face_location , face_name = (response.json()['message'])
                print(face_name)
                if(len(self.queue) <= 3):
                    self.queue.append(face_name)
                    break
                if(len(self.queue) == 4 ):
                    if self.queue[0] != [] and self.queue[0] != ['Unknown'] and (all((x==self.queue[0]) for x in self.queue)):
                        self.has_face = face_name[0]
                        self.save_jpg = frame
                    self.queue.pop(0)
                else:
                    self.queue.pop(0)
            ret , jpg = cv2.imencode('.jpg' , frame)
            return jpg.tobytes()
        except:
            pass
    def getStatus(self):
        return self.has_face

    

    def resetVideo(self):
        self.save_jpg = None
        self.queue = []
        self.has_face = None
    from datetime import datetime
    def submitVideo(self):
        curDT = datetime.now()
        date_time = curDT.strftime("%Y/%m/%d, %H:%M:%S")
        response = requests.post(url = self.URL + "/api/resource/Attendance Image" , 
        headers=self.AUTH, 
        json = {"employee" : self.has_face})
        self.resetVideo()
        return response.json()

