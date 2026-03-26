
import streamlit as st
import cv2
import dlib
import numpy as np
import sqlite3
import os
import csv
import pandas as pd
import time
from datetime import datetime
from scipy.spatial import distance

st.set_page_config(page_title="Face Liveness Security System",layout="wide")
st.title("🔐 Face Liveness Security System")

os.makedirs("database",exist_ok=True)
os.makedirs("captured_faces",exist_ok=True)

# ---------------- DATABASE ----------------

def create_db():

    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    roll TEXT,
    image_path TEXT,
    embedding BLOB)
    """)

    # check roll column
    cur.execute("PRAGMA table_info(users)")
    columns=[c[1] for c in cur.fetchall()]

    if "roll" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN roll TEXT")

    conn.commit()
    conn.close()

create_db()


def insert_user(name,roll,path,embedding):

    conn=sqlite3.connect("database/database.db")
    cur=conn.cursor()

    cur.execute(
    "INSERT OR IGNORE INTO users(name,roll,image_path,embedding) VALUES (?,?,?,?)",
    (name,roll,path,embedding.tobytes())
    )

    conn.commit()
    conn.close()


def get_users():

    conn=sqlite3.connect("database/database.db")
    cur=conn.cursor()

    cur.execute("SELECT name,roll,image_path,embedding FROM users")

    rows=cur.fetchall()
    conn.close()

    users=[]

    for name,roll,path,emb in rows:

        emb=np.frombuffer(emb,dtype=np.float64)
        users.append((name,roll,path,emb))

    return users


# ---------------- RESET SYSTEM ----------------

if st.sidebar.button("⚠ Reset All Data"):

    if os.path.exists("database/database.db"):
        os.remove("database/database.db")

    for f in os.listdir("captured_faces"):
        os.remove(f"captured_faces/{f}")

    if os.path.exists("attendance.csv"):
        os.remove("attendance.csv")

    create_db()

    st.sidebar.success("System reset successfully")


# ---------------- ATTENDANCE ----------------

def mark_attendance(name,roll):

    file="attendance.csv"

    today=datetime.now().strftime("%Y-%m-%d")
    now=datetime.now().strftime("%H:%M:%S")

    if not os.path.exists(file):

        with open(file,"w",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["Date","Time","Name","Roll"])

    with open(file,"r") as f:
        rows=list(csv.reader(f))

    for row in rows[1:]:

        if row[0]==today and row[2]==name:
            return

    with open(file,"a",newline="") as f:

        writer=csv.writer(f)
        writer.writerow([today,now,name,roll])


# ---------------- SPOOF DETECTION ----------------

def detect_screen_spoof(face_img):

    gray=cv2.cvtColor(face_img,cv2.COLOR_BGR2GRAY)
    lap=cv2.Laplacian(gray,cv2.CV_64F)

    return lap.var()


# ---------------- MODELS ----------------

detector=dlib.get_frontal_face_detector()

predictor=dlib.shape_predictor(
"models/shape_predictor_68_face_landmarks.dat")

face_model=dlib.face_recognition_model_v1(
"models/dlib_face_recognition_resnet_model_v1.dat")

LEFT=list(range(42,48))
RIGHT=list(range(36,42))


def eye_ratio(eye):

    A=distance.euclidean(eye[1],eye[5])
    B=distance.euclidean(eye[2],eye[4])
    C=distance.euclidean(eye[0],eye[3])

    return (A+B)/(2*C)


# ---------------- MENU ----------------

menu=st.sidebar.selectbox(
"Navigation",
["Enroll User","Authenticate","Attendance Dashboard","Registered Users"]
)

# ---------------- ENROLL ----------------

if menu=="Enroll User":

    st.subheader("User Enrollment")

    username=st.text_input("Enter Name")
    roll=st.text_input("Enter Roll Number")

    start=st.button("Start Camera")

    frame_window=st.image([])

    if start:

        cap=cv2.VideoCapture(0)

        blink_counter=0
        saved=False

        while True:

            ret,frame=cap.read()

            if not ret:
                break

            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            faces=detector(gray)

            for face in faces:

                shape=predictor(gray,face)

                points=np.array([[p.x,p.y] for p in shape.parts()])

                ear=(eye_ratio(points[LEFT])+eye_ratio(points[RIGHT]))/2

                face_img=frame[face.top():face.bottom(),face.left():face.right()]

                if ear<0.25:
                    blink_counter+=1

                if blink_counter>2 and username and roll and not saved:

                    path=f"captured_faces/{username}.jpg"

                    cv2.imwrite(path,face_img)

                    embedding=np.array(
                    face_model.compute_face_descriptor(frame,shape)
                    )

                    insert_user(username,roll,path,embedding)

                    saved=True

                    st.success("User enrolled successfully")

            frame_window.image(frame,channels="BGR")

            if saved:
                break

        cap.release()


# ---------------- AUTHENTICATE ----------------

elif menu=="Authenticate":

    st.subheader("Authentication")

    start=st.button("Start Camera")

    frame_window=st.image([])

    users=get_users()

    if start:

        cap=cv2.VideoCapture(0)

        frame_id=0
        prev_x=None
        blink_counter=0
        movement=False
        authenticated=False

        while True:

            ret,frame=cap.read()

            if not ret:
                break

            frame_id+=1

            small=cv2.resize(frame,(0,0),fx=0.4,fy=0.4)
            gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)

            faces=detector(gray)

            for face in faces:

                x1=int(face.left()/0.4)
                y1=int(face.top()/0.4)
                x2=int(face.right()/0.4)
                y2=int(face.bottom()/0.4)

                if authenticated:

                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                    frame_window.image(frame,channels="BGR")
                    continue

                shape=predictor(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),
                                dlib.rectangle(x1,y1,x2,y2))

                points=np.array([[p.x,p.y] for p in shape.parts()])

                ear=(eye_ratio(points[LEFT])+eye_ratio(points[RIGHT]))/2

                face_img=frame[y1:y2,x1:x2]

                if face_img.size==0:
                    continue

                texture=detect_screen_spoof(face_img)

                if texture>120:

                    cv2.putText(frame,"SCREEN SPOOF",
                    (30,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,0,255),2)

                    continue

                current_x=x1

                if prev_x is not None:

                    if abs(current_x-prev_x)>15:
                        movement=True

                prev_x=current_x

                if ear<0.25:
                    blink_counter+=1

                if frame_id % 5 != 0:
                    continue

                embedding=np.array(
                face_model.compute_face_descriptor(frame,shape)
                )

                best_match=None
                best_dist=1.0
                best_roll=None

                for name,roll,path,emb in users:

                    dist=np.linalg.norm(embedding-emb)

                    if dist<best_dist:

                        best_dist=dist
                        best_match=name
                        best_roll=roll

                if blink_counter>2 and movement and best_dist<0.48:

                    authenticated=True

                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

                    cv2.putText(frame,f"{best_match} ({best_roll})",
                    (x1,y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,255,0),2)

                    st.success(f"Access Granted : {best_match} ({best_roll})")

                    mark_attendance(best_match,best_roll)

                else:

                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)

                    cv2.putText(frame,"Unknown",
                    (x1,y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,0,255),2)

            frame_window.image(frame,channels="BGR")

        cap.release()


# ---------------- DASHBOARD ----------------

elif menu=="Attendance Dashboard":

    st.subheader("Attendance Dashboard")

    if os.path.exists("attendance.csv"):

        df=pd.read_csv("attendance.csv")

        st.dataframe(df)

        if st.button("Export Excel"):

            df.to_excel("attendance_report.xlsx",index=False)

            st.success("Excel exported")

    else:

        st.info("No attendance records yet.")


# ---------------- REGISTERED USERS ----------------

elif menu=="Registered Users":

    st.subheader("Registered Users")

    users=get_users()

    if len(users)==0:

        st.info("No users registered.")

    else:

        data=[[u[0],u[1]] for u in users]

        st.table(pd.DataFrame(data,columns=["Name","Roll Number"]))