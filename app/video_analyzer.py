import cv2

def detect_motion(video_path: str, movement_threshold: float = 0.01) -> bool:
    """
    Возвращает True, если в видео обнаружено движение.
    movement_threshold это доля пикселей, которая должна измениться, чтобы считать, что движение есть.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Cannot open video file")

    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Cannot read frames from video")

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    motion_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        frame_delta = cv2.absdiff(prev_gray, gray)
        _, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)

        changed_pixels = cv2.countNonZero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]

        if total_pixels > 0:
            fraction_changed = changed_pixels / total_pixels
            if fraction_changed > movement_threshold:
                motion_detected = True
                break

        prev_gray = gray

    cap.release()
    return motion_detected
