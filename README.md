# ADD
Automated Defect Detection

This project is for automated defect detection on upper mating surface of cylinder block(CB) for engine assembling production. 
This is privet project so no examples, images or photos will be present. It's a trade secret.
All algorithmes will work on Ruspberry PI4B + HQ Raspberry camera module 16mm.

First part is just making photo on event (CB moves under camera). Already tested, workes well. If you will use it for your perpuse some
constants and thresholdes have to be adjusted. 

Get_image_from_video_3.py finds differance between template image of empty assembling line and carrent frame from video srtream.
If differance is greater then threash_up then wait for some frames (s - value in code).
To decrease computantional cost differnt between template and frame calculates only each nn-th frame (nn - value). nn = 2 in my case.
And more it calculates differnace not for whole frame but just for small part of it as I know where the motion appers each time.
farme_cut_up & farme_cut_low determine area of frame for differance culculation.

multiprocessing is needed for run second algorith (find_defect.py) and keep making shots of CBs at the same time.
folder_control.py is used for creation and deletion folders for images saving daily based by crontab.
