import argparse
import os
from pathlib import Path
from threading import Thread
from time import time

import EasyPySpin
import rasterio
import cv2

IMG_BASE_DIR = "images"


class VideoPlayback:

    def __init__(self, video_file="sources/Sahara2EU.webm", start_at = 150):
        self.background_video = cv2.VideoCapture(video_file)

        fps = self.background_video.get(cv2.CAP_PROP_FPS)
        print(f"background fps {fps}")
        self.background_video.set(cv2.CAP_PROP_POS_FRAMES, start_at * fps)

        self.grabbed, self.frame = self.background_video.read()
        self.stopped = False

    def start(self):
        self.thread = Thread(target=self.get, args=())
        # self.thread.daemon = True
        self.thread.start()
        return self
    
    def get(self):
        # os.environ['DISPLAY'] = ":1"
        cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        while self.background_video.isOpened():
            if self.stopped:
                return
            self.grabbed, self.frame = self.background_video.read()
            # print(self.grabbed)
            # print(self.frame.shape)
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


class StatickBackground:

    def __init__(self, img_file="sources/BlackMarble_2016_C1_geo.tif") -> None:
        src = rasterio.open(img_file)
        img = src.read()

        left_offset = 15000
        top_offset = 10000

        display_width = 3840
        # display_width = 1920
        display_height = 2160
        # display_height = 1080

        cropped_img = img[..., left_offset:left_offset+display_height, top_offset:top_offset+display_width]
        cropped_img = cropped_img.transpose(1, 2, 0)
        self.img_background = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2BGR)
        
    def start(self):
        self.thread = Thread(target=self.show, args=())
        # self.thread.daemon = True
        self.thread.start()
        return self
    
    def show(self):
        cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("window", self.img_background)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
    
    def stop(self):
        cv2.destroyAllWindows()
        self.thread.join()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder_name", required=True, help="Folder name")
    parser.add_argument("-n", "--num_frames", type=int, default=20, help="Number of frames to capture")
    parser.add_argument("-s", "--start_at", type=int, default=200, help="Start video at specific position (seconds)")
    parser.add_argument("-p", "--photo", action="store_true", help="Use photo (static background) instead of video")
    args = parser.parse_args()

    img_dir = f"{IMG_BASE_DIR}/{args.folder_name}"
    Path(img_dir).mkdir(parents=True, exist_ok=False)

    try:
        cap = EasyPySpin.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 4)

        if not cap.isOpened():
            print("Camera can't open\nexit")
            cap.release()
            exit(-1)

        cap.set_pyspin_value("AdcBitDepth", "Bit12")
        cap.set_pyspin_value("PixelFormat", "Mono16")
        # cap.set(cv2.CAP_PROP_EXPOSURE, 100) # us
        # cap.set(cv2.CAP_PROP_EXPOSURE, -1) # default
        # exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
        # print(exposure)
        # gain  = cap.get(cv2.CAP_PROP_GAIN)
        # gamma  = cap.get(cv2.CAP_PROP_GAMMA)

        if args.photo:
            background = StatickBackground()
        else:
            background = VideoPlayback(start_at=args.start_at)
        background.start()

        i = 0
        while i < args.num_frames:
            i += 1
            ret, frame = cap.read()

            print(f"frame read={ret}, {i=}, dtype={frame.dtype}, exposure={cap.get(cv2.CAP_PROP_EXPOSURE)}, time={time()}")
            file_name = f"{img_dir}/frame_{i}.png"
            cv2.imwrite(file_name, frame)

        print("camera release")
        cap.release()        
        
        print("stop background")
        background.stop()

    except KeyboardInterrupt:
        print("Capture interrupted")
        cap.release()
        background.stop()



