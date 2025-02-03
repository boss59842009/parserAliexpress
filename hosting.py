import cloudinary
import cloudinary.uploader

# Налаштування Cloudinary
# https://console.cloudinary.com/settings/c-6f5534e46e74f613fa802f99963078/api-keys
CLOUD_NAME = "dnghh41px"
API_KEY = "884367949269729"
API_SECRET = "IzJSTpOFNIhWYCC8Lm5bDnWbYJs"

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
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
