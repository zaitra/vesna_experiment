import argparse
from pathlib import Path
from threading import Thread
from time import time

import EasyPySpin
import cv2

IMG_BASE_DIR = "images"


class VideoPlayback:

    def __init__(self, video_file="Africa2EU_50x.mp4", start_at = 100):
        self.background_video = cv2.VideoCapture(video_file)

        fps = self.background_video.get(cv2.CAP_PROP_FPS)
        self.background_video.set(cv2.CAP_PROP_POS_FRAMES, start_at * fps)

        self.grabbed, self.frame = self.background_video.read()
        self.stopped = False

    def start(self):
        self.thread = Thread(target=self.get, args=())
        # self.thread.daemon = True
        self.thread.start()
        return self
    
    def get(self) :
        cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        while self.background_video.isOpened():
            if self.stopped:
                return
            self.grabbed, self.frame = self.background_video.read()
            # print(self.grabbed)
            cv2.imshow("window", self.frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                cv2.destroyAllWindows()

    def stop(self):
        self.stopped = True
        cv2.destroyAllWindows()
        self.thread.join()
        self.background_video.release()


    def __exit__(self, exc_type, exc_value, traceback) :
        self.background_video.release()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--session", required=True, help="Session name")
    parser.add_argument("-n", "--num_frames", type=int, default=20, help="Number of frames to capture")
    args = parser.parse_args()

    img_dir = f"{IMG_BASE_DIR}/{args.session}"
    Path(img_dir).mkdir(parents=True, exist_ok=True)

    cap = EasyPySpin.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 4)

    # cap.set(cv2.CAP_PROP_EXPOSURE, 100) # us
    # cap.set(cv2.CAP_PROP_EXPOSURE, -1) # default
    # exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
    # print(exposure)
    # gain  = cap.get(cv2.CAP_PROP_GAIN)
    # gamma  = cap.get(cv2.CAP_PROP_GAMMA)

    video_playback = VideoPlayback()
    video_playback.start()

    i = 0
    while i < args.num_frames:
        i += 1
        ret, frame = cap.read()
        print(ret, i, time())
        file_name = f"{img_dir}/frame_{i}.png"
        cv2.imwrite(file_name, frame)

    print("stop video")
    video_playback.stop()



