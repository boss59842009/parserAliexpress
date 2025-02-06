import json
import os
from datetime import datetime

import requests
from data import (get_item_info, get_shopify_one_item, get_items_list_from_query,
                  save_json, save_csv, save_shopify_csv_one_item, save_shopify_csv_list_items)
from hosting import upload_photos
from dotenv import load_dotenv
load_dotenv()

headers = {
    "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
    "x-rapidapi-host": "aliexpress-datahub.p.rapidapi.com"
}

def get_item_id_from_url(link: str) -> str:
    """Повертає ID товару з посилання."""
    try:
        segment = link.split('/')[4]
        return segment.split('.')[0]
    except IndexError:
        return ""

def get_query_from_url(link: str) -> str:
    """Повертає пошуковий запит з посилання."""
    try:
        segment = link.split('/')[4]
        return segment[10:].split('.')[0]
    except IndexError:
        return ""

def parse_item(headers: dict, item_id: str) -> tuple[dict, dict] | None:
    """Повертає дані про товар за ID із сайту."""
    url = "https://aliexpress-datahub.p.rapidapi.com/item_detail_7"
    url_reviews = "https://aliexpress-datahub.p.rapidapi.com/item_review"
    querystring = {"itemId": item_id, "region": "US"}
    querystring_reviews = {"itemId": item_id, "page": "1", "sort": "default", "filter": "allReviews"}
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            data_item = response.json()
            if data_item.get("result", {}).get("status", {}).get("data") == "error":
                return None
        else:
            return None
    except Exception as e:
        return None

    try:
        response_reviews = requests.get(url_reviews, headers=headers, params=querystring_reviews, timeout=10)
        if response_reviews.status_code == 200:
            data_reviews = response_reviews.json()
            if data_reviews.get("result", {}).get("status", {}).get("data") == "error":
                data_reviews = None
        else:
            data_reviews = None
    except Exception:
        data_reviews = None

    return data_item, data_reviews


def parse_query(headers: dict, query: str) -> dict:
    """Повертає дані про товари за пошуковим запитом."""
    url_query = "https://aliexpress-datahub.p.rapidapi.com/item_search_4"
    querystring = {"q": query, "page": "1", "sort": "default", "region": "US"}
    try:
        response = requests.get(url_query, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            query_items = response.json()
            if query_items.get("result", {}).get("status", {}).get("data") == "error":
                return {}
            return query_items
        else:
            return {}
    except Exception:
        return {}


def parse_item_from_link(link: str) -> None:
    """Парсинг та збереження одного товару за посиланням."""
    item_id = get_item_id_from_url(link)
    item_data = parse_item(headers, item_id)
    if item_data:
        item_dict = get_item_info(item_data)
        save_json(item_dict, item_id)
        save_csv(item_dict.copy(), item_id)
        main_photos_url = upload_photos(item_dict["MainPhotoLinks"], f"{item_id}/MainPhotos")
        upload_photos(item_dict["ReviewsPhotoLinks"], f"{item_id}/PhotoReview")
        shopify_info = get_shopify_one_item(item_dict, main_photos_url)
        save_shopify_csv_one_item(shopify_info, item_id)


def parse_items_from_links(headers: dict, items_id: list, filename: str = "list_items") -> None:
    """Парсинг та збереження багатьох товарів із списку."""
    items = []
    shopify_list = []
    for item_id in items_id:
        item_data = parse_item(headers, item_id)
        if item_data:
            item_dict = get_item_info(item_data)
            items.append(item_dict)
            main_photos_url = upload_photos(item_dict["MainPhotoLinks"], f"{item_id}/MainPhotos") if item_dict["MainPhotoLinks"] else []
            if item_dict["ReviewsPhotoLinks"]:
                upload_photos(item_dict["ReviewsPhotoLinks"], f"{item_id}/PhotoReview")
            shopify_info = get_shopify_one_item(item_dict, main_photos_url)
            shopify_list.append(shopify_info)
    if items and shopify_list:
        save_json(items, filename)
        save_csv(items, filename)
        save_shopify_csv_list_items(shopify_list, filename)


def parse_items_from_query(headers: dict, query: str, items_count: int) -> None:
    """Парсинг багатьох товарів за пошуковим запитом (не більше 60)."""
    links_list = parse_query(headers, query)
    if links_list:
        items_list = get_items_list_from_query(links_list)
        if items_count:
            parse_items_from_links(headers, items_list[:items_count], "list_items_from_query")


