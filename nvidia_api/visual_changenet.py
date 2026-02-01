import uuid
import zipfile
import os
import requests
from config.settings import NVIDIA_API_URL, NVIDIA_API_KEY


HEADER_AUTH = f"Bearer {NVIDIA_API_KEY}"


def upload_asset(image_path: str, description: str) -> str:
    """
    Uploads an image to NVIDIA NVCF and returns asset ID
    """
    with open(image_path, "rb") as f:
        binary = f.read()

    authorize = requests.post(
        "https://api.nvcf.nvidia.com/v2/nvcf/assets",
        headers={
            "Authorization": HEADER_AUTH,
            "Content-Type": "application/json",
            "accept": "application/json",
        },
        json={
            "contentType": "image/jpeg",
            "description": description
        },
        timeout=30,
    )
    authorize.raise_for_status()

    upload_url = authorize.json()["uploadUrl"]
    asset_id = authorize.json()["assetId"]

    response = requests.put(
        upload_url,
        data=binary,
        headers={
            "x-amz-meta-nvcf-asset-description": description,
            "content-type": "image/jpeg",
        },
        timeout=300,
    )
    response.raise_for_status()

    return asset_id


def run_visual_changenet(
    reference_image: str,
    test_image: str,
    output_dir: str
) -> str:
    """
    Runs Visual ChangeNet on two images and extracts results
    """

    os.makedirs(output_dir, exist_ok=True)

    asset_id1 = upload_asset(reference_image, "Reference Image")
    asset_id2 = upload_asset(test_image, "Test Image")

    inputs = {
        "reference_image": asset_id1,
        "test_image": asset_id2
    }

    asset_list = f"{asset_id1},{asset_id2}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": HEADER_AUTH,
        "NVCF-INPUT-ASSET-REFERENCES": asset_list,
        "NVCF-FUNCTION-ASSET-IDS": asset_list,
    }

    response = requests.post(
        NVIDIA_API_URL,
        headers=headers,
        json=inputs,
        timeout=300
    )
    response.raise_for_status()

    zip_path = os.path.join(output_dir, "changenet_output.zip")

    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(output_dir)

    return output_dir
