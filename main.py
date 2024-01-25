from bs4 import BeautifulSoup
import requests
import json
import os
from urllib.parse import urljoin
# import calendar
import tkinter as tk
from tkinter import simpledialog, filedialog

def fetch_json_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    #Getting the json of images
    script_content = soup.find_all('script')[2].contents[0]

    #Cleaning the script content up for json parsing
    json_data = script_content.replace('var images =', '') #removing js bits
    json_data = json_data.replace("'", '"') #single to double quotes
    json_data = json_data[:-2] #strip semi-colon
    json_data = json_data.rsplit(',', 1)[0] + json_data.rsplit(',', 1)[1].replace(',', '') #remove trailing delim

    # Replace single quotes around keys with double quotes
    json_data = json_data.replace('id:', '"id":')
    json_data = json_data.replace('title:', '"title":')
    json_data = json_data.replace('width:', '"width":')
    json_data = json_data.replace('height:', '"height":')
    json_data = json_data.replace('src:', '"src":')
    json_data = json_data.replace('url:', '"url":')
    json_data = json_data.replace('potw:', '"potw":')

    return json.loads(json_data)

def download_image(url, save_folder):
    #make dir if need be
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    #getting the div containing all the download links
    download_links = soup.find_all('div', class_='archive_download')


    for download_link in download_links:
        if 'Large JPEG' in download_link.text: 
            large_jpg_url = urljoin(url, download_link.select_one('.archive_dl_text a').get('href')) #Getting the proper URL for the Large JPEG
            
            response = requests.get(large_jpg_url)

            #naming the file probably needs some changes. Originally I was only getting the pictures of the month but now it can grab from any gallery but they lack the same naming conventions. For now this will be commented out
            filename = large_jpg_url.split('/')[-1]  #grabbing the end bit 'YYMM.jpg'
            # year, month = filename[4:6], int(filename[6:8]) 
            # month_name = calendar.month_name[month]
            # filename = f'20{year} - {month_name}.jpg'

            # Combining the folder path and filename to save the image
            save_path = os.path.join(save_folder, filename)
            
            #Writing the file
            with open(save_path, 'wb') as file_writer:
                file_writer.write(response.content)
            print(f'Fullsize Image Saved: {save_path}')

def fetchImageListAndDownload(url, save_folder='images'):
    data = fetch_json_data(url)
    src_urls = [urljoin(url, entry['url']) for entry in data]
    for src_url in src_urls:
        download_image(src_url, save_folder)


class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title, website_label, folder_label, default_website_url=''):
        self.website_label = website_label
        self.folder_label = folder_label
        self.default_website_url = default_website_url
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.website_label).grid(row=0)
        tk.Label(master, text=self.folder_label).grid(row=1)

        self.website_entry = tk.Entry(master)
        self.folder_entry = tk.Entry(master)

        # Set default value for website URL
        self.website_entry.insert(0, self.default_website_url)

        self.website_entry.grid(row=0, column=1)
        self.folder_entry.grid(row=1, column=1)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2)

    def apply(self):
        self.result = (self.website_entry.get(), self.folder_entry.get())

    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)

def get_inputs():
    root = tk.Tk()
    root.withdraw()

     # Set a default website URL
    default_website_url = "https://esawebb.org/images/archive/category/pictureofthemonth/"

    # Create a custom dialog with labels for website and folder
    dialog = CustomDialog(root, "ESA / Webb Scraper", "Enter Gallery URL:", "Enter Folder Path:", default_website_url)

    # Get the result (tuple containing website URL and folder path)
    result = dialog.result

    # Print the values for verification
    if result:
        website_url, folder_path = result
        print(f"Website URL: {website_url}")
        print(f"Folder Path: {folder_path}")
    
    return result



if __name__ == '__main__':
    website_url, folder_path = get_inputs()
    fetchImageListAndDownload(website_url, folder_path)