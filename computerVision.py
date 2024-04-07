import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

# مقطع الفيديو أو كاميرا الويب
cap = cv2.VideoCapture(0)

# تهيئة Mediapipe instance
with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
 
)as pose:
####################### 1 ####################################
   counter = 0  # المتغير لتتبع العداد
   hand = 'left'  # افتراضيًا، سيتم تتبع اليد اليسرى
   stage=None
   while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("لا يمكن قراءة الإطار، قد يكون هناك خطأ في الكاميرا.")
            break

        # تحويل الصورة إلى RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # كشف الموقع
        results = pose.process(image)

        # استعادة الألوان لتنسيق BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # استخراج النقاط البارزة
        try:
            landmarks = results.pose_landmarks.landmark
            
            # التحقق من اليد المراد تتبعها
            if hand == 'left':
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            else:
                shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # حساب الزاوية
            angle = calculate_angle(shoulder, elbow, wrist)
            cv2.putText(image, str(angle), tuple(np.multiply(elbow, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            # التحقق من الزاوية وزيادة العداد
            if angle > 160:
                stage = "down"
            if angle < 30 and stage =='down':
                stage="up"
                counter +=1
                print(counter)

        ####################################### 2 ###################################
        except Exception as e:
            print("wrong in detect boints", e)

        # رسم النقاط والاتصالات
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))


        # عرض العداد
        cv2.putText(image, 'To Close Camera  Click [Q]', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.rectangle(image, (100,0), (300,100), (0,255,0), -1)
        # عرض زر التحديد بين اليد اليسرى واليمنى
        cv2.putText(image, 'choose hand [L] left- [R] right ', (0, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Rep data
        cv2.putText(image, str(counter), 
                    (110,50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
        # Stage data
        cv2.putText(image, stage, 
                    (110,90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)

        # عرض الإطار
        cv2.imshow('Mediapipe Feed', image)

        # الخروج عند الضغط على 'q'
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

        # تحديد اليد المراد تتبعها
        key = cv2.waitKey(1)
        if key & 0xFF == ord('l'):  # اختيار اليد اليسرى
            hand = 'left'
            counter=0
        elif key & 0xFF == ord('r'):  # اختيار اليد اليمنى
            hand = 'right'
            counter=0
#####################################################3######################
    # إغلاق الكاميرا وت