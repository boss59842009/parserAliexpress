import os

import cloudinary
import cloudinary.uploader

from dotenv import load_dotenv

# Налаштування Cloudinary
# https://console.cloudinary.com/settings/c-6f5534e46e74f613fa802f99963078/api-keys
load_dotenv()


cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True
)

def upload_photos(photo_links: list, folder_name: str) -> list[str]:
    """
    Завантажує фото на хостинг та повертає список посилань на завантажені фото.
    """
    photos_url = []
    for photo_link in photo_links:
        if not photo_link:
            continue
        try:
            response = cloudinary.uploader.upload(photo_link, folder=folder_name)
            secure_url = response.get("secure_url")
            if secure_url:
                photos_url.append(secure_url)
        except Exception:
            continue
    return photos_url
