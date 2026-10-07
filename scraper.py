import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

SUPABASE_URL = "https://bswaocmeujbbsnvwvpoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzd2FvY21ldWpiYnNudnd2cG9xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNzU3OTAsImV4cCI6MjEwNjk1MTc5MH0.50zNzY3xCDf0yfNaKbuYIxdjPKA2n7gH_5Zk-SR8Qq8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Taranacak Hedef Adresler
KAYNAKLAR = [
    {"ad": "SBB Kamu İlan", "url": "https://kamuilan.sbb.gov.tr/"},
    {"ad": "Kariyer Kapısı", "url": "https://kariyerkapisi.gov.tr/isealim"},
    {"ad": "GSB Personel", "url": "https://pgm.gsb.gov.tr/"},
    {"ad": "İlan.gov.tr Akademik/Kamu", "url": "https://www.ilan.gov.tr/ilan/kategori/8/kamu-akademik-personel"}
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
}

def siteleri_tara():
    toplanan_ilanlar = []
    
    for kaynak in KAYNAKLAR:
        print(f"Taraniyor: {kaynak['ad']} ({kaynak['url']})")
        try:
            res = requests.get(kaynak['url'], headers=HEADERS, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, 'html.parser')
                links = soup.find_all('a', href=True)
                
                bulunan_sayi = 0
                for a in links:
                    text = a.get_text(strip=True)
                    href = a['href']
                    
                    # Filtreleme kriterleri
                    if len(text) > 12 and any(k in text.lower() for k in ['alımı', 'personel', 'memur', 'sözleşmeli', 'akademik', 'kpss', 'duyuru', 'ilan']):
                        # Tam URL oluşturma
                        if href.startswith('http'):
                            full_url = href
                        elif href.startswith('/'):
                            base_domain = '/'.join(kaynak['url'].split('/')[:3])
                            full_url = f"{base_domain}{href}"
                        else:
                            full_url = f"{kaynak['url'].rstrip('/')}/{href}"

                        toplanan_ilanlar.append({
                            "baslik": text[:180],
                            "link": full_url,
                            "kurum": kaynak['ad'],
                            "tarih": "Güncel"
                        })
                        bulunan_sayi += 1
                
                print(f"-> {kaynak['ad']} kaynağından {bulunan_sayi} adet başlık süzüldü.")
            else:
                print(f"-> {kaynak['ad']} yanıt vermedi (Status: {res.status_code})")
        except Exception as e:
            print(f"-> {kaynak['ad']} taranırken hata: {e}")

    print(f"\nToplam {len(toplanan_ilanlar)} adet potansiyel ilan toplandı. Supabase'e aktarılıyor...")

    # Supabase'e Ekleme
    basarili = 0
    for ilan in toplanan_ilanlar:
        try:
            supabase.table('ilanlar').upsert(ilan, on_conflict='link').execute()
            basarili += 1
        except Exception as err:
            pass # Mükerrer veya hatalı verileri sessizce atla

    print(f"İşlem Tamamlandı! Toplam {basarili} ilan Supabase'e eklendi/güncellendi.")

if __name__ == "__main__":
    siteleri_tara()
