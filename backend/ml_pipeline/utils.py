import cv2
import numpy as np


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def get_perspective_transform(image):
    """Detect a page and warp it to a flat, top-down view."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            pts = approx.reshape(4, 2).astype("float32")
            rect = order_points(pts)
            (tl, tr, br, bl) = rect
            width = max(int(np.linalg.norm(br - bl)), int(np.linalg.norm(tr - tl)))
            height = max(int(np.linalg.norm(tr - br)), int(np.linalg.norm(tl - bl)))
            dst = np.array(
                [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
                dtype="float32",
            )
            matrix = cv2.getPerspectiveTransform(rect, dst)
            return cv2.warpPerspective(image, matrix, (width, height))
    return image


def sort_contours(cnts, method="left-to-right"):
    if not cnts:
        return []
    axis = 1 if method in ["top-to-bottom", "bottom-to-top"] else 0
    reverse = method in ["bottom-to-top", "right-to-left"]
    boxes = [cv2.boundingRect(c) for c in cnts]
    packed = sorted(zip(cnts, boxes), key=lambda item: item[1][axis], reverse=reverse)
    return [contour for contour, _box in packed]


def preprocess_for_bubbles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    return gray, cleaned
