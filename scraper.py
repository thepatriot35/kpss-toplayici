import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

SUPABASE_URL = "https://bswaocmeujbbsnvwvpoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzd2FvY21ldWpiYnNudnd2cG9xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNzU3OTAsImV4cCI6MjEwNjk1MTc5MH0.50zNzY3xCDf0yfNaKbuYIxdjPKA2n7gH_5Zk-SR8Qq8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def resmi_gazete_kamu_ilanlari():
    """Resmi Gazete'de yayınlanan güncel kamu ve akademik alım ilanları"""
    ilanlar = []
    url = "https://www.resmigazete.gov.tr/ilanlar"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                if len(text) > 12 and any(k in text.lower() for k in ['alımı', 'personel', 'memur', 'sözleşmeli', 'akademik', 'rektörlük', 'bakanlığı']):
                    full_link = href if href.startswith('http') else f"https://www.resmigazete.gov.tr/{href.lstrip('/')}"
                    ilanlar.append({
                        "baslik": text[:180],
                        "link": full_link,
                        "kurum": "Resmi Gazete Kamu İlanları",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"Resmi Gazete tarama hatası: {e}")
    return ilanlar

def gsb_duyurulari():
    """Gençlik ve Spor Bakanlığı Personel Alım Duyuruları"""
    ilanlar = []
    url = "https://pgm.gsb.gov.tr/"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                if len(text) > 10 and any(k in text.lower() for k in ['alımı', 'personel', 'sınav', 'duyuru', 'kpss', 'kura']):
                    full_link = href if href.startswith('http') else f"https://pgm.gsb.gov.tr/{href.lstrip('/')}"
                    ilanlar.append({
                        "baslik": text[:180],
                        "link": full_link,
                        "kurum": "GSB Personel Genel Md.",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"GSB tarama hatası: {e}")
    return ilanlar

def main():
    print("Kamu kaynakları taranıyor...")
    toplanan = []
    
    rg_ilanlar = resmi_gazete_kamu_ilanlari()
    print(f"Resmi Gazete'den süzülen: {len(rg_ilanlar)}")
    toplanan.extend(rg_ilanlar)
    
    gsb_ilanlar = gsb_duyurulari()
    print(f"GSB'den süzülen: {len(gsb_ilanlar)}")
    toplanan.extend(gsb_ilanlar)

    print(f"Toplam {len(toplanan)} adet güncel kamu ilanı veritabanına aktarılıyor...")

    basarili = 0
    for item in toplanan:
        try:
            supabase.table('ilanlar').upsert(item, on_conflict='link').execute()
            basarili += 1
        except Exception as e:
            print(f"Yazma hatası: {e}")

    print(f"İşlem tamamlandı: {basarili} ilan Supabase'e kaydedildi.")

if __name__ == "__main__":
    main()
