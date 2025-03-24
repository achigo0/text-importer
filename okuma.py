import pytesseract
from PIL import Image, ImageEnhance
import mss
import tkinter as tk
from tkinter import scrolledtext
import keyboard
import threading

# Tesseract'ın kurulu olduğu yolu belirtin
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class SelectionWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ekran Alanı Seç")
        
        # Pencereyi tam ekran yap
        self.attributes('-fullscreen', True)
        
        # Şeffaflık ayarı
        self.attributes('-alpha', 0.3)  # 0 (tamamen şeffaf) ile 1 (tamamen opak) arasında bir değer
        
        # Tam ekran ve en üstte olmasını sağlar
        self.wm_attributes('-topmost', True)
        self.canvas = tk.Canvas(self, bg='grey', cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selected_area = None

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        end_x, end_y = event.x, event.y
        self.selected_area = {
            'left': min(self.start_x, end_x),
            'top': min(self.start_y, end_y),
            'width': abs(end_x - self.start_x),
            'height': abs(end_y - self.start_y)
        }
        self.destroy()

def capture_and_ocr(area):
    if area is None:
        print("Alan seçilmedi.")
        return

    # Ekran görüntüsü almak için mss kullanımı
    with mss.mss() as sct:
        # Seçilen alanın görüntüsünü al
        screenshot = sct.grab(area)

        # Görüntüyü Pillow Image objesine çevir
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

        # Görüntüyü gri tonlamaya çevir
        img = img.convert('L')

        # Kontrastı artır
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)

        # OCR ile görüntüden yazıları oku
        text = pytesseract.image_to_string(img, lang='tur')

        # Sonucu pencerede göster
        show_result(text)

def show_result(text):
    # Tkinter penceresi oluşturma
    window = tk.Tk()
    window.title("OCR Sonucu")

    # Sonuç metni için scrolledtext widget'ı ekleme
    text_widget = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20)
    text_widget.pack(padx=10, pady=10)
    text_widget.insert(tk.END, text)

    # Pencerenin kapatılması için basit bir buton ekleme
    close_button = tk.Button(window, text="Kapat", command=window.destroy)
    close_button.pack(pady=5)

    # Pencereyi sürekli olarak güncel tutma
    window.mainloop()

def on_hotkey():
    # Seçim penceresini aç ve ardından seçilen alanı kullanarak ekran görüntüsünü alıp OCR yap
    selection_window = SelectionWindow()
    selection_window.mainloop()
    area = selection_window.selected_area

    if area:
        capture_and_ocr(area)

# Kısayol tuşunu ayarla (örneğin, ALT+F12 tuşu)
keyboard.add_hotkey('alt + f12', on_hotkey)

print("Alan seçmek ve OCR yapmak için ALT+F12 tuşuna basın.")

# Programın çalışmasını sağla
keyboard.wait('esc')  # Programı 'esc' tuşuna basana kadar beklet
