import os
import time
from datetime import date
import shutil

def folder_control():
    path = "/home/pi/AuDD/5_Photos/"  # replace with real path to photo folder
    
    my_date = date.today().weekday() # weekday 0 - monday, 6 - sunday
    if my_date == 0 or my_date == 1:
        days = 6
    else:
        days = 3
    seconds = time.time() - (days * 24 * 60 * 60)  # calculate time that was days ago
    
    ### remove all dir older then 2 work week days. Except Semples
    dir_list = os.listdir(path)

    if len(dir_list) > 0:
        try:
            dir_list.remove("Samples")
        except:
            pass

        for dirs in dir_list:
            if seconds > os.stat(path+dirs).st_ctime:
                shutil.rmtree(path+dirs)
                #os.rmdir(path+dirs)          
                
    ####  Create a folder with today name (YYYY-MM-DD), except weekends
    try:
        if str(date.today()) not in os.listdir(path) and my_date < 5:
            os.umask(0)
            os.mkdir(path+str(date.today()), mode=0o777)
    except:
        pass

folder_control()