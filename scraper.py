import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Supabase Bağlantısı
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def ilani_kaydet(baslik, link, kurum, tarih):
    """Veritabanına mükerrer kontrolü ile ilan ekler"""
    try:
        var_mi = supabase.table("duyurular").select("id").eq("link", link).execute()
        if len(var_mi.data) == 0:
            supabase.table("duyurular").insert({
                "baslik": baslik,
                "link": link,
                "kurum": kurum,
                "tarih": tarih
            }).execute()
            print(f"[YENİ EKLENDİ] {kurum}: {baslik}")
        else:
            print(f"[MEVCUT] {baslik}")
    except Exception as e:
        print(f"Hata oluştu: {e}")

# -------------------------------------------------------------
# 1. GSB PGM Duyurular Scraper
# -------------------------------------------------------------
def gsb_cek():
    url = "https://pgm.gsb.gov.tr/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        duyurular = soup.find_all("a", href=True)
        for d in duyurular:
            link = d["href"]
            if not link.startswith("http"):
                link = "https://pgm.gsb.gov.tr" + link
            baslik = d.text.strip()
            
            if len(baslik) > 10 and ("Duyuru" in baslik or "Alım" in baslik or "Sınav" in baslik or "KPSS" in baslik):
                ilani_kaydet(baslik, link, "GSB (Gençlik ve Spor Bakanlığı)", "Güncel")
    except Exception as e:
        print(f"GSB çekilirken hata: {e}")

# -------------------------------------------------------------
# 2. İlan.gov.tr Kamu-Akademik Personel Scraper (Kategori 8)
# -------------------------------------------------------------
def ilan_gov_cek():
    url = "https://www.ilan.gov.tr/kategori/8/kamu-akademik-personel"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        ilanlar = soup.find_all("a", href=True)
        for d in ilanlar:
            link = d["href"]
            if "/detail/" in link or "/ilan/" in link:
                if not link.startswith("http"):
                    link = "https://www.ilan.gov.tr" + link
                baslik = d.text.strip()
                if len(baslik) > 15:
                    ilani_kaydet(baslik, link, "İlan.gov.tr (Kamu-Akademik)", "Güncel")
    except Exception as e:
        print(f"İlan.gov.tr çekilirken hata: {e}")

if __name__ == "__main__":
    print("Scraper çalışmaya başladı...")
    gsb_cek()
    ilan_gov_cek()
    print("Scraping işlemi tamamlandı.")
