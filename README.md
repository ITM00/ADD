# ADD
Automated Defect Detection

This project is for automated defect detection on upper mating surface of cylinder block(CB) for engine assembling production. 
This is privet project so no examples, images or photos will be present. It's a trade secret.
All algorithmes will work on Ruspberry PI4B + HQ Raspberry camera module 16mm.

First part is just making photo on event (CB moves under camera). Already tested, workes well. If you will use it for your purpose some
constants and thresholdes have to be adjusted. 

Start_control.py is for run Folder_control and then Get_image_from_video_3 in proper time and day of a week. And wathcing for errors. 
If error restart Get_image_from_video_3 if it can't handel this by it's own.

Get_image_from_video_3.py finds differance between template image of empty assembling line and current frame from video srtream.
If differance is greater then threash_up then wait for some frames (s - value in code).
To decrease computantional cost differnt between template and frame calculates only each nn-th frame (nn - value). nn = 2 in my case.
And more it calculates differnace not for whole frame but just for small part of it as I know where the motion appers each time.
farme_cut_up & farme_cut_low determine area of frame for differance culculation.

Multiprocessing is needed for run second algorith (Find_defect.py) and keep making shots of CBs at the same time.

Folder_control.py is used for creation and deletion folders for images saving daily based by crontab. (Tested, works)
It creates folder with current date as a name in format YYYY-MM-DD and delete folders that older then 6 work days.

Find_defect.py is based on find differance between template image and actual. Then found points of diference go through evaluation 
of dimention and position. If it pass conditions, differance counts as OK, if not - NG. But this aproach doesn't work in my case.
Part's surface produces too differnt reflections wich count as differance and lead to wrong evaluation. This coudn't be handled 
without changing final machining polishing of the part.
