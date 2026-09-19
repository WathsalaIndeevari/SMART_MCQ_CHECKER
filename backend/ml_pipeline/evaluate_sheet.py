import cv2
import json
import csv
import os
import numpy as np
from utils import get_perspective_transform

def evaluate_sheet(image_path, layout_json="layout.json"):
    if not os.path.exists(layout_json):
        return "LAYOUT_MISSING"
    
    img = cv2.imread(image_path)
    if img is None: 
        return None
    
    warped = get_perspective_transform(img)
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cv2.imwrite("check_this_image.jpg", thresh) # Check this image to see if bubbles are white!

    with open(layout_json, "r") as f:
        layout = json.load(f)

    student_answers = {}

    for q_num, bubbles in layout.items():
        # Count pixels in each bubble
        pixel_counts = [cv2.countNonZero(thresh[y:y+h, x:x+w]) for (x, y, w, h) in bubbles]
        
        filled_idx = np.argmax(pixel_counts)
        
        # USE NUMBERS INSTEAD OF LETTERS:
        # Index 0 becomes "1", Index 1 becomes "2", etc.
        if pixel_counts[filled_idx] > 40: 
            student_answers[int(q_num)] = str(filled_idx + 1)
        else:
            student_answers[int(q_num)] = "0"

    # Print a sample to the terminal so we can see what the computer 'saw'
    sample_keys = sorted(list(student_answers.keys()))[:5]
    sample_ans = [student_answers[k] for k in sample_keys]
    print(f"🔎 Computer read (Q1-5): {sample_ans}")
            
    return student_answers

def load_answer_key_row(csv_path, target_test_id):
    key_mapping = {}
    if not os.path.exists(csv_path): 
        return None
    with open(csv_path, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['test_id'].strip() == target_test_id:
                for col_name, value in row.items():
                    if col_name.strip().upper().startswith('Q'):
                        try:
                            q_num = int(''.join(filter(str.isdigit, col_name)))
                            key_mapping[q_num] = value.strip().upper()
                        except: 
                            continue
                return key_mapping
    return None

if __name__ == "__main__":
    TARGET_TEST = "Test001" 
    ANS_KEY_PATH = "dataset/answer_key.csv"
    LAYOUT_PATH = "layout.json"
    SHEETS_DIR = "dataset/sample_data" 

    answer_key = load_answer_key_row(ANS_KEY_PATH, TARGET_TEST)
    
    if not answer_key:
        print(f"❌ Error: Test ID '{TARGET_TEST}' not found in {ANS_KEY_PATH}")
    else:
        print(f"\n🚀 Processing {TARGET_TEST} (Total Questions: {len(answer_key)})")
        print(f"{'FILE NAME':<25} | {'SCORE':<10} | {'PERCENTAGE'}")
        print("-" * 55)

        results_summary = []
        if not os.path.exists(SHEETS_DIR):
            print(f"❌ Directory not found: {SHEETS_DIR}")
        else:
            for file_name in os.listdir(SHEETS_DIR):
                if file_name.lower().endswith((".jpg", ".png", ".jpeg")):
                    ans = evaluate_sheet(os.path.join(SHEETS_DIR, file_name), LAYOUT_PATH)
                    
                    if ans == "LAYOUT_MISSING":
                        print("❌ Error: layout.json not found! Run extract_layout.py first.")
                        break
                    elif ans:
                        # Robust comparison: convert both to string, strip spaces, and uppercase
                        correct = 0
                        for q, correct_val in answer_key.items():
                            student_val = str(ans.get(q)).strip().upper()
                            if student_val == str(correct_val).strip().upper():
                                correct += 1
                        
                        total = len(answer_key)
                        percent = (correct / total) * 100
                        print(f"{file_name:<25} | {correct}/{total:<7} | {percent:.2f}%")
                        results_summary.append([file_name, correct, total, f"{percent:.2f}%"])

        print("-" * 55)
        print(f"✅ Total Sheets Processed: {len(results_summary)}")

        output_csv = "dataset/results.csv"
        try:
            with open(output_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["FileName", "Correct", "Total", "Percentage"])
                writer.writerows(results_summary)
        except PermissionError:
            print(f"\n⚠️ WARNING: Could not save CSV. Please CLOSE '{output_csv}' and try again.")