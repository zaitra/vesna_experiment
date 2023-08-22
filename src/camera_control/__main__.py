import argparse
import logging
import os
from pathlib import Path
from threading import Thread
from time import time

import boto3
import cv2
import EasyPySpin
import rasterio
import structlog
import typer
from botocore.exceptions import ClientError
from typing_extensions import Annotated

IMG_BASE_DIR = "images"
SRC_BASE_DIR = "sources"


class VideoPlayback:
    def __init__(
        self,
        video_file=f"{SRC_BASE_DIR}/Sahara2EU-002.webm",
        start_at=150,
        download=False,
    ):
        if not Path(video_file).exists():
            structlog.get_logger().warning(
                "Video %s was not found locally.", video_file
            )

            s3 = boto3.client("s3")
            bucket_name = "vesna-camera-control-storage"
            key = "Sahara2EU-002.webm"
            structlog.get_logger().info(
                "Attempting to fetch video remotely from %s", bucket_name + "/" + key
            )

            response = s3.head_object(Bucket=bucket_name, Key=key)
            content_length = int(response["ContentLength"])

            if download:
                structlog.get_logger().info(
                    "Downloading and storing video, this may take a while depending on file size."
                )
                s3.download_file(bucket_name, key, video_file)
            else:
                structlog.get_logger().info(
                    "Remotely streaming video, file won't be stored locally."
                )
                structlog.get_logger().warning(
                    "It may take a while for OpenCV to begin playing a streamed video from the start_at frame!"
                )
                try:
                    video_file = s3.generate_presigned_url(
                        ClientMethod="get_object",
                        Params={"Bucket": bucket_name, "Key": key},
                    )
                except Exception:
                    structlog.get_logger().warning(
                        "Could not reach remote storage. Proceeding without video..."
                    )

        self.background_video = cv2.VideoCapture(video_file)
        structlog.get_logger().info("Video fetched.")

        fps = self.background_video.get(cv2.CAP_PROP_FPS)
        structlog.get_logger().info(f"Background FPS {fps}, setting start_at frame...")
        self.background_video.set(cv2.CAP_PROP_POS_FRAMES, start_at * fps)
        structlog.get_logger().info(
            "Set start_at frame to %d, %d seconds in.", start_at * fps, start_at
        )

        (
            self.grabbed,
            self.frame,
        ) = self.background_video.read()  # What is this here for?
        self.stopped = False

    # Start video thread
    def start(self):
        self.thread = Thread(target=self.get, args=())
        self.thread.start()
        return self

    # Get video frames until window is closed
    def get(self):
        os.environ["DISPLAY"] = ":1"
        cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        while self.background_video.isOpened():
            structlog.get_logger().info("Querying whether to stop")
            if self.stopped:
                structlog.get_logger().info("STOPPING!")
                return
            self.grabbed, self.frame = self.background_video.read()
            # print(self.grabbed)
            # print(self.frame.shape)
            cv2.imshow("window", self.frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.stop()
                cv2.destroyAllWindows()
                cv2.waitKey(1)

    # Stop/close background
    def stop(self):
        self.stopped = True
        cv2.waitKey(1)
        self.thread.join()
        self.background_video.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    # Release video in case of premature exit
    def __exit__(self, exc_type, exc_value, traceback):
        self.background_video.release()


class StatickBackground:
    def __init__(self, img_file=f"{SRC_BASE_DIR}/BlackMarble_2016_C1_geo.tif") -> None:
        if not Path(img_file).exists():
            structlog.get_logger().warning(
                "Image %s was not found and won't be opened.", img_file
            )

        src = rasterio.open(img_file)
        structlog.get_logger().info("Image opened.")
        img = src.read()

        left_offset = 15000
        top_offset = 10000

        # display_width = 3840
        display_width = 1920
        # display_height = 2160
        display_height = 1080

        cropped_img = img[
            ...,
            left_offset : left_offset + display_height,
            top_offset : top_offset + display_width,
        ]

        cropped_img = cropped_img.transpose(1, 2, 0)
        self.img_background = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2BGR)
        structlog.get_logger().info(
            "Preparing cropped image. Press the 'q' key to close prematurely."
        )

        self.stopped = False

    # Start image showing thread
    def start(self):
        self.thread = Thread(target=self.show, args=())
        self.thread.start()
        return self

    # Show image until key is pressed or recording's over
    def show(self):
        cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("window", self.img_background)
        print(self.stopped)
        while not self.stopped:
            if cv2.waitKey(500) & 0xFF == ord("q"):
                self.stopped = True
                cv2.destroyAllWindows()
                cv2.waitKey(1)
        return

    # Stop/close background
    def stop(self):
        if not self.stopped:
            self.stopped = True
            cv2.destroyAllWindows()
            cv2.waitKey(1)
        self.thread.join()


def main(
    folder_name: Annotated[
        str, typer.Argument(help="Target Images Folder Name")
    ] = "test",
    num_frames: Annotated[int, typer.Argument(help="Number of frames to capture")] = 20,
    start_at: Annotated[
        int, typer.Argument(help="Start video at specific position (seconds)")
    ] = 120,
    photo: Annotated[
        bool, typer.Argument(help="Use photo (static background) instead of video")
    ] = True,
    download: Annotated[
        bool,
        typer.Argument(
            help="Download and locally store source footage if obtaining it remotely."
        ),
    ] = False,
):
    # Initiate logger
    log = structlog.get_logger()

    # Create new Target Folder for captured images
    img_dir = f"{IMG_BASE_DIR}/{folder_name}"
    if Path(img_dir).exists():
        log.info("Chosen directory for target images already exists;")
        while Path(img_dir).exists():
            img_dir = img_dir + "'"
        log.info("New target directory is %s", img_dir)
    Path(img_dir).mkdir(parents=True, exist_ok=False)

    # Use camera until keyboard input interruption
    try:
        cap = EasyPySpin.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 4)

        if not cap.isOpened():
            log.fatal("Camera can't open\nexit")
            cap.release()
            exit(-1)

        cap.set_pyspin_value("AdcBitDepth", "Bit12")
        cap.set_pyspin_value("PixelFormat", "Mono16")

        # Open background
        if photo:
            background = StatickBackground()
        else:
            background = VideoPlayback(start_at=start_at, download=download)
        background.start()

        # Begin camera capture loop
        i = 0
        while i < num_frames:
            i += 1
            ret, frame = cap.read()

            log.info(
                f"Frame: read={ret}, {i=}, dtype={frame.dtype}, exposure={cap.get(cv2.CAP_PROP_EXPOSURE)}, time={time()}"
            )
            file_name = f"{img_dir}/frame_{i}.png"
            cv2.imwrite(file_name, frame)

        log.info("Camera released.")
        cap.release()

        log.info("Stopping background.")
        background.stop()

    except KeyboardInterrupt:
        log.warning("Capture interrupted.")
        cap.release()
        background.stop()


if __name__ == "__main__":
    typer.run(main)
