import translate
import audio
import os

def main():
    while True:  # Sử dụng vòng lặp để lặp lại chương trình
        # Nhập thông tin từ người dùng
        pj_folder = input("Hãy nhập tên dự án: ")
        file_sub = input("Nhập tên tệp phụ đề gốc: ")
        output_sub = input(f"Nhập tên tệp phụ đề được dịch (nếu để trống thì mặc định là {pj_folder}_translated.srt): ")
        output_audio = input(f"Nhập tên tệp thuyết minh (nếu để trống thì mặc định là {pj_folder}.mp3): ")
        if !output_audio:
            output_audio += ".mp3"

        # Dịch phụ đề
        translate.translated_sub(file_sub, pj_folder, output_sub)
        
        # Xác định tệp phụ đề đầu vào cho audio
        if output_sub == "":
            input_audio = os.path.join(pj_folder, pj_folder + "_translated.srt")
        else:
            input_audio = os.path.join(pj_folder, output_sub)

        # Xuất tệp âm thanh
        audio.export_audio(input_audio, pj_folder, output_audio)

        # Kiểm tra người dùng có muốn lặp lại hay không
        n = input("Nhập bất kì để kết thúc chương trình, hoặc nhập '1' để tiếp tục: ")
        if n != "1":  # Nếu không phải '1', thoát khỏi vòng lặp
            print("Kết thúc chương trình.")
            break

if __name__ == "__main__":
    main()