import base64
from flask import Flask , render_template, Response , request
from camera import Video, API

import cv2
import numpy as np
import requests




app = Flask(__name__)
faceDetect = cv2.CascadeClassifier('haar.xml')

my_video = Video()
api = API()
status = None

# API ROUTE

@app.route('/api/getListEmployee')
def getListEmployee():
    return api.getListEmployee()

@app.route('/api/getEmployeeImage/<employee>')
def getEmployeeImage(employee):
    return api.getEmployeeImage(employee)

@app.route('/api/createEmployeeImage' ,methods=['POST'])
def createEmployeeImage():
    employee = request.form.get('employee')
    filename = request.form.get('filename')
    filedata = request.form.get('filedata')
    return api.createEmployeeImage(employee, filename,filedata)
@app.route('/api/getEmployee/<face_name>')
def getEmployee(face_name):
    return api.getEmployee(face_name)
@app.route('/api/uploadFileAttendanceImage' , methods = ['POST'])
def uploadFileAttendanceImage():
    name = request.form['name']
    base64 = request.form['base64']
    return api.uploadFileAttendanceImage(name, base64)

@app.route('/api/deleteEmployeeImage/<name>' , methods = ['DELETE'])
def deleteEmployeeImage(name):
    return api.deleteEmployeeImage(name)
#



@app.route('/')
def index():
    return render_template('index.html')

def generate(camera):
    while True:
        frame = camera.get_frame() or None
        if(frame == None):
            continue
        get_face(frame)
        yield(b'--frame\r\n'
        b'Content-Type : image/jpeg\r\n\r\n' + frame
        + b'\r\n\r\n')

def bts_to_img(bts):
    buff = np.fromstring(bts, np.uint8)
    buff = buff.reshape(1, -1)
    img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
    return img



def get_face(frame):
    frame = bts_to_img(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces=faceDetect.detectMultiScale(gray,1.3,5)

    centerH = frame.shape[0] // 2
    centerW = frame.shape[1] // 2
    
    sizeboxW = 350
    sizeboxH = 350
    cv2.rectangle(frame, (centerW - sizeboxW // 2, centerH - sizeboxH // 2),
                (centerW + sizeboxW // 2, centerH + sizeboxH // 2), (255, 255, 255), 4)
    # for(x,y,w,h) in faces:
    #     # cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
    #     if ((x >= (centerW - sizeboxW // 2)) and 
    #        (y >= (centerH - sizeboxH // 2)) and 
    #        (x + w <= (centerW + sizeboxW // 2)) and 
    #        (y + h <= (centerH + sizeboxH // 2))):
    #        break
    return faces

@app.route('/video')
def video():
    return Response(generate(my_video),
    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/get_status')
def get_status():
    return {'status' : my_video.getStatus()}

@app.route('/reset')
def reset():
    my_video.resetVideo()
    return {'action' : 'reset'}

@app.route('/submit')
def submit():
   return my_video.submitVideo()
   

if __name__ == "__main__":
    app.run(debug = True)