import numpy as np
import cv2
import time
from datetime import date
import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
import traceback
import os

# import find_defect
# from multiprocessing import Process, Queue


# get formated time and date for logging
def get_date():
    line = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    return line
    
def image_from_video(command, sampling):

    w,h  = 1648, 1232    # camera resolution.  Ratio 1.77
    ww, wh = 650, 296    # for window size adjustment and image resize
    s = 5      # s-th frame will be save after cross the thresh_up
    nn = 2     # diff will be calculated for each nn-th frame

    camera = PiCamera()
    camera.resolution = (w, h)    # Original camera modul resolution  4056, 3040
    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size=(w, h))

    thresh_up = 24000000   # Diff between empty line and CB. Lower thresh less diff counts like a motion
    thresh_low = 6000000  # Diff between empty line and empty line
    frame_cut_up = 300     # Cut frame for thresh calculating to save up some time
    frame_cut_low = 500
    prefix =   "/home/pi/AuDD/5_Photos/" + str(date.today()) + '/'  # For image name

    try:
        os.chmod('/home/pi/AuDD/log.txt', 0o777)
        f = open('/home/pi/AuDD/log.txt', 'a')
        f.write(get_date() + " Photo making started.\n")
        f.close()
    except:
        pass
    
    if command == "start":
        template = cv2.imread('/home/pi/AuDD/3_Templates/1.jpg')
        #template = cv2.imread('/home/pi/AuDD/3_Templates/Empty_line1.jpg')
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.GaussianBlur(template, (3, 3), 0)
        t_cut = template[frame_cut_up:frame_cut_low, :]
        t_thresh = cv2.threshold(t_cut, 25, 255, cv2.THRESH_BINARY)[1]
        
#         q = Queue()
#         p = Process(target=find_defect.image_check, args=(q, sampling))
#         p.start()

        shot = 0  # Counters and switch
        n = 0
        n0 = 0
        
        while datetime.datetime.now().time() < datetime.time(16, 45, 0):
            try:
                for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                    if datetime.datetime.now().time() < datetime.time(16, 45, 0):
                        img = frame.array
                        img = img[420:1170,:]
                        img_res = cv2.resize(img, (ww, wh), interpolation = cv2.INTER_CUBIC)
                        rawCapture.truncate(0)
                        n += 1
                        
                        if n % nn == 0:  # check each n-th frame
                            next_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            next_frame = cv2.GaussianBlur(next_frame, (3, 3), 0)
                            n_cut = next_frame[frame_cut_up:frame_cut_low, :]
                            n_thresh = cv2.threshold(n_cut, 25, 255, cv2.THRESH_BINARY)[1]
                            frameDelta = cv2.absdiff(t_thresh, n_thresh)
                            summ = np.sum(frameDelta)
                            n = 0
#                             print(summ)
                            if summ > thresh_up and shot == 0:
                                n0 += 1
                                
                                if n0 == s:  # n value have to be ajusted to stream video or use sleep
                                    time.sleep(3.5)
                                    timer = time.strftime("%H_%M", time.localtime())
                                    name = prefix +str(timer)+".jpg"
                                    cv2.imwrite(name, img)
                            
        #                             img_to_check = cv2.imread("Block on line with DFx2 crop.jpg")  # For test. Change to img
        #                             q.put(img_to_check)
        #                             if not p.is_alive():
        #                                 p = Process(target=find_defect.image_check, args=(q, sampling))
        #                                 p.start()

                                    shot = 1
                            if summ < thresh_low and shot == 1:
                                shot = 0
                                n0 = 0
                    else:
                        rawCapture.truncate(0)
                        finish, error = True, False
                        return finish, error
                        break
            except:
                rawCapture.truncate(0)
                camera.close()
                time.sleep(2)
                finish, error = False, True
                with open('/home/pi/AuDD/log.txt', 'a') as f:
                    f.write(get_date() + " ERROR making photo (Get_image_from_video): \n")
                    f.write(traceback.format_exc())
                return finish, error  
                break
                
# if __name__ == "__main__":
#image_from_video("start", "sampling")
