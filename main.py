import translate
import audio
import os
import re

def main():
    while True:  # Sử dụng vòng lặp để lặp lại chương trình
        # Nhập thông tin từ người dùng
        pj_folder = input("Nhập tên tệp phụ đề gốc: ")
        if re.findall(r"\.srt", pj_folder) == []:
            file_sub = pj_folder + ".srt"
        else:
            file_sub = pj_folder

        # Dịch phụ đề
        translate.translated_sub(file_sub, pj_folder)
        
        # Xác định tệp phụ đề đầu vào cho audio
        input_audio = pj_folder + "_translated.srt"

        # Xuất tệp âm thanh
        audio.export_audio(input_audio, pj_folder) 

        # Kiểm tra người dùng có muốn lặp lại hay không
        n = input("Nhập bất kì để kết thúc chương trình, hoặc nhập '1' để tiếp tục: ")
        if n != "1":  # Nếu không phải '1', thoát khỏi vòng lặp
            print("Kết thúc chương trình.")
            break

if __name__ == "__main__":
    main()