import os
import requests
from supabase import create_client, Client

SUPABASE_URL = "https://bswaocmeujbbsnvwvpoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzd2FvY21ldWpiYnNudnd2cG9xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNzU3OTAsImV4cCI6MjEwNjk1MTc5MH0.50zNzY3xCDf0yfNaKbuYIxdjPKA2n7gH_5Zk-SR8Qq8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

def kariyer_kapisi_cek():
    """Kariyer Kapısı İşe Alım API'sinden aktif ilanları çeker"""
    ilanlar = []
    url = "https://isealimkariyerkapisi.cbiko.gov.tr/api/announcement/getlist"
    payload = {"pageIndex": 1, "pageSize": 20, "sortField": "createdDate", "sortOrder": "DESC"}
    try:
        res = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            items = data.get('data', {}).get('items', []) or data.get('items', [])
            for item in items:
                title = item.get('title') or item.get('header') or item.get('announcementTitle')
                id_val = item.get('id') or item.get('announcementId')
                if title:
                    link = f"https://kariyerkapisi.cbiko.gov.tr/isealim/ilan/{id_val}" if id_val else "https://kariyerkapisi.cbiko.gov.tr/isealim"
                    ilanlar.append({
                        "baslik": str(title)[:180],
                        "link": link,
                        "kurum": "Kariyer Kapısı",
                        "tarih": "Güncel"
                    })
    except Exception as e:
        print(f"Kariyer Kapısı API Hatası: {e}")
    return ilanlar

def sbb_kamu_ilan_cek():
    """SBB Kamu İlan Portalının API servisinden aktif ilanları çeker"""
    ilanlar = []
    url = "https://kamuilan.sbb.gov.tr/api/Ilan/List?pageSize=20&pageNumber=1"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            items = data.get('data', []) or data.get('items', []) if isinstance(data, dict) else data
            if isinstance(items, list):
                for item in items:
                    title = item.get('baslik') or item.get('title') or item.get('kurumAdi')
                    id_val = item.get('id')
                    if title:
                        link = f"https://kamuilan.sbb.gov.tr/ilan/{id_val}" if id_val else "https://kamuilan.sbb.gov.tr/"
                        ilanlar.append({
                            "baslik": str(title)[:180],
                            "link": link,
                            "kurum": "SBB Kamu İlan",
                            "tarih": "Güncel"
                        })
    except Exception as e:
        print(f"SBB Kamu İlan Hatası: {e}")
    return ilanlar

def gsb_duyuru_cek():
    """GSB Personel Genel Müdürlüğü Duyuruları"""
    ilanlar = []
    url = "https://pgm.gsb.gov.tr/"
    try:
        from bs4 import BeautifulSoup
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                if len(text) > 12 and any(k in text.lower() for k in ['alımı', 'personel', 'sınav', 'duyuru', 'kpss', 'kura']):
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

def main():
    toplanan = []
    
    print("1. Kariyer Kapısı çekiliyor...")
    toplanan.extend(kariyer_kapisi_cek())
    
    print("2. SBB Kamu İlan çekiliyor...")
    toplanan.extend(sbb_kamu_ilan_cek())
    
    print("3. GSB Personel çekiliyor...")
    toplanan.extend(gsb_duyuru_cek())

    print(f"Toplam {len(toplanan)} adet ilan toplandı.")

    basarili = 0
    for item in toplanan:
        try:
            supabase.table('ilanlar').upsert(item, on_conflict='link').execute()
            basarili += 1
        except Exception as e:
            print(f"Yazma hatası: {e}")

    print(f"Supabase'e başarıyla aktarılan: {basarili}")

if __name__ == "__main__":
    main()
