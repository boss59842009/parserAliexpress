import json
import csv
import os
import re


def get_item_info(item_data: tuple) -> dict:
    """
    Повертає інформацію про товар у вигляді словника.
    Об'єднує дані (опис, специфікації, ціни, фото, інші дані) із API.
    
    **Основні ціни для головного товару (які бачить користувач) визначаються за першим SKU:**
      - Якщо значення 'price' містить роздільник "-", то:
            NewPrice (DiscountPrice) = перша частина (мінімальна ціна)
            OldPrice (OriginalPrice) = друга частина (максимальна ціна)
      - Якщо роздільника немає:
            NewPrice (DiscountPrice) = значення з 'promotionPrice', якщо воно задане (не None і не пусте), інакше – значення 'price'
            OldPrice (OriginalPrice) = значення 'price'
    
    Додатково формується поле "SKUPriceRange" як рядок із діапазоном цін по всім варіантам.
    """
    item, reviews = item_data
    product_id = item["result"]['item']['itemId']
    
    # Формування специфікацій
    specs = item["result"]["item"]["properties"]["list"]
    specs_info = "\n".join(f"{spec['name']}: {spec['value']}" for spec in specs) if specs else ""
    
    # Отримання фото з відгуків
    reviews_photo = []
    try:
        for review in reviews['result']["resultList"]:
            imgs = review['review'].get("reviewImages")
            if imgs:
                reviews_photo.extend(imgs)
    except Exception:
        reviews_photo = []
    
    # Отримання інформації про доставку
    try:
        delivery_note = item["result"]["delivery"]["shippingList"][0]['note']
        if delivery_note and len(delivery_note) >= 2:
            main_delivery_option = f"{delivery_note[0]}\nDelivery: {delivery_note[1]}"
        else:
            main_delivery_option = ""
    except Exception:
        main_delivery_option = ''
    
    # Отримання основних фото з опису
    main_photo_links = ["https:" + image for image in item["result"]["item"]["description"]["images"]]
    reviews_photo_links = ["https:" + image for image in reviews_photo]
    
    # Отримання текстового опису: спочатку ключ "text", інакше очищення HTML з "html"
    description_obj = item["result"]["item"]["description"]
    description_text = description_obj.get("text", "").strip()
    if not description_text:
        raw_html = description_obj.get("html", "")
        description_text = re.sub(r'<[^>]*>', '', raw_html).strip()

    original_price = item.get('result', {}).get("item", {}).get("sku", {}).get("def", {}).get("price", "")
    discount_price = item.get('result', {}).get("item", {}).get("sku", {}).get("def", {}).get("promotionPrice", "")
  
    return {

        "Link": "https:" + item["result"]["item"]["itemUrl"],
        "Title": item["result"]["item"]["title"],
        "DiscountPrice": discount_price if discount_price else "",
        "OriginalPrice": original_price if original_price else "",
        "Rating": float(item["result"]["reviews"]["averageStar"]),
        "Likes": item["result"]["item"]["wishCount"],
        "MainDeliveryOption": main_delivery_option,
        "Description": description_text,
        "Specifications": specs_info,
        "MainPhotoLinks": main_photo_links,
        "ReviewsPhotoLinks": reviews_photo_links,
        "HostingFolderLink": [
            f"https://res.cloudinary.com/dnghh41px/{product_id}/MainPhotos",
            f"https://res.cloudinary.com/dnghh41px/{product_id}/PhotoReview"
        ],
    }

def get_items_list_from_query(items: dict):
    """Повертає список ID товарів із результатів пошукового запиту."""
    return [item['item']['itemId'] for item in items['result']['resultList']]

def get_shopify_one_item(items: dict, photos_url: list[str]) -> list[dict]:
    """
    Формує дані для Shopify.
    Поле Body (HTML) формується як об'єднання Specifications і Description.
    Для цін:
      - DiscountPrice використовується для колонок Price / International і Variant Price,
      - OriginalPrice – для колонок Compare At Price / International і Variant Compare At Price.
    """
    body_html = (items.get("Specifications", "") + "\n" + items.get("Description", "")).strip()
    shopify_items = []
    
    main_row = {
        "Title": items.get("Title", ""),
        "Body (HTML)": body_html,
        "Vendor": "",
        "Product Category": "Uncategorized",
        "Type": "",
        "Tags": items.get("Title", ""),
        "Published": False,
        "Option1 Name": "",
        "Option1 Value": "",
        "Option2 Name": "",
        "Option2 Value": "",
        "Option3 Name": "",
        "Option3 Value": "",
        "Variant SKU": "",
        "Variant Grams": "",
        "Variant Inventory Tracker": "shopify",
        "Variant Inventory Qty": 100,
        "Variant Inventory Policy": "continue",
        "Variant Fulfillment Service": "manual",
        "Variant Price": "",
        "Variant Compare At Price": "",
        "Variant Requires Shipping": "",
        "Variant Taxable": "",
        "Variant Barcode": "",
        "Image Src": photos_url[0] if photos_url else "",
        "Image Position": 1,
        "Image Alt Text": "",
        "Gift Card": "",
        "SEO Title": "",
        "SEO Description": "",
        "Google Shopping / Google Product Category": "",
        "Google Shopping / Gender": "",
        "Google Shopping / Age Group": "",
        "Google Shopping / MPN": "",
        "Google Shopping / AdWords Grouping": "",
        "Google Shopping / AdWords Labels": "",
        "Google Shopping / Condition": "",
        "Google Shopping / Custom Product": "",
        "Google Shopping / Custom Label 0": "",
        "Google Shopping / Custom Label 1": "",
        "Google Shopping / Custom Label 2": "",
        "Google Shopping / Custom Label 3": "",
        "Google Shopping / Custom Label 4": "",
        "Variant Image": "",
        "Variant Weight Unit": "",
        "Variant Tax Code": "",
        "Cost per item": "",
        "Price / International": items.get("DiscountPrice", ""),
        "Compare At Price / International": "",
        "Status": "draft"
    }
    shopify_items.append(main_row)
    
    for i in range(1, len(photos_url)):
        extra_row = {
            "Title": "",
            "Body (HTML)": "",
            "Vendor": "",
            "Product Category": "",
            "Type": "",
            "Tags": "",
            "Published": "",
            "Option1 Name": "",
            "Option1 Value": "",
            "Option2 Name": "",
            "Option2 Value": "",
            "Option3 Name": "",
            "Option3 Value": "",
            "Variant SKU": "",
            "Variant Grams": "",
            "Variant Inventory Tracker": "",
            "Variant Inventory Qty": "",
            "Variant Inventory Policy": "",
            "Variant Fulfillment Service": "",
            "Variant Price": "",
            "Variant Compare At Price": "",
            "Variant Requires Shipping": "",
            "Variant Taxable": "",
            "Variant Barcode": "",
            "Image Src": photos_url[i],
            "Image Position": i + 1,
            "Image Alt Text": "",
            "Gift Card": "",
            "SEO Title": "",
            "SEO Description": "",
            "Google Shopping / Google Product Category": "",
            "Google Shopping / Gender": "",
            "Google Shopping / Age Group": "",
            "Google Shopping / MPN": "",
            "Google Shopping / AdWords Grouping": "",
            "Google Shopping / AdWords Labels": "",
            "Google Shopping / Condition": "",
            "Google Shopping / Custom Product": "",
            "Google Shopping / Custom Label 0": "",
            "Google Shopping / Custom Label 1": "",
            "Google Shopping / Custom Label 2": "",
            "Google Shopping / Custom Label 3": "",
            "Google Shopping / Custom Label 4": "",
            "Variant Image": "",
            "Variant Weight Unit": "",
            "Variant Tax Code": "",
            "Cost per item": "",
            "Price / International": "",
            "Compare At Price / International": "",
            "Status": ""
        }
        shopify_items.append(extra_row)
    return shopify_items


def save_json(items: dict | list[dict], folder: str) -> None:
    """
    Зберігає дані у JSON файл у вказаній папці.
    Якщо папки не існує, вона буде створена.
    """
    os.makedirs(folder, exist_ok=True)
    file_path = f"{folder}/{folder}.json"
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(items, file, ensure_ascii=False, indent=4)
    print("JSON файл успішно збережено!")


def save_csv(items: dict | list[dict], folder: str) -> None:
    """
    Зберігає дані у CSV файл у вказаній папці.
    Якщо папки не існує, вона буде створена.
    """
    os.makedirs(folder, exist_ok=True)
    file_path = f"{folder}/{folder}.csv"
    if isinstance(items, dict):
        items["MainPhotoLinks"] = ",".join(items["MainPhotoLinks"])
        items["ReviewsPhotoLinks"] = ",".join(items["ReviewsPhotoLinks"])
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=items.keys())
            writer.writeheader()
            writer.writerow(items)
    else:
        
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=items[0].keys())
            writer.writeheader()
            for item in items:
                if isinstance(item.get("MainPhotoLinks"), list):
                    item["MainPhotoLinks"] = ",".join(item["MainPhotoLinks"])
                if isinstance(item.get("ReviewsPhotoLinks"), list):
                    item["ReviewsPhotoLinks"] = ",".join(item["ReviewsPhotoLinks"])
                writer.writerow(item)
    print("CSV файл успішно збережено!")

def save_shopify_csv_one_item(items: list[dict] | dict, folder: str) -> None:
    """
    Зберігає дані для Shopify (один товар) у CSV файл у вказаній папці.
    Усі рядки одного товару отримують однаковий Handle.
    """
    if isinstance(items, dict):
        items = [items]
    fieldnames = ["Handle"] + list(items[0].keys())
    os.makedirs(folder, exist_ok=True)
    file_path = f"{folder}/{folder}_shopify.csv"
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        count = 1
        for item in items:
            writer.writerow({"Handle": count, **item})
            count += 1
    print("Shopify CSV файл успішно збережено!")


def save_shopify_csv_list_items(items: list[list[dict]], folder: str) -> None:
    """
    Зберігає дані для Shopify (список товарів) у один CSV файл у вказаній папці.
    """
    os.makedirs(folder, exist_ok=True)
    fieldnames = ["Handle"] + list(items[0][0].keys())
    file_path = f"{folder}/{folder}_shopify.csv"
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        count = 1
        for product_items in items:
            for item in product_items:
                writer.writerow({"Handle": count, **item})
                count += 1
    print("Shopify CSV файл успішно збережено!")
