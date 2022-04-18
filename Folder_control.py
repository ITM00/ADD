import os
import time
import datetime
import shutil
import traceback

def get_date():
    line = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    return line

def folder_control():
    path = "/home/pi/AuDD/5_Photos/"  # replace with real path to photo folder
    
    my_date = datetime.date.today().weekday() # weekday 0 - monday, 6 - sunday
    if my_date == 0 or my_date == 1:
        days = 6
    else:
        days = 3
    seconds = time.time() - (days * 24 * 60 * 60)  # calculate time that was "days" ago
    
    ### Remove all dir older then 2 work week days. Except Samples
    dir_list = os.listdir(path)
    os.chmod('/home/pi/AuDD/log.txt', 0o777)
    with open('/home/pi/AuDD/log.txt', 'a') as f:
        
        if len(dir_list) > 0:
            try:
                dir_list.remove("Samples")
            except:
                pass

            for dirs in dir_list:
                if seconds > os.stat(path+dirs).st_ctime:
                    try:
                        shutil.rmtree(path+dirs)
                        f.write(get_date() + " folder " + str(dirs) + " was deleted\n")
                    except:
                        f.write(get_date() + " ERROR during folder deletion: \n")
                        f.write(traceback.format_exc())
                        pass
                    
        ####  Create a folder with today name (YYYY-MM-DD), except weekends
        try:
            if str(datetime.date.today()) not in os.listdir(path) and my_date < 5:
                os.umask(0)
                os.mkdir(path+str(datetime.date.today()), mode=0o777)
                f.write(get_date() + " folder " + str(datetime.date.today()) + " was created\n")
        except:
            f.write(get_date() + " ERROR during folder creation: \n")
            f.write(traceback.format_exc())
            pass
