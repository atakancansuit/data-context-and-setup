import os
import pandas as pd
from pathlib import Path

class Olist:
    def __init__(self):
        # Makine başladığında verinin yolunu belirle.
        # ~/.workintech/olist/data/csv yolunu Path nesnesi yapıyoruz.
        self.csv_path = Path("~/.workintech/olist/data/csv").expanduser()

    def get_data(self):
        """
        Bu fonksiyon CSV dosyalarını okur ve temizlenmiş anahtarlarla
        bir sözlük (dictionary) olarak döndürür.
        """
        
        # 1. ADIM: Klasördeki tüm .csv dosyalarının yollarını bul
        # iterdir() klasörü tarar, endswith('.csv') sadece csv olanları alır.
        file_paths = [
            f for f in self.csv_path.iterdir() 
            if f.name.endswith('.csv')
        ]
        
        # 2. ADIM: Dosya isimlerini temizleyerek 'Key' (Anahtar) oluştur
        # Örnek: 'olist_sellers_dataset.csv' -> 'sellers'
        key_names = [
            f.name.replace("olist_", "").replace("_dataset", "").replace(".csv", "")
            for f in file_paths
        ]
        
        # 3. ADIM: Veri Sözlüğünü Oluştur
        data = {}
        
        # zip() fermuarı ile isimleri ve yolları eşleştirip döngüye sokuyoruz
        for key, path in zip(key_names, file_paths):
            # pandas ile oku ve sözlüğe koy
            # Not: pd.read_csv bazen Path nesnesi yerine string ister, 
            # o yüzden str(path) ile garantiye alabiliriz (zorunlu değil ama güvenli).
            data[key] = pd.read_csv(path)
            
        # 4. ADIM: Hazırlanan paketi geri gönder
        return data

    def ping(self):
        """
        Sistemin çalıştığını test etmek için basit bir fonksiyon.
        """
        print("pong")