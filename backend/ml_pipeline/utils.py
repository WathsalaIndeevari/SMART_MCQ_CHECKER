import cv2
import numpy as np

def get_perspective_transform(image):
    """Detects a page and warps it to a flat, top-down view."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            # Sort points: top-left, top-right, bottom-right, bottom-left
            pts = approx.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            (tl, tr, br, bl) = rect
            width = max(int(np.linalg.norm(br - bl)), int(np.linalg.norm(tr - tl)))
            height = max(int(np.linalg.norm(tr - br)), int(np.linalg.norm(tl - bl)))
            
            dst = np.array([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            return cv2.warpPerspective(image, M, (width, height))
    return image # Return original if no page found

def sort_contours(cnts, method="left-to-right"):
    if not cnts: # Safety check
        return []
    
    i = 1 if method in ["top-to-bottom", "bottom-to-top"] else 0
    reverse = method in ["bottom-to-top", "right-to-left"]
    
    boxes = [cv2.boundingRect(c) for c in cnts]
    # Re-packing into a list so it's easier to handle than a zip object
    (cnts, _) = zip(*sorted(zip(cnts, boxes), key=lambda b: b[1][i], reverse=reverse))
    return list(cnts)