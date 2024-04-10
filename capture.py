 # -*- coding: utf-8 -*-
import time
import datetime
import cv2 as cv
import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

save_dir  = './'
fn_suffix = 'motion_detect.jpg'
cap = cv.VideoCapture(0) 
cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

DELTA_MAX = 255

DOT_TH = 20

MOTHON_FACTOR_TH = 0.07

avg = None

f_name = 0

while True:

    ret, frame = cap.read()     # 1フレーム読み込む
    motion_detected = False     # 動きが検出されたかどうかを示すフラグ

    dt_now = datetime.datetime.now() #データを取得した時刻

    dt_format_string = dt_now.strftime('%Y-%m-%d %H:%M:%S') 


    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    if avg is None:
        avg = gray.copy().astype("float")
        continue


    cv.accumulateWeighted(gray, avg, 0.6)
    frameDelta = cv.absdiff(gray, cv.convertScaleAbs(avg))

    thresh = cv.threshold(frameDelta, DOT_TH, DELTA_MAX, cv.THRESH_BINARY)[1]

    motion_factor = thresh.sum() * 1.0 / thresh.size / DELTA_MAX 
    motion_factor_str = '{:.08f}'.format(motion_factor)

    cv.putText(frame,dt_format_string,(25,50),cv.FONT_HERSHEY_SIMPLEX, 1.5,(0,0,255), 2)
    cv.putText(frame,motion_factor_str,(25,470),cv.FONT_HERSHEY_SIMPLEX, 1.5,(0,0,255), 2)

    if motion_factor > MOTHON_FACTOR_TH:
        motion_detected = True

    # 動き検出していれば画像を保存する
    if motion_detected  == True:
        #save
        f_name += 1
        filepath = save_dir + '/' + str(f_name) + '.jpg'
        cv.imwrite(filepath, frame)
        print("Detected!")
        with open(filepath, "rb") as f :
            supabase.storage.from_("pictures").upload(file=f, path=filepath, file_options={"content-type": "image/jpeg"})
        os.remove(filepath)

print("Bye!\n")
