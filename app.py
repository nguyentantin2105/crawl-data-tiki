import requests
import json
import csv
import re
import xlwt
from xlwt import Workbook

laptop_page_url = "https://tiki.vn/api/v2/products?limit=48&include=advertisement&aggregations=1&category={}&page={}"

# laptop_page_url = "https://tiki.vn/api/v2/products?limit=48&include=advertisement&aggregations=1&category=1846&page={}&urlKey=laptop-may-vi-tinh-linh-kien"
product_url = "https://tiki.vn/api/v2/products/{}"
category_url = "https://tiki.vn/api/shopping/v2/mega_menu"

category_id_file = "./data/category-id.txt"
product_id_file = "./data/product-id.txt"
product_data_file = "./data/product.txt"
product_file = "./data/product.csv"

headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}

def crawl_category_id():
    category_list = []
    urls = []
    response = requests.get(category_url, headers=headers)
    for i in response.json()["data"]:
        urls.append(i["item"]["url"])
    
    for j in urls:
        categoryId = re.findall(r'\d+',j)
        if j!="":
            category_list.append(categoryId[0])
    return category_list

def save_category_id(category_list=[]):
    file = open(category_id_file, "w+")
    str = "\n".join(category_list)
    file.write(str)
    file.close()
    print("Save file: ", category_id_file)

category_list = crawl_category_id()
save_category_id(category_list)

def crawl_product_id():
    product_list = []
    i = 1
    category_list = crawl_category_id()
    for j in category_list:
        for i in range(1,45):
            print("Crawl page: ", i)
            print(laptop_page_url.format(j,i))
            
            response = requests.get(laptop_page_url.format(j,i), headers=headers)
            
            if (response.status_code != 200):
                break

            products = response.json()["data"]
            print(products)

            if (len(products) == 0):
                break

            for product in products:
                product_id = str(product["id"])
                print("Product ID: ", product_id)
                product_list.append(product_id)

    return product_list

product_list = crawl_product_id()

def save_product_id(product_list=[]):
    file = open(product_id_file, "w+")
    str = "\n".join(product_list)
    file.write(str)
    file.close()
    print("Save file: ", product_id_file)

save_product_id(product_list)

def crawl_product(product_list=[]):
    product_detail_list = []
    for product_id in product_list:
        response = requests.get(product_url.format(product_id), headers=headers)
        if (response.status_code == 200):
            product_detail_list.append(response.text)
            print("Crawl product: ", product_id, ": ", response.status_code)
    return product_detail_list

flatten_field = [ "badges", "inventory", "categories", "rating_summary", 
                      "brand", "seller_specifications", "current_seller", "other_sellers", 
                      "configurable_options",  "configurable_products", "specifications", "product_links",
                      "services_and_promotions", "promotions", "stock_item", "installment_info" ]


def adjust_product(product):
    e = json.loads(product)
    if not e.get("id", False):
        return None

    for field in flatten_field:
        if field in e:
            e[field] = json.dumps(e[field], ensure_ascii=False).replace('\n','')

    return e

def save_raw_product(product_detail_list=[]):
    file = open(product_data_file, "w+", encoding="utf-8")
    str = "\n".join(product_detail_list)
    file.write(str)
    file.close()
    print("Save file: ", product_data_file)

def load_raw_product():
    file = open(product_data_file, "r+", encoding="utf-8")
    return file.readlines()

def save_product_list(product_json_list):
    file = open(product_file, "w", encoding='utf-8')
    csv_writer = csv.writer(file)

    count = 0
    for p in product_json_list:
        if p is not None:
            if count == 0:
                header = p.keys() 
                csv_writer.writerow(header) 
                count += 1
            csv_writer.writerow(p.values())
    file.close()
    print("Save file: ", product_file)

product_list = crawl_product(product_list)

# save product detail for backup
save_raw_product(product_list)

product_list = load_raw_product()
# flatten detail before converting to csv
product_json_list = [adjust_product(p) for p in product_list]
# # save product to csv
save_product_list(product_json_list)





    

