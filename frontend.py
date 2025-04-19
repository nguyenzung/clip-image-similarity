import os
import time
import requests
import heapq

from pathlib import Path

def is_image(filename):
    try:
        with Image.open(filename) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        return False

def list_files_in_directory(directory):
    try:
        files = [
            os.path.abspath(os.path.join(directory, f))
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and is_image(os.path.join(directory, f))
        ]
        return files
    except FileNotFoundError:
        return []


def process_files(file1, file2):
    url = "http://localhost:8002/predict/"
    
    if not os.path.isfile(file1) or not os.path.isfile(file2):
        return

    try:
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            files = [
                ("files", (os.path.basename(file1), f1, "image/jpeg")),
                ("files", (os.path.basename(file2), f2, "image/jpeg")),
            ]
            response = requests.post(url, files=files)
            # print("✅ Response:", response.json(), type(response.json()))
            if not isinstance(response.json(), float):
                return None
            return response.json()
    except Exception as e:
        print(f"⚠️ Error processing files:\n - {file1}\n - {file2}")
        print("Exception:", e)
        return None

def find_top_similar_files(test_file, files, top_n=20):
    similarity_scores = []
    total = len(files)
    for i in range(0, len(files)):
        if i % 50 == 0:
            print("Progress:", i, "/", total)
        try:
            similarity = process_files(test_file, files[i])
            if similarity is not None:
                similarity_scores.append((similarity, files[i]))
        except Exception as e:
            print(f"Error processing {files[i]}: {e}")

    print("Heapq sort")
    top_files = heapq.nlargest(top_n, similarity_scores, key=lambda x: x[0])
    print("Result")
    print(top_files)

    return top_files

def clear_output_dir(output_dir):
    output_path = Path(output_dir)
    if output_path.exists() and output_path.is_dir():
        for file in output_path.iterdir():
            if file.is_file():
                file.unlink()

def save_top_files(top_files, output_dir):
    clear_output_dir(output_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for idx, (score, file_path) in enumerate(top_files):
        filename = os.path.basename(file_path)
        # print(filename)
        output_file_path = output_path / f"top_{idx+1}_{filename}"
        # print(output_file_path)
        with open(file_path, 'rb') as src_file:
            with open(output_file_path, 'wb') as dest_file:
                dest_file.write(src_file.read())  # Or use shutil.copy

        print(f"Saved {file_path} to {output_file_path}")

def main():
    print("The main function")
    directory = input("Đường dẫn ảnh được lưu: ")
    files = list_files_in_directory(directory)
    # for i in range(0, len(files)-1, 2):
    #     if i % 100 == 0:
    #         timestamp = time.time()
    #         print("Progress:", i, time.time())
        
    #     pair = files[i:i+2]
    #     process_files(pair[0], pair[1])
    while True:
        try:
            in_img = input("Đường dẫn ảnh muốn kiểm tra: ")
            output_dir = "output/"

            top_files = find_top_similar_files(in_img, files, top_n=20)
            save_top_files(top_files, output_dir)
        except Exception as e:
            print(e)

    return


if __name__ == "__main__":
    main()