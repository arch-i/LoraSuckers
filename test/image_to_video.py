import base64
import time
import requests
from pathlib import Path
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

API_BASE = "https://api.minimaxi.chat/v1"
API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJhZGl0eWEgbGFraGUiLCJVc2VyTmFtZSI6ImFkaXR5YSBsYWtoZSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTI4NzI2Nzg3MzI4NTc4MjA2IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTkyODcyNjc4NzMyNDM4MzkwMiIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6ImFkaXR5YWxha2hlNUBnbWFpbC5jb20iLCJDcmVhdGVUaW1lIjoiMjAyNS0wNS0zMSAxOTozNDoxOSIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.PpvFaPS_vXtQO6Tq4r3DcHBo3uqMEqdX3p0PrWOfrJHJ4i_mB8YBpe6iGt1qB60Fw6J54vJae3cKos8pOSQJENAOtSWDH61SGf4A8yFLEFd62eUXygqcpXQs1HwnAN60syqw6RmGavWg9kP5W63xfhDOULqKkjlO7FPoRbF4f2QeTyVu4R971aYDAfB1FfeFbkFQ0ikK8QfMtpEoreSu7pRwgliX23HJwaSVVKThZuYlHCWz13McvB-ddgvsxGoO6b_sGpgW3j6ooSpOVt6K3SFC8lXCMhnJivcq4CDfS5JrymnWmi0lzfPt6osvXPV7h4jIosb0h0u5QsWt9LfXtg"
GROUP_ID = "1928726787324383902"
HEADERS_JSON = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
HEADERS_AUTH = {"Authorization": f"Bearer {API_KEY}"}


def encode_image(path: Path) -> str:
    with path.open("rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")


def submit_task(image_b64: str, prompt: str, model: str = "I2V-01-Director") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "first_frame_image": f"data:image/png;base64,{image_b64}",
    }
    resp = requests.post(f"{API_BASE}/video_generation", headers=HEADERS_JSON, json=payload)
    resp.raise_for_status()
    logger.info(f'video generation task submitted output:\n {resp.text}')
    task_id = resp.json()["task_id"]
    logger.info(f"video generation task returns task_id {task_id}")
    return task_id


def wait_for_completion(task_id: str, interval: int = 20):
    url = f"{API_BASE}/query/video_generation?task_id={task_id}"
    while True:
        time.sleep(interval)
        resp = requests.get(url, headers=HEADERS_AUTH)
        resp.raise_for_status()
        data = resp.json()
        status = data["status"]
        logger.info(f'video file_id is {data["file_id"]}')
        if status == "Success":
            return data["file_id"]
        if status in ("Fail", "Unknown"):
            raise RuntimeError(f"Task ended with status: {status}")


def get_download_url(group_id: str, file_id: str) -> str:
    url = f"{API_BASE}/files/retrieve?GroupId={group_id}&file_id={file_id}"
    resp = requests.get(url, headers=HEADERS_AUTH)
    resp.raise_for_status()
    return resp.json()["file"]["download_url"]


def download_video(url: str, dst: Path) -> None:
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with dst.open("wb") as file, tqdm(
        total=total, unit="iB", unit_scale=True, desc=str(dst), unit_divisor=1024
    ) as bar:
        for chunk in resp.iter_content(chunk_size=8192):
            file.write(chunk)
            bar.update(len(chunk))


def main() -> None:
    image_path = Path("./resources/2.png")
    prompt = "Logos of companies appearing one by one"
    output_path = Path("./output2.mp4")

    logger.info('Starting video generation task')
    task_id = submit_task(encode_image(image_path), prompt)
    logger.info('Getting video file_id')
    file_id = wait_for_completion(task_id)
    logger.info('Getting video download_url')
    video_url = get_download_url(GROUP_ID, file_id)
    logger.info(f'video download_url is {video_url}')
    download_video(video_url, output_path)


if __name__ == "__main__":
    main()
