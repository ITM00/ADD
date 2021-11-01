import numpy as np
import cv2
from operator import itemgetter
from skimage.metrics import structural_similarity
from datetime import datetime, date



def image_subtraction(img2):
    # load images
    f = open("/home/pi/AuDD/2_Scripts_V2/Settings.txt", "r")
    lines = f.readlines()
    f.close()

    img1 = cv2.imread(lines[0].strip())  # Standard image
    # img1 = img1[900:3000, 300:4200]
    imgblr1 = cv2.medianBlur(img1, 3)
    # img2 = cv2.imread("Block on line with DFx2 crop.jpg")
    # img2 = img2[898:2998, 298:4198]
    # imgblr2 = cv2.medianBlur(np.float32(img2), 3)
    imgblr2 = cv2.medianBlur(img2, 3)

    gray1 = cv2.cvtColor(imgblr1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(imgblr2, cv2.COLOR_BGR2GRAY)

    # Diff score, closer to 1 more similar
    score, diff = structural_similarity(gray1, gray2, full=True)
    diff = (diff * 255).astype("uint8")
    # print("SSIM: {}".format(score))

    retr_is, thresh_is = cv2.threshold(diff, 0, 255,
                                       cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)  # [1]    # binary image of differance
    # cv2_imshow(thresh_is)
    return retr_is, thresh_is


def grouping_and_area(retr_is, thresh_is):  # Check is retr_is really needed for this function???
    retr = retr_is
    cnts, hierarchy = cv2.findContours(thresh_is, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Area calculating
    # pix_sqare = 0.0116
    areas = []
    for c in cnts:
        area = round(cv2.contourArea(c), 2)  # *pix_sqare
        areas.append(area)

    # Grouping
    areas_copy = areas.copy()
    cnts_copy = cnts.copy()
    d = 50  # distance between defects to count as one, in pixels
    closest_contours = []
    areas_grouped = []
    cnts_number = 0
    n = 0

    def proximity_check(contour_1, contour_2, area_1, area_2):
        for p_1 in contour_1:
            for p_2 in contour_2:
                dist = np.sqrt((abs(p_2[0][0] - p_1[0][0])) ** 2 + (abs(p_2[0][1] - p_1[0][1])) ** 2)
                if dist < d:
                    contour_1 = np.concatenate((contour_1, contour_2), axis=0)
                    area_1 = round((area_1 + area_2), 2)
                    return contour_1, area_1;
                if p_1[0][0] == contour_1[-1][0][0] and p_1[0][1] == contour_1[-1][0][1]:
                    return contour_1, area_1;

    for i in range(len(cnts_copy)):
        if not cnts_copy:
            break
        area_1 = areas_copy[cnts_number]
        contour_1 = cnts_copy[cnts_number]
        for i in range(len(cnts_copy) - 1):
            length_1 = len(contour_1)
            contour_2 = cnts_copy[cnts_number + 1]
            area_2 = areas_copy[cnts_number + 1]
            contour_1, area_1 = proximity_check(contour_1, contour_2, area_1, area_2)
            length_2 = len(contour_1)

            if length_1 < length_2:
                del areas_copy[cnts_number + 1]
                del cnts_copy[cnts_number + 1]
            if length_1 == length_2:
                cnts_number += 1

        del cnts_copy[0]
        del areas_copy[0]
        closest_contours.append(contour_1)
        areas_grouped.append(area_1)
        cnts_number = 0

    return areas_grouped, closest_contours


def drawing_frames(areas_grouped, closest_contours, ntrsct, img_to_check, sampling, cnt, path):
    if ntrsct:
        sealing_line = cv2.imread("Gasket final.jpg", 0)
        retr_sl, thresh_sl = cv2.threshold(sealing_line, 0, 255,
                                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)  # For C/B image
        # retr_sl, thresh_sl = cv2.threshold(sealing_line, 0, 255,cv2.THRESH_BINARY)  # For test image
        cnts_sl, hierarchy = cv2.findContours(thresh_sl, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        sealing_line_contour = img_to_check.copy()
        cv2.drawContours(sealing_line_contour, cnts_sl, -1, (0, 0, 255), 3)

    if not ntrsct:
        sealing_line_contour = img_to_check.copy()

    for i in range(len(closest_contours)):
        # Get coords for bounding
        group = np.concatenate(closest_contours[i], axis=0)
        sorted_h = sorted(group, key=itemgetter(1))
        sorted_w = sorted(group, key=itemgetter(0))
        coef = 15  # For taking more space around defect
        h = sorted_h[0][1] - coef
        w = sorted_w[0][0] - coef
        w_frame = abs(sorted_w[-1][0] - w + coef)
        h_frame = abs(sorted_h[-1][1] - h + coef)

        # Bounding around gropups
        cv2.rectangle(sealing_line_contour, (w, h), (w + w_frame, h + h_frame), (0, 0, 255), 2)
        crop = sealing_line_contour[h:h + h_frame, w:w + w_frame]
        crop_res = cv2.resize(crop, (5 * np.shape(crop)[1], 5 * np.shape(crop)[0]), interpolation=cv2.INTER_CUBIC)
        if sampling:
            path_sample = "/home/pi/AuDD/5_Photos/Samples//" + path + str(cnt) + ".jpg"
            crop = img_to_check[h:h + h_frame, w:w + w_frame]
            cv2.imwrite(path_sample, crop)
            cnt += 1
        # Coordinates fro crop_res paste
        h_main, w_main = np.shape(img_to_check)[0], np.shape(img_to_check)[1]
        h_rect, h_padding = 60, 30
        w_paste = w - int(w_frame / 2)

        if h > h_main / 2:
            h_paste = h - np.shape(crop_res)[0] - h_rect - h_padding
        if h < h_main / 2:
            h_paste = h + h_frame + h_padding

        # Coordinates for white rectangle
        x_rect = w_paste
        y_rect, w_rect = h_paste + np.shape(crop_res)[0], np.shape(crop_res)[1]
        cv2.rectangle(sealing_line_contour, (x_rect, y_rect), (x_rect + w_rect, y_rect + h_rect), (255, 255, 255), -1)

        # Bounding + text + paste crop_res
        sealing_line_contour[h_paste: h_paste + np.shape(crop_res)[0],
        w_paste: w_paste + np.shape(crop_res)[1]] = crop_res
        cv2.rectangle(sealing_line_contour, (w_paste, h_paste),
                      (w_paste + np.shape(crop_res)[1], h_paste + np.shape(crop_res)[0] + h_rect), (0, 0, 255), 3)
        font_size = (w_paste - w_paste + np.shape(crop_res)[1]) * 0.05
        if font_size > 1.7:
            font_size = 1.7
        pixel = 0.0116  # Convert pixel to mm2 coef
        cv2.putText(sealing_line_contour, str(int(areas_grouped[i] * pixel)) + "mm2", (x_rect + 10, y_rect + 40),
                    cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 2)

    return sealing_line_contour, cnt  #sealing_line_contour img_to_check


def intersection_check(thresh_is):
    img2 = cv2.imread("Gasket final.jpg", 0)  # Gasket contour binary image

    # Finding intersection
    row, col = 0, 0
    result, line = [], []
    col_lim = len(thresh_is[0])

    for s in thresh_is:
        if sum(s) == 0:
            result.append(s)
            row += 1
        else:
            for i in s:
                if col >= col_lim:
                    col = 0
                if i == 0 or i == img2[row][col]:
                    line.append(i)
                else:
                    line.append(0)
                col += 1
            row += 1
            result.append(line)
            line = []

    result = np.array(result)  # need for cv2 to show image
    return result


#
# def if_no_defects(img_to_check):
#     x, y, w, h = 0, 0, np.shape(img_to_check)[1], np.shape(img_to_check)[0]
#     cv2.rectangle(img_to_check, (x, y), (x + w, y + h), (0, 255, 0), 5)
#     no_defects = True
#     return no_defects, img_to_check


# Start is here.

def image_check(myQ, sampling):
    print("image check started")
    img_to_check = myQ.get()
    now = datetime.now()
    dt_string = now.strftime("%d.%m.%Y %H.%M")
    no_defects = False
    retr_is, thresh_is = image_subtraction(img_to_check)
    # If no defects save and done:
    if np.sum(thresh_is) == 0:
        x, y, w, h = 0, 0, np.shape(img_to_check)[1], np.shape(img_to_check)[0]
        cv2.rectangle(img_to_check, (x, y), (x + w, y + h), (0, 255, 0), 5)
        path = dt_string + " OK.jpg"
        cv2.imwrite(path, img_to_check)
        pass
        # done = if_no_defects(img_to_check)
        # no_defects = True
        # return no_defects, img_to_check

    # If there are defects:
    result = intersection_check(thresh_is)

    if np.sum(result) != 0:
        cv2.rectangle(img_to_check, (0, 0), (np.shape(img_to_check)[1], np.shape(img_to_check)[0]), (0, 0, 255), 10)
        retr, thresh = cv2.threshold(result.astype("uint8"), 0, 255, cv2.THRESH_BINARY_INV)  # Add _INV for C/B image
        areas_grouped_ntrsct, closest_contours_ntrsct = grouping_and_area(retr, thresh)

    areas_grouped, closest_contours = grouping_and_area(retr_is, thresh_is)
    array_1 = np.array(closest_contours, dtype="object")
    array_2 = np.array(closest_contours_ntrsct, dtype="object")
    cnt = 0

    # If all countoures intersect sealing line:
    if np.array_equal(array_1, array_2):
        ntrsct = True
        img_to_check, cnt = drawing_frames(areas_grouped, closest_contours, ntrsct, img_to_check, sampling, cnt)

    # If some contours intersect sealing line and some not:
    closest_contours_copy = closest_contours.copy()
    closest_contours_ntrsct_grouped = []
    areas_grouped_ntrsct_grouped = []
    if not np.array_equal(array_1, array_2):
        n = 0
        for i in range(len(closest_contours_ntrsct)):
            el_first = closest_contours_ntrsct[i]
            for el_second in closest_contours:
                if any(elem in el_second for elem in el_first):
                    closest_contours_ntrsct_grouped.append(closest_contours[n])
                    areas_grouped_ntrsct_grouped.append(areas_grouped[n])
                    closest_contours = np.delete(closest_contours, n, 0)
                    areas_grouped = np.delete(areas_grouped, n, 0)
                    n += 1
                    break
        closest_contours_ntrsct_grouped = np.array(closest_contours_ntrsct_grouped, dtype="object")
        areas_grouped_ntrsct_grouped = np.array(areas_grouped_ntrsct_grouped, dtype="object")

        path = date.today().strftime("%d.%m.%Y") + "//" + dt_string + " NG"

        ntrsct = True
        img_to_check, cnt = drawing_frames(areas_grouped_ntrsct_grouped, closest_contours_ntrsct_grouped, ntrsct,
                                      img_to_check, sampling, cnt, path)
        ntrsct = False
        img_to_check, cnt = drawing_frames(areas_grouped, closest_contours, ntrsct, img_to_check, sampling, cnt, path)
        cv2.imwrite('/home/pi/AuDD/Photos//'+ path + '.jpg', img_to_check)
    print("image checked")
    # return (img_to_check, no_defects)

# img_to_check = cv2.imread("Block on line with DFx2 crop.jpg")  # Photo shot module output. Have to be writen!
# image_check(img_to_check)
# img_to_check, no_defects = image_check(img_to_check)
# cv2_imshow(img_to_check)

# # Path + name for saving
# now = datetime.now()
# dt_string = now.strftime("%d.%m.%Y %H.%M")
# if no_defects:
#     path = dt_string + " OK.jpg"
# else:  # if NG run parallelizm and send email and save the image
#     path = dt_string + " NG.jpg"
# cv2.imwrite(path, img_to_check)
