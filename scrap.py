import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import time
import threading
from tkinter import ttk
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

host = "smtp-mail.outlook.com"
port = 587
fr = "" #From Mail
t = "" #To Mail
password = "" #password of from mail
class AmazonPriceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Price Tracker")

        self.products = []

        self.product_label = tk.Label(root, text="Product Name:")
        self.product_label.grid(row=0, column=0, padx=5, pady=5)
        self.product_entry = tk.Entry(root, width=30)
        self.product_entry.grid(row=0, column=1, padx=5, pady=5)

        self.link_label = tk.Label(root, text="Link:")
        self.link_label.grid(row=1, column=0, padx=5, pady=5)
        self.link_entry = tk.Entry(root, width=30)
        self.link_entry.grid(row=1, column=1, padx=5, pady=5)

        self.price_label = tk.Label(root, text="Target Price:")
        self.price_label.grid(row=2, column=0, padx=5, pady=5)
        self.price_entry = tk.Entry(root, width=10)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        self.add_button = tk.Button(root, text="Add Product", command=self.add_product)
        self.add_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.tree = ttk.Treeview(root, columns=('Product Name', 'Current Price', 'Target Price'))
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.tree.heading('#0', text='ID')
        self.tree.heading('#1', text='Product Name')
        self.tree.heading('#2', text='Current Price')
        self.tree.heading('#3', text='Target Price')

        self.track_button = tk.Button(root, text="Start Tracking", command=self.start_tracking)
        self.track_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.reset_button = tk.Button(root, text="Reset", command=self.reset_table)
        self.reset_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    def add_product(self):
        product_name = self.product_entry.get()
        amazon_link = self.link_entry.get()
        target_price = float(self.price_entry.get())

        self.products.append({'name': product_name, 'link': amazon_link, 'target': target_price})

        self.tree.insert('', 'end', text=str(len(self.products)), values=(product_name, 'N/A', target_price))

        self.product_entry.delete(0, tk.END)
        self.link_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def start_tracking(self):
        self.track_button.config(state="disabled")

        for index, product in enumerate(self.products):
            threading.Thread(target=self.monitor_price, args=(index, product)).start()

    def monitor_price(self,index, product):
        headers = {'User-Agent': ''}#your user agent
        while True:
            try:
                page = requests.get(product['link'], headers=headers)
                soup = BeautifulSoup(page.content, 'html.parser')
                product_price_str = soup.find(class_='_30jeq3 _16Jk6d').get_text()[1:]
                product_price = float(product_price_str.replace(',', ''))

                print(f"Price: {product_price}")
                self.reset_table()
                
                self.tree.insert('', 'end', text=product['name'], values=(product['name'], product_price, product['target']))

                # if product_price <= product['target']:
                #     messagebox.showinfo("Price Alert",
                #                         f"{product['name']} is now available for ${product_price} (<= ${product['target']})!")
                #     break
                if product_price <= product['target']:
                    self.send_email_notification(product['name'], product_price, product['target'])
                    break
            except Exception as e:
                print("An error occurred:", e)
            
            time.sleep(60)  

        self.track_button.config(state="normal")
    def send_email_notification(self, product_name, current_price, target_price):
        print('inside')
        message = MIMEMultipart()
        message["From"] = fr
        message["To"] = t
        message["Subject"] = "Price Alert: {0}".format(product_name)

        body = "{0} is now available for {1} (<= ${2})!".format(product_name, current_price, target_price)
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
            print('inside2')
            server.starttls()
            server.login(fr, password)
            text = message.as_string()
            server.sendmail(fr, t, text)
    def reset_table(self):
        self.products = []
        for row in self.tree.get_children():
            self.tree.delete(row)
    def print_tree_row_by_index(self, index):
        all_items = self.tree.get_children()
        print(all_items)
        if index < len(all_items):
            item_id = all_items[index]
            values = self.tree.item(item_id, 'values')
            print(f"Row {index} values:", values)
        else:
            print(f"Row {index} does not exist in the Treeview.")



root = tk.Tk()
app = AmazonPriceTracker(root)
root.mainloop()
