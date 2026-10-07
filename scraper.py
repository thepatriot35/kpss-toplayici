import os
import json
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

SUPABASE_URL = "https://bswaocmeujbbsnvwvpoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzd2FvY21ldWpiYnNudnd2cG9xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNzU3OTAsImV4cCI6MjEwNjk1MTc5MH0.50zNzY3xCDf0yfNaKbuYIxdjPKA2n7gH_5Zk-SR8Qq8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def ilan_gov_tr_cek():
    """ilan.gov.tr API uç noktası üzerinden doğrudan JSON çeker"""
    ilanlar = []
    try:
        # ilan.gov.tr servis uç noktası
        api_url = "https://www.ilan.gov.tr/api/v1/search/category/8?pageSize=20&page=0"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*'
        }
        res = requests.get(api_url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            items = data.get('data', {}).get('items', [])
            for item in items:
                title = item.get('title') or item.get('header')
                ilan_id = item.get('id')
                if title and ilan_id:
                    ilanlar.append({
                        "baslik": str(title)[:180],
                        "link": f"https://www.ilan.gov.tr/ilan/{ilan_id}",
                        "kurum": "İlan.gov.tr",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"ilan.gov.tr API Hatası: {e}")
    return ilanlar

def gsb_cek():
    """GSB Duyurular sayfasını tarar"""
    ilanlar = []
    try:
        url = "https://pgm.gsb.gov.tr/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                if len(text) > 15 and any(k in text.lower() for k in ['alımı', 'personel', 'duyuru', 'sınav', 'kpss', 'sözleşmeli']):
                    full_link = href if href.startswith('http') else f"https://pgm.gsb.gov.tr/{href.lstrip('/')}"
                    ilanlar.append({
                        "baslik": text[:180],
                        "link": full_link,
                        "kurum": "GSB Personel",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"GSB Hatası: {e}")
    return ilanlar

def ana_calistir():
    toplanan = []
    
    print("1. ilan.gov.tr taranıyor...")
    ig_ilanlar = ilan_gov_tr_cek()
    toplanan.extend(ig_ilanlar)
    print(f"   -> {len(ig_ilanlar)} ilan çekildi.")
    
    print("2. GSB taranıyor...")
    gsb_ilanlar = gsb_cek()
    toplanan.extend(gsb_ilanlar)
    print(f"   -> {len(gsb_ilanlar)} ilan çekildi.")

    print(f"\nToplam {len(toplanan)} ilan Supabase'e gönderiliyor...")

    basarili = 0
    for item in toplanan:
        try:
            supabase.table('ilanlar').upsert(item, on_conflict='link').execute()
            basarili += 1
        except Exception as e:
            print(f"Ekleme hatası: {e}")

    print(f"Sonuç: {basarili} adet ilan başarıyla eklendi!")

if __name__ == "__main__":
    ana_calistir()
