import cv2
import numpy as np
import pyautogui
import time

def findobject(inp):
    # Đường dẫn ảnh cần tìm
    template_path = inp

    # Chụp màn hình hiện tại
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)  # Chuyển đổi sang mảng NumPy để sử dụng OpenCV

    # Đọc ảnh cần tìm
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Chuyển ảnh màn hình sang grayscale
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # So khớp mẫu
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Lấy vị trí có độ khớp cao nhất
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Ngưỡng khớp tối thiểu
    threshold = 0.8
    if max_val >= threshold:
        print(f"Đã tìm thấy hình ảnh! Độ khớp: {max_val}")
        top_left = max_loc
        h, w = template_gray.shape

        # Tính tọa độ trung tâm của vùng tìm thấy
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2

        # Nhấp chuột vào tọa độ trung tâm
        pyautogui.click(center_x, center_y)

findobject('s1.png')
time.sleep(10)
findobject('s2.png')
time.sleep(5)
findobject('s3.png')
time.sleep(3)
pyautogui.click(342,192,1,1)
time.sleep(3)
pyautogui.click(793,495,1,1)
time.sleep(3)
pyautogui.click(247,258,1,1)
time.sleep(3)
pyautogui.click(400,60,1,1)
time.sleep(3)
pyautogui.click(508,595,1,1)
time.sleep(30)
pyautogui.click(1761,26,1,1)
time.sleep(3)
# Di chuyển chuột 100 pixel sang phải và 50 pixel xuống dưới
pyautogui.move(1257, 378)
time.sleep(2)
pyautogui.scroll(-10)
time.sleep(2)
pyautogui.click(1006,686,1,1)
time.sleep(3)
pyautogui.click(1158,847,1,1)