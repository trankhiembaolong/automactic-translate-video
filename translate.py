import openai
import re
import os

def tach_sub(content, batch_size):    
    # Sử dụng biểu thức chính quy để tách các khối phụ đề
    pattern = r"[0-9]+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n.+"
    matches = re.findall(pattern, content)
    sub = []

    combined = ""
    i = 0
    for x in matches:
        combined += x + "\n\n"
        i += 1
        if i == batch_size:
            sub.append(combined)
            i=0
            combined=""
        if x == matches[len(matches)-1]:
            sub.append(combined)

    dodaiphancuoi=len(sub[len(sub)-1])
    dodaikecuoi=len(sub[len(sub)-2])
    if dodaiphancuoi <= dodaikecuoi*0.4:
        sub[len(sub)-2] += sub[len(sub)-1] + "\n"
        del sub[len(sub)-1]
    return sub

def tao_sub(text):
    client = openai.OpenAI(api_key="sk-XLrlwYWMGgauXdqf60451f931c53407587253eFa33F234D6", base_url="https://api.llm.ai.vn/v1")
    response = client.chat.completions.create(
        model="openai:gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là một người phiên dịch phụ đề hoạt hình chuyên nghiệp, có thể sử dụng từ hán việt để bản dịch trở nên tốt nhất và luôn xuất dữ liệu theo dạng phụ đề"},
            {"role": "system", "content": "xưng hô chính là cậu-tôi"},
            {"role": "user", "content": f"Hãy giúp tôi phiên dịch đoạn phụ đề sau sang tiếng việt: {text}"}
        ]
    )
    translation = response.choices[0].message.content
    return translation

def translated_sub(file_sub,pj_folder):
    
    #Tạo folder và đường dẫn
    if not os.path.exists(pj_folder):
        os.makedirs(pj_folder)
    input_path = os.path.join("input", file_sub)
    output_file = pj_folder + "_translated.srt"
    output_path = os.path.join(pj_folder, output_file)
    
    # Đọc phụ đề gốc 
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Tách phụ đề ra từng đoạn nhỏ 
    sub=tach_sub(text,30)

    # Đưa cho chatgpt dịch
    translation = ""
    for text in sub:
        translation += tao_sub(text)

    # Xử lí sạch dữ liệu với regex
    pattern = r"(\```.+\n)|(```)"
    clear_translation = re.sub(pattern,"",translation)
    pattern1 = r"([^0-9 \n])\n([0-9])"
    clear_translation = re.sub(pattern1, r'\g<1>\n\n\g<2>',clear_translation)

    # Ghi nội dung vào tệp .srt
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(clear_translation)

    print(f"Dữ liệu được dịch đã ghi vào tệp {output_file} trong thư mục {pj_folder}")
    


