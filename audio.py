import edge_tts
import asyncio
import pyrubberband as pyrb
import soundfile as sf
from pydub import AudioSegment
from datetime import datetime
import os
from pathlib import Path
from multiprocessing import Pool
import logging
import shutil

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# Lớp Sub lưu thông tin phụ đề
class Sub:
    def __init__(self, stt, time, content):
        self.stt = stt
        self.time = time
        self.content = content

    def __str__(self):
        return f"Sub(stt={self.stt}, time={self.time}, content={self.content})"

# Hàm tính khoảng nghỉ giữa hai đoạn thời gian
def time_difference(time_range1, time_range2):
    format = "%H:%M:%S,%f"
    try:
        start_time1, end_time1 = time_range1.split(" --> ")
        start_time2, end_time2 = time_range2.split(" --> ")

        t1 = datetime.strptime(end_time1, format)
        t2 = datetime.strptime(start_time2, format)

        difference = t2 - t1
        return max(0, int(difference.total_seconds() * 1000))
    except ValueError as e:
        logging.error(f"Lỗi định dạng thời gian: {e}")
        return 0

# Hàm tính thời gian của một đoạn phụ đề (tính bằng giây)
def calculate_time_duration_seconds(time_str):
    try:
        start_time, end_time = time_str.split(" --> ")
        start_time = start_time.replace(',', '.')
        end_time = end_time.replace(',', '.')

        start_hours, start_minutes, start_seconds = map(float, start_time.split(':'))
        end_hours, end_minutes, end_seconds = map(float, end_time.split(':'))

        start_total_seconds = start_hours * 3600 + start_minutes * 60 + start_seconds
        end_total_seconds = end_hours * 3600 + end_minutes * 60 + end_seconds

        return round(end_total_seconds - start_total_seconds, 3)
    except Exception as e:
        logging.error(f"Lỗi tính thời gian phụ đề: {e}")
        return 0

# Hàm tính tỷ lệ thời gian cần kéo dãn
def need_rate(raw, right):
    ratio = raw / right
    return max(0.9, min(ratio, 2.0))  # Giới hạn tỷ lệ từ 0.9 đến 2.0 để tránh kéo quá nhiều

# Hàm đọc tệp phụ đề
def read_subtitles(file_path):
    subs = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        index = 0
        while index < len(lines):
            if lines[index].strip().isdigit():
                stt = int(lines[index].strip())
                time = lines[index + 1].strip()
                content = lines[index + 2].strip()
                subs.append(Sub(stt, time, content))
                index += 4
            else:
                index += 1
    except Exception as e:
        logging.error(f"Lỗi đọc phụ đề: {e}")
    return subs

# Hàm điều chỉnh tốc độ âm thanh (chạy trong mỗi tiến trình)
def adjust_audio_speed(task):
    sub, output_folder = task
    try:
        # Đọc file TTS
        tts_file = output_folder / f"{sub.stt}.mp3"
        y, sr = sf.read(tts_file)

        # Tính toán thời gian và tỷ lệ
        raw = len(y) / sr
        right = calculate_time_duration_seconds(sub.time)
        ratio = need_rate(raw, right)

        # Điều chỉnh tốc độ
        y_stretched = pyrb.time_stretch(y, sr, ratio)

        # Lưu file điều chỉnh
        adjusted_file = output_folder / f"{sub.stt}_right.wav"
        sf.write(adjusted_file, y_stretched, sr)

        # Xóa file TTS tạm
        os.remove(tts_file)
        return sub.stt
    except Exception as e:
        logging.error(f"Lỗi khi điều chỉnh tốc độ cho phụ đề {sub.stt}: {e}")
        return None

# Hàm xử lý âm thanh song song bằng multiprocessing
def process_audio_parallel(subtitles, output_folder):
    tasks = [(sub, Path(output_folder)) for sub in subtitles]

    # Tạo một Pool để xử lý song song
    with Pool() as pool:
        results = pool.map(adjust_audio_speed, tasks)

    logging.info(f"Hoàn tất xử lý các file âm thanh.")

# Hàm ghép các file âm thanh đã xử lý
def combine_audio(subtitles, output_folder, combined_output):
    combined = None
    endpoint = None

    output_folder = Path(output_folder)
    combined_output = Path(combined_output)

    for sub in subtitles:
        adjusted_file = output_folder / f"{sub.stt}_right.wav"
        if not adjusted_file.exists():
            continue

        # Đọc file đã điều chỉnh
        current_audio = AudioSegment.from_file(adjusted_file)

        # Thêm quãng nghỉ nếu cần
        if combined is None:
            combined = current_audio
        else:
            silence = AudioSegment.silent(duration=time_difference(endpoint, sub.time))
            combined += silence + current_audio

        # Cập nhật endpoint
        endpoint = sub.time

        # Xóa file tạm
        os.remove(adjusted_file)

    # Xuất file âm thanh cuối cùng
    if combined:
        combined.export(combined_output, format="mp3")
        logging.info(f"Tệp âm thanh cuối cùng đã được tạo: {combined_output}")
    else:
        logging.warning("Không có đoạn âm thanh nào được tạo.")

# Hàm chính
async def create_audio(subtitle_file, output_folder, combined_output):
    if not shutil.which("rubberband"):
        logging.error("Yêu cầu cài đặt rubberband-cli để sử dụng pyrubberband.")
        return

    # Đọc phụ đề
    subtitles = read_subtitles(subtitle_file)

    # Bước 1: Tạo TTS cho tất cả phụ đề (bất đồng bộ)
    tasks = []
    for sub in subtitles:
        try:
            tts_file = Path(output_folder) / f"{sub.stt}.mp3"
            if not tts_file.exists():
                logging.info(f"Tạo TTS cho phụ đề {sub.stt}: {sub.content}")
                communicate = edge_tts.Communicate(sub.content, 'vi-VN-HoaiMyNeural', pitch='+20Hz')
                tasks.append(communicate.save(str(tts_file)))
        except Exception as e:
            logging.error(f"Lỗi tạo TTS cho phụ đề {sub.stt}: {e}")
    await asyncio.gather(*tasks)

    # Bước 2: Điều chỉnh tốc độ âm thanh song song (multiprocessing)
    process_audio_parallel(subtitles, output_folder)

    # Bước 3: Ghép file âm thanh cuối cùng
    combine_audio(subtitles, output_folder, combined_output)

# Chạy chương trình
def export_audio(input_file, pj_folder, output_audio):
    # Đường dẫn đầu vào và đầu ra
    subtitle_file = Path(input_file)
    output_folder = Path(pj_folder)
    combined_output = Path(output_audio) if output_audio else output_folder / pj+".mp3"

    # Chạy bất đồng bộ
    asyncio.run(create_audio(subtitle_file, output_folder, combined_output))


if __name__ == '__main__':
    # Chạy chương trình
    export_audio(input_file,pj_folder,output_audio)

