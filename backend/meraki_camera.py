import cv2
import numpy as np

class MerakiCamera(object):
    def __init__(self, ip):
        self.feed = f"rtsp://{ip}:9000/live"
        self.cap = cv2.VideoCapture(self.feed)
        self.retry = 0

    def __del__(self):
        self.cap.release()

    def get_frame(self, mqtt_output=None, hide_feed=False):
        if not hide_feed:
            ret, frame = self.cap.read()
        else:
            ret = True
            frame = np.zeros((1080, 1080, 3), dtype = np.uint8)

        while not ret:
            if self.retry >= 3:
                raise Exception(f"Exceeded retry limit for: {self.feed}")
            print(f"Reconneting to {self.feed}")
            self.cap.release()
            self.cap = cv2.VideoCapture(self.feed)
            ret, frame = self.cap.read()
            self.retry += 1
        self.retry = 0
            
        if mqtt_output is not None:
            for detection in mqtt_output:
                if detection['class'] == 0:
                    x1, y1, x2, y2 = detection['location']
                    x1 = int(x1 * frame.shape[1])
                    y1 = int(y1 * frame.shape[0])
                    x2 = int(x2 * frame.shape[1])
                    y2 = int(y2 * frame.shape[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'Class: {detection["class"]}, Score: {detection["score"]:.2f}',
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        frame = cv2.resize(frame, (1080, 1080))
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
