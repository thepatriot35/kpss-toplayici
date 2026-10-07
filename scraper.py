import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

SUPABASE_URL = "https://bswaocmeujbbsnvwvpoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzd2FvY21ldWpiYnNudnd2cG9xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNzU3OTAsImV4cCI6MjEwNjk1MTc5MH0.50zNzY3xCDf0yfNaKbuYIxdjPKA2n7gH_5Zk-SR8Qq8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
}

def ilanlari_topla():
    toplanan = []

    # 1. Kaynak: İlan.gov.tr (Akademik & Kamu)
    try:
        url1 = "https://www.ilan.gov.tr/ilan/kategori/8/kamu-akademik-personel"
        res = requests.get(url1, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            # İlan linklerini yakala
            links = soup.find_all('a', href=True)
            for a in links:
                href = a['href']
                text = a.get_text(strip=True)
                if '/ilan/' in href and len(text) > 10:
                    full_link = href if href.startswith('http') else f"https://www.ilan.gov.tr{href}"
                    toplanan.append({
                        "baslik": text[:180],
                        "link": full_link,
                        "kurum": "İlan.gov.tr",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"İlan.gov.tr hata: {e}")

    # 2. Kaynak: GSB Personel Genel Müdürlüğü
    try:
        url2 = "https://pgm.gsb.gov.tr/"
        res = requests.get(url2, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                if any(k in text.lower() for k in ['alımı', 'personel', 'sözleşmeli', 'duyuru', 'sınav', 'kpss']):
                    full_link = href if href.startswith('http') else f"https://pgm.gsb.gov.tr/{href.lstrip('/')}"
                    toplanan.append({
                        "baslik": text[:180],
                        "link": full_link,
                        "kurum": "GSB Personel",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"GSB hata: {e}")

    # 3. Kaynak: Kamu İlan SBB & Kariyer Kapısı Genel Duyurular
    try:
        url3 = "https://kamuilan.sbb.gov.tr/"
        res = requests.get(url3, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                if len(text) > 12:
                    full_link = href if href.startswith('http') else f"https://kamuilan.sbb.gov.tr/{href.lstrip('/')}"
                    toplanan.append({
                        "baslik": text[:180],
                        "link": full_link,
                        "kurum": "SBB Kamu İlan",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"SBB Kamu İlan hata: {e}")

    print(f"Süzülen toplam ilan sayısı: {len(toplanan)}")

    # Supabase'e Yazma
    basarili = 0
    for item in toplanan:
        try:
            supabase.table('ilanlar').upsert(item, on_conflict='link').execute()
            basarili += 1
        except Exception:
            pass

    print(f"Supabase'e başarıyla yazılan: {basarili}")

if __name__ == "__main__":
    ilanlari_topla()
