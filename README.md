
# AliExpress Parser

**AliExpress Parser** is a Python-based tool designed to extract detailed product information from AliExpress. It retrieves product details via RapidAPI, processes pricing and SKU information, uploads product images to Cloudinary, and generates output files in JSON, CSV, and Shopify CSV formats. The project features a minimalistic PyQt5 graphical interface, making it ideal for developers who need a straightforward yet powerful parsing solution.

---

## Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Requirements](#requirements)
4. [Installation and Setup](#installation-and-setup)
5. [Configuration](#configuration)
    - [RapidAPI Setup](#rapidapi-setup)
    - [Cloudinary Setup](#cloudinary-setup)
    - [Resource Files (Icons/Favicon)](#resource-files-iconsfavicon)
6. [Running the Application](#running-the-application)
7. [Building the Executable](#building-the-executable)
8. [Technical Details](#technical-details)
9. [Troubleshooting](#troubleshooting)
10. [License](#license)

---

## 1. Features(#features)

- **Multiple Parsing Modes:**
  - **Single:** Parse a single product by its URL.
  - **Query:** Parse multiple products from a search query URL with a user-specified limit.
  - **Multiple:** Parse several products from a comma-separated list of product URLs.
- **Data Extraction:**
  - Retrieve product details including title, merged description and specifications, rating, likes, and delivery options.
  - **Pricing Information:**
    - **Main Prices:** The first SKU variant (i.e., the product the user sees upon opening the page) is used to determine:
      - **DiscountPrice (NewPrice):**  
        - If the first SKU’s `price` field contains a range (e.g. `"96.46 - 127.37"`), the lower (first) value is used.
        - Otherwise, if the SKU’s `promotionPrice` is provided, that value is used; if not, the value from `price` is used.
      - **OriginalPrice (OldPrice):**  
        - If the first SKU’s `price` contains a range, the higher (second) value is used.
        - Otherwise, the value from `price` is used.
    - **SKUPriceRange:** A single, human-readable string (e.g., `"6.70 - 7.06"`) representing the overall price range among all SKU variants.
- **Photo Upload:**  
  Automatically uploads product images (both main and review images) to Cloudinary.
- **Output Files:**
  - **JSON:** Contains complete product details.
  - **CSV:** Contains basic product data.
  - **Shopify CSV:** Formatted for direct import into Shopify.
- **User Interface:**  
  A clean, developer-focused PyQt5 GUI that provides real-time progress and log messages during parsing.

---

## 2. Project Structure

AliExpress Parser/


├── ali_parse.py #Parsing module (renamed from parse.py to avoid circular imports) 

├── data.py #Data processing and file output (JSON, CSV, Shopify CSV) 

├── funcionality.py #Core parsing logic and threading for the UI

├── hosting.py #Cloudinary integration for uploading photos 

├── main.py # Main PyQt5 GUI application entry point

├── qss.py # Stylesheet for the PyQt5 interface 

├── README.md # This document 

└── requirements.txt # List of Python dependencies



> **Note:**  
> If your project originally had a module named `parse.py`, it has been renamed to `ali_parse.py` to prevent circular import conflicts.

---

## 3. Requirements

- **Python:** 3.12 or later
- **PyQt5:** For the graphical user interface
- **Requests-HTML:** For JavaScript rendering (if needed)
- **Cloudinary:** (using the `cloudinary` package) for photo uploads
- **RapidAPI Credentials:** API key to access AliExpress data via RapidAPI
- **Additional Libraries:** See `requirements.txt` for the complete dependency list

---

## 4. Installation and Setup

1. **Clone the Repository:**

   ```bash
   git clone https://your-repository-url.git
   cd parserAli
Create a Virtual Environment:

     
    python -m venv venv
    Activate the Virtual Environment:

Windows:

    venv\Scripts\activate
Linux/macOS:

    source venv/bin/activate
Install Dependencies:


    pip install -r requirements.txt

Ensure your requirements.txt includes at least:

    PyQt5
    requests-html
    cloudinary
#(Other packages required by the project)

## 5. Configuration
RapidAPI Setup
The project uses RapidAPI to access AliExpress data. Update the API key in the appropriate module (usually in ali_parse.py or funcionality.py):

    headers = {
        "x-rapidapi-key": "YOUR_RAPIDAPI_KEY",
        "x-rapidapi-host": "aliexpress-datahub.p.rapidapi.com"
    }
Replace "YOUR_RAPIDAPI_KEY" with your actual RapidAPI key.

Cloudinary Setup
Open the file hosting.py and update your Cloudinary credentials:


    CLOUD_NAME = "cloud_name"
    API_KEY = "api_key"
    API_SECRET = "api_secret"

Replace these values with your own Cloudinary account details if necessary.

Resource Files (Icons/Favicon)
Using an Icon File:
Place your icon file (e.g., ico.png) in the same directory as main.py. In main.py, set the icon as follows:


    self.setWindowIcon(QIcon('ico.png'))
Using a Qt Resource File (Optional):

Create a file named resources.qrc with the following content:


    <!DOCTYPE RCC>
    <RCC version="1.0">
    <qresource prefix="/">
        <file>ico.png</file>
    </qresource>
    </RCC>
Compile the resource file:


    pyrcc5 resources.qrc -o resources_rc.py
In main.py, import the resource and set the icon:

    import resources_rc
    self.setWindowIcon(QIcon(":/ico.png"))
## 6. Running the Application
To launch the application, run:


    python main.py
The PyQt5 interface will open. In the interface you can:

**Enter a URL / Query:**
Input a single product URL, a search query URL, or a comma-separated list of product URLs.

**Select the Parsing Mode:
Choose one of the following modes:**

**Single:** 
    Parse one product.

**Query:** Parse multiple products from a search query (with a configurable limit).

**Multiple:** Parse several products from a comma-separated list of URLs.

**Set a Limit (for Query Mode):**
Specify the maximum number of products to parse from the query.

**Start Parsing:**
Click the "Start Parsing" button. The interface will display a progress bar and log messages indicating the status.

After parsing completes, the application generates three output files in a folder named after the product ID (or a common folder for multiple products):

    <foldername>.json – Contains complete product data.
    <foldername>.csv – Contains basic product details.
    <foldername>_shopify.csv – Formatted for Shopify import.

**Price Fields:**

The main prices (DiscountPrice and OriginalPrice) are taken from the first SKU variant—the product that the user sees when they open the page.
The SKUPriceRange field shows a concise price range (e.g., "6.70 - 7.06") across all SKU variants.
7. Building the Executable
You can build a standalone executable using PyInstaller. Run the following command:


    pyinstaller --onefile --windowed main.py


**Notes:**

Ensure that all required resource files (e.g., icons) are included. You may need to modify the generated .spec file (for example, add datas=[('ico.png', '.')]).
The final executable will be located in the dist folder after the build process completes.

## 8. Technical Details
**Parsing Modes:**

**Single:**
Parses a single product.

**Query:** Parses multiple products from a search query URL.

**Multiple:** Parses several products from a comma-separated list of URLs.

**Data Extraction:**
Uses the AliExpress API via RapidAPI to retrieve product details.
Merges Description and Specifications into a single field for the Shopify CSV’s Body (HTML).

**Pricing:**
The first SKU variant is used to determine the main product prices:
DiscountPrice (NewPrice):
If the price field of the first SKU contains a range (e.g., "96.46 - 127.37"), the lower (first) value is used.
Otherwise, if promotionPrice is provided, that value is used; if not, the value from price is used.

**OriginalPrice (OldPrice):**
If the price field contains a range, the higher (second) value is used.
Otherwise, the value from price is used.

**SKUPriceRange:** Generated by scanning all SKU variants, computing the overall minimum and maximum prices, and formatting them as a single string (e.g., "6.70 - 7.06").

**Output Files:**

***JSON:***
Contains all parsed product data.

***CSV:*** Contains basic product information.

***Shopify CSV:*** Formatted for easy import into Shopify.

**Photo Upload:**
Product images (both main and review) are automatically uploaded to Cloudinary as configured in hosting.py.

## 9. Troubleshooting
**Circular Import Errors:**

If you encounter errors related to circular imports (e.g., with a module named parse), ensure that your local parsing module has been renamed (e.g., to ali_parse.py) and update all corresponding import statements.

**Missing Dependencies:**

Verify that all required packages are installed by reviewing the requirements.txt file.

**API & Cloudinary Credentials:**

Double-check that your RapidAPI key and Cloudinary credentials are correctly entered in the configuration files ***(in ali_parse.py/funcionality.py and hosting.py)***.

**Resource Files Not Found:**
If icons or other resource files do not appear in the built executable, update the PyInstaller .spec file to include these files ***(e.g., add datas=[('ico.png', '.')])***.

**Price Data Issues:**
If the prices (DiscountPrice, OriginalPrice, or SKUPriceRange) are not displayed correctly, print the raw SKU data (e.g., using print(json.dumps(sku_info, indent=4))) to inspect the structure returned by the API, then adjust key access in the code as needed.

## 10. License 
**[Your License Information Here]**

