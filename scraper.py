import os
import requests
from supabase import create_client, Client

SUPABASE_URL = "https://bswaocmeujbbsnvwvpoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzd2FvY21ldWpiYnNudnd2cG9xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNzU3OTAsImV4cCI6MjEwNjk1MTc5MH0.50zNzY3xCDf0yfNaKbuYIxdjPKA2n7gH_5Zk-SR8Qq8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def ilan_gov_tr_api():
    ilanlar = []
    # ilan.gov.tr Mobil API uç noktası (Akademik & Kamu Personel Alımları)
    url = "https://www.ilan.gov.tr/api/v1/search/category/8?pageSize=30&page=0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://www.ilan.gov.tr',
        'Referer': 'https://www.ilan.gov.tr/'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"API Yanıt Kodu: {res.status_code}")
        
        if res.status_code == 200:
            json_data = res.json()
            # API'den gelen öğeleri süz
            items = json_data.get('data', {}).get('items', [])
            
            for item in items:
                title = item.get('title') or item.get('header') or item.get('titleText')
                ilan_id = item.get('id')
                
                if title and ilan_id:
                    ilanlar.append({
                        "baslik": str(title)[:180],
                        "link": f"https://www.ilan.gov.tr/ilan/{ilan_id}",
                        "kurum": "İlan.gov.tr (Kamu & Akademik)",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"API İstek Hatası: {e}")
        
    return ilanlar

def main():
    print("İlanlar çekiliyor...")
    toplanan = ilan_gov_tr_api()
    print(f"Çekilen ilan sayısı: {len(toplanan)}")

    if not tolanan:
        # Yedek veri (API'de geçici aksama olursa veritabanı boş kalmasın)
        toplanan.append({
            "baslik": "Aramalar Aktif - Yeni İlanlar Bekleniyor",
            "link": "https://www.ilan.gov.tr",
            "kurum": "Kamu İlan Takip",
            "tarih": "Bugün"
        })

    basarili = 0
    for item in tolanan:
        try:
            supabase.table('ilanlar').upsert(item, on_conflict='link').execute()
            basarili += 1
        except Exception as e:
            print(f"Yazma hatası: {e}")

    print(f"Supabase'e başarıyla aktarılan: {basarili}")

if __name__ == "__main__":
    main()
