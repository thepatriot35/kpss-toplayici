import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

SUPABASE_URL = "https://bswaocmeujbbsnvwvpoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzd2FvY21ldWpiYnNudnd2cG9xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNzU3OTAsImV4cCI6MjEwNjk1MTc5MH0.50zNzY3xCDf0yfNaKbuYIxdjPKA2n7gH_5Zk-SR8Qq8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def ilanlari_cikar():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Test ve başlangıç verisi (Sitenin boş kalmaması ve bağlantıyı doğrulamak için)
    ilanlar = [
        {
            "baslik": "Sistem Bağlantı Test İlanı - KPSS Personel Alımı",
            "link": "https://www.resmigazete.gov.tr",
            "kurum": "Kamu Personeli Portalı",
            "tarih": "Bugün"
        }
    ]
    
    # Örnek kaynak: Resmi Gazete / İlan Portalı tarama
    url = "https://www.resmigazete.gov.tr/ilanlar"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Web sitesi yanıt kodu: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for a in links:
                text = a.get_text(strip=True)
                href = a['href']
                
                # İlan içeren kelimeleri filtreleme
                if any(kelime in text.lower() for kelime in ['memur', 'alımı', 'personel', 'kpss', 'akademik']):
                    full_link = href if href.startswith('http') else f"https://www.resmigazete.gov.tr/{href.lstrip('/')}"
                    ilanlar.append({
                        "baslik": text[:150],
                        "link": full_link,
                        "kurum": "Resmi Gazete",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"Scrape sırasında hata oluştu: {e}")

    print(f"Toplam {len(ilanlar)} adet ilan işleniyor...")

    # Supabase veritabanına aktarma
    eklenen_sayisi = 0
    for ilan in ilanlar:
        try:
            res = supabase.table('ilanlar').upsert(ilan, on_conflict='link').execute()
            eklenen_sayisi += 1
        except Exception as err:
            print(f"Veri ekleme hatası ({ilan['baslik'][:20]}...): {err}")
            
    print(f"Başarıyla Supabase'e kaydedilen: {eklenen_sayisi}")

if __name__ == "__main__":
    ilanlari_cikar()
