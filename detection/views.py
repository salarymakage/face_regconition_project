from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
import cv2
import sqlite3
import logging

logger = logging.getLogger(__name__)

camera = None
detected_student = None

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        if not self.video.isOpened():
            logger.error("Failed to open camera")
        self.facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        try:
            self.recognizer.read('trainer.yml')
        except cv2.error as e:
            logger.error(f"Error loading recognizer: {e}")
        
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, img = self.video.read()
        if not success:
            logger.error("Failed to capture frame")
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.facedetect.detectMultiScale(gray, 1.3, 5) 

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, conf = self.recognizer.predict(gray[y:y + h, x:x + w])
            profile = self.getprofile(id)
            
            if profile:
                global detected_student
                detected_student = profile
                text = f"ID: {profile[0]} - Name: {profile[1]} {profile[2]}"
                cv2.putText(img, text, (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', img)
        if not ret:
            logger.error("Failed to encode frame to JPEG")
            return None
        
        return jpeg.tobytes()

    @staticmethod
    def getprofile(id):
        """Retrieve user profile by ID from the database."""
        try:
            conn = sqlite3.connect("sqlite.db")
            cursor = conn.execute("SELECT * FROM STUDENTS WHERE id=?", (id,))
            profile = cursor.fetchone()
            return profile
        finally:
            conn.close()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    global camera
    if camera is None:
        camera = VideoCamera()
    return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')

def stop_camera(request):
    global camera
    if camera is not None:
        del camera
        camera = None
    return redirect('index')

def index(request):
    global detected_student
    conn = sqlite3.connect("sqlite.db")
    cursor = conn.execute("SELECT * FROM STUDENTS")
    students = cursor.fetchall()
    conn.close()
    return render(request, 'detection/index.html', {'students': students, 'detected_student': detected_student})

def detected_student_info(request):
    global detected_student
    if detected_student:
        return JsonResponse({
            'id': detected_student[0],
            'first_name': detected_student[1],
            'last_name': detected_student[2],
            'gender': detected_student[3],
            'medical_condition': detected_student[4],
            'address': detected_student[5],
            'emergency_contact': detected_student[6],
        })
    return JsonResponse({'Error': 'No student detected'}, status=404)

def student_list(request):
    global detected_student
    conn = sqlite3.connect("sqlite.db")
    cursor = conn.execute("SELECT id, FirstName, LastName, Gender, MedicalCondition, Address FROM STUDENTS")
    students = cursor.fetchall()
    conn.close()
    return JsonResponse({'students': students, 'detected_student': detected_student})

def main_page(request):
    return render(request, 'detection/main.html')
