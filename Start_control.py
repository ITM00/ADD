import time
import datetime
import traceback
import os

import Folder_control
import Get_image_from_video_3



def get_date():
    line = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    return line

path = "/home/pi/AuDD/5_Photos/"
folders_list = os.listdir(path)
current_date = str(datetime.date.today())

start = datetime.time(7, 39, 0)
end = datetime.time(16, 45, 0)
current = datetime.datetime.now().time()

# Check if folder creation needed
if datetime.date.today().weekday() < 5 and current_date not in folders_list:
    
    Folder_control.folder_control()

# Check if it's proper time for Get_image_from_vide to work
# And save to log.txt when finished.
while datetime.date.today().weekday() < 5 and start <= current <= end:
    try:
        finish, error = Get_image_from_video_3.image_from_video("start", "sampling")
    except:
        os.chmod('/home/pi/AuDD/log.txt', 0o777)
        f = open('/home/pi/AuDD/log.txt', 'a')
        f.write(get_date() + " ERROR making photo (Start_control): \n")
        f.write(traceback.format_exc())
        f.close()
        time.sleep(2)
        continue
        
    if error:
        time.sleep(2)
        error = False
        continue
        
    if finish:
        os.chmod('/home/pi/AuDD/log.txt', 0o777)
        f = open('/home/pi/AuDD/log.txt', 'a')
        f.write(get_date() + " Get_image retirned finish.\n")
        f.close()
        break
     
photos_quantity = len(os.listdir(path + str(datetime.date.today())))
os.chmod('/home/pi/AuDD/log.txt', 0o777)
f = open('/home/pi/AuDD/log.txt', 'a')
f.write(get_date() + " Photo making finished. " + str(photos_quantity) + " photos were made.\n")
f.write("\n")
f.close()
    
