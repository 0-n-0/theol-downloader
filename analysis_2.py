import matplotlib.pyplot as plt
import requests
import codecs
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import tkinter as tk
import os
import numpy as np

hex_to_letter = {
    '0': 'A',
    '1': 'B',
    '2': 'C',
    '3': 'D',
    '4': 'E',
    '5': 'F',
    '6': 'G',
    '7': 'H',
    '8': 'I',
    '9': 'J',
    'a': 'K',
    'b': 'L',
    'c': 'M',
    'd': 'N',
    'e': 'O',
    'f': 'P'
}

letter_to_hex = {
    'A': '0',
    'B': '1',
    'C': '2',
    'D': '3',
    'E': '4',
    'F': '5',
    'G': '6',
    'H': '7',
    'I': '8',
    'J': '9',
    'K': 'a',
    'L': 'b',
    'M': 'c',
    'N': 'd',
    'O': 'e',
    'P': 'f'
}

def encode_id(id):
    encoded_content = id.encode('gb2312')
    hex_encoded_content = codecs.encode(encoded_content, 'hex')
    letter_encoded_content = ''.join(hex_to_letter[c] for c in hex_encoded_content.decode())
    return letter_encoded_content

def decode(content):
    hex_encoded_content = ''.join(letter_to_hex[c] for c in content)
    encoded_content = codecs.decode(hex_encoded_content, 'hex')
    decoded_content = encoded_content.decode('gb2312')
    return decoded_content

def check_url(url):
    response = None
    try:
        response = requests.get(url, stream=True, timeout=10)
        if 'Content-Type' in response.headers:
            return True
    except Exception as e:
        pass
    finally:
        if response is not None:
            response.close()
    return False

def generate_urls(start_id, end_id, url_keyword, step):
    return [f"{url_keyword}/meol/common/ckeditor/openfile.jsp?id={encode_id(str(id).zfill(6))}" for id in
            range(start_id, end_id + 1, step)]

def start_checking(start_id, end_id, step, url_keyword, thread_count, bins):
    urls = generate_urls(start_id, end_id, url_keyword, step)
    valid_ids = []
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for url, is_valid in tqdm(zip(urls, executor.map(check_url, urls)), total=len(urls)):
            id = decode(url.split('=')[-1])
            if is_valid:
                valid_ids.append(int(id))

    valid_ids_np = np.array(valid_ids)
    bins_np = np.linspace(start_id, end_id, bins + 1)
    counts, _ = np.histogram(valid_ids_np, bins=bins_np)
    attempts_per_bin = (end_id - start_id) // bins // step
    valid_ratios = counts / attempts_per_bin

    plt.figure(figsize=(int(bins / 5), 6))
    plt.bar(range(1, bins + 1), valid_ratios)
    plt.title('Distribution of valid IDs')
    plt.xlabel('ID Range')
    plt.ylabel('Valid Ratio')
    plt.xticks(range(1, bins + 1), labels=[f'{bins_np[i]:.0f}-{bins_np[i + 1]:.0f}' for i in range(bins)], rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(os.getcwd(), f"ID_Distribution_{start_id}_{end_id}.png"))
    plt.close()
    print(f"The distribution graph is saved as 'ID_Distribution_{start_id}_{end_id}.png' in the current directory.")


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.start_id_label = tk.Label(self, text="Start ID")
        self.start_id_label.pack()
        self.start_id_entry = tk.Entry(self)
        self.start_id_entry.pack()

        self.end_id_label = tk.Label(self, text="End ID")
        self.end_id_label.pack()
        self.end_id_entry = tk.Entry(self)
        self.end_id_entry.pack()

        self.step_label = tk.Label(self, text="Step")
        self.step_label.pack()
        self.step_entry = tk.Entry(self)
        self.step_entry.pack()

        self.url_keyword_label = tk.Label(self, text="URL Keyword")
        self.url_keyword_label.pack()
        self.url_keyword_entry = tk.Entry(self)
        self.url_keyword_entry.pack()

        self.thread_count_label = tk.Label(self, text="Thread Count")
        self.thread_count_label.pack()
        self.thread_count_entry = tk.Entry(self)
        self.thread_count_entry.pack()

        self.bins_label = tk.Label(self, text="Bins")
        self.bins_label.pack()
        self.bins_entry = tk.Entry(self)
        self.bins_entry.pack()

        self.start_button = tk.Button(self)
        self.start_button["text"] = "Start"
        self.start_button["command"] = self.start_checking
        self.start_button.pack()

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack()

    def start_checking(self):
        try:
            start_id = int(self.start_id_entry.get())
            end_id = int(self.end_id_entry.get())
            step = int(self.step_entry.get())
            url_keyword = self.url_keyword_entry.get()
            thread_count = int(self.thread_count_entry.get())
            bins = int(self.bins_entry.get())
            if start_id > end_id or step <= 0 or thread_count <= 0 or bins <= 0:
                raise ValueError
            start_checking(start_id, end_id, step, url_keyword, thread_count, bins)
        except ValueError:
            print("Invalid input! Please ensure all inputs are positive integers and start_id is less than end_id.")


root = tk.Tk()
root.title('ID Explorer')
root.geometry('230x350')
app = Application(master=root)
app.mainloop()
