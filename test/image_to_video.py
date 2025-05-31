import requests
import base64

from tqdm import tqdm

url = "https://api.minimaxi.chat/v1/video_generation"
api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJhZGl0eWEgbGFraGUiLCJVc2VyTmFtZSI6ImFkaXR5YSBsYWtoZSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTI4NzI2Nzg3MzI4NTc4MjA2IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTkyODcyNjc4NzMyNDM4MzkwMiIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6ImFkaXR5YWxha2hlNUBnbWFpbC5jb20iLCJDcmVhdGVUaW1lIjoiMjAyNS0wNS0zMSAxOTozNDoxOSIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.PpvFaPS_vXtQO6Tq4r3DcHBo3uqMEqdX3p0PrWOfrJHJ4i_mB8YBpe6iGt1qB60Fw6J54vJae3cKos8pOSQJENAOtSWDH61SGf4A8yFLEFd62eUXygqcpXQs1HwnAN60syqw6RmGavWg9kP5W63xfhDOULqKkjlO7FPoRbF4f2QeTyVu4R971aYDAfB1FfeFbkFQ0ikK8QfMtpEoreSu7pRwgliX23HJwaSVVKThZuYlHCWz13McvB-ddgvsxGoO6b_sGpgW3j6ooSpOVt6K3SFC8lXCMhnJivcq4CDfS5JrymnWmi0lzfPt6osvXPV7h4jIosb0h0u5QsWt9LfXtg"
image_path = "/Users/i0d02fk/Desktop/dev/IMS/LoraSuckers/test/resources/1.png"

with open(image_path, "rb") as image_file:
    data = base64.b64encode(image_file.read()).decode('utf-8')

payload = {
    "model": "I2V-01-Director",
    "prompt": "Thermometer filling up and blowing",
    "first_frame_image": f"data:image/png;base64,{data}"
}

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# response = requests.post(url, headers=headers, json=payload)
#
# try:
#     response.raise_for_status()
#     print("response",response.json())
# except requests.exceptions.RequestException as e:
#     print(f"Request failed: {e}")


#
# task_id="275003969912990"
#
# url = f"http://api.minimaxi.chat/v1/query/video_generation?task_id={task_id}"
#
# payload = {}
# headers = {
#   'authorization': f'Bearer {api_key}',
#   'content-type': 'application/json',
# }
#
# response = requests.request("GET", url, headers=headers, data=payload)
#
# print(response.text)

file_id = 275004606845079
group_id = 1928726787324383902

url = f'https://api.minimaxi.chat/v1/files/retrieve?GroupId={group_id}&file_id={file_id}'
headers = {
    'authority': 'api.minimaxi.chat',
    'content-type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

response = requests.get(url, headers=headers)
video_url = response.json()['file']['download_url']
print(video_url)


def download_video(url, output_path=None):
    """
    Download a video from a URL with progress bar.

    Args:
        url (str): URL of the video to download
        output_path (str, optional): Path where the video will be saved.
                                   If not provided, will use the filename from the URL.

    Returns:
        str: Path to the downloaded video file
    """
    try:
        # If no output path is provided, use the filename from the URL
        if output_path is None:
            output_path = url.split('/')[-1]
            # Remove any query parameters from the filename
            output_path = output_path.split('?')[0]

        # Send a GET request to the URL with stream=True to download in chunks
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Get the total file size
        total_size = int(response.headers.get('content-length', 0))

        # Open the output file and download with progress bar
        with open(output_path, 'wb') as file, tqdm(
                desc=output_path,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as progress_bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                progress_bar.update(size)

        print(f"Successfully downloaded video to {output_path}")
        return output_path

    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None


download_video(video_url , "./downloaded_video.mp4")