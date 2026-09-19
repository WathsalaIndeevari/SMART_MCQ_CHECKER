import cv2
import json
import numpy as np
import os
import glob
from utils import get_perspective_transform, sort_contours

def extract_layout(image_path, output_json="layout.json"):
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: Could not read image at {image_path}")
        return

    warped = get_perspective_transform(img)
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # Find all bubble-like contours
    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubbles = []
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        # Narrowed constraints to target only the bubbles (1-5)
        if 15 <= w <= 45 and 15 <= h <= 45: 
            bubbles.append(c)

    if not bubbles:
        print("❌ No bubbles detected!")
        return

    # 1. Sort all bubbles Left-to-Right to separate the 5 columns
    bubbles = sort_contours(bubbles, method="left-to-right")
    
    # 2. Group bubbles into 5 columns based on X-coordinate
    columns = []
    if bubbles:
        curr_col = [bubbles[0]]
        for i in range(1, len(bubbles)):
            (x_prev, y_prev, w_prev, h_prev) = cv2.boundingRect(bubbles[i-1])
            (x_curr, y_curr, w_curr, h_curr) = cv2.boundingRect(bubbles[i])
            
            # If X difference is large, it's a new group/column
            if abs(x_curr - x_prev) > 50: 
                columns.append(curr_col)
                curr_col = []
            curr_col.append(bubbles[i])
        columns.append(curr_col)

    # 3. Process each column to extract questions (10 questions per column)
    final_layout = {}
    q_number = 1
    
    for col in columns:
        # Sort current column Top-to-Bottom
        col_sorted = sort_contours(col, method="top-to-bottom")
        
        current_q_bubbles = []
        last_y = -1
        
        for b in col_sorted:
            (x, y, w, h) = cv2.boundingRect(b)
            # Group 5 bubbles into one question row
            if last_y != -1 and abs(y - last_y) > h/2:
                final_layout[str(q_number)] = sorted(current_q_bubbles, key=lambda b: b[0])
                q_number += 1
                current_q_bubbles = []
            
            current_q_bubbles.append([int(x), int(y), int(w), int(h)])
            last_y = y
        
        # Add the last question of the column
        if current_q_bubbles:
            final_layout[str(q_number)] = sorted(current_q_bubbles, key=lambda b: b[0])
            q_number += 1

    with open(output_json, "w") as f:
        json.dump(final_layout, f, indent=4)
    
    print(f"✅ Success! Found {len(final_layout)} questions across 5 columns.")
    print(f"✅ Layout saved to: {os.path.abspath(output_json)}")

if __name__ == "__main__":
    template_folder = "dataset/blank_template"
    search_pattern = os.path.join(template_folder, "*.*")
    found_files = [f for f in glob.glob(search_pattern) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if found_files:
        extract_layout(found_files[0], "layout.json")
    else:
        print(f"❌ Error: No image files found in {template_folder}")