import os
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from supabase import create_client, Client

SUPABASE_URL = "https://bswaocmeujbbsnvwvpoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzd2FvY21ldWpiYnNudnd2cG9xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNzU3OTAsImV4cCI6MjEwNjk1MTc5MH0.50zNzY3xCDf0yfNaKbuYIxdjPKA2n7gH_5Zk-SR8Qq8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def scrape_site(page, url, kurum_adi):
    ilanlar = []
    try:
        print(f"Tarayıcı açılıyor: {kurum_adi} ({url})")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000) # Sayfanın JS render tamamlaması için bekleme
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True)
            href = a['href']
            
            if len(text) > 10 and any(k in text.lower() for k in ['alımı', 'personel', 'memur', 'sözleşmeli', 'akademik', 'duyuru', 'sınav', 'kpss', 'ilan']):
                if href.startswith('http'):
                    full_link = href
                elif href.startswith('/'):
                    base = '/'.join(url.split('/')[:3])
                    full_link = f"{base}{href}"
                else:
                    full_link = f"{url.rstrip('/')}/{href}"

                ilanlar.append({
                    "baslik": text[:180],
                    "link": full_link,
                    "kurum": kurum_adi,
                    "tarih": "Güncel"
                })
    except Exception as e:
        print(f"{kurum_adi} taranırken hata: {e}")
    return ilanlar

async def main():
    toplanan = []
    async with async_playwright() as p:
        # Gerçek Chrome tarayıcı başlatılıyor
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 1. Kamu İlan SBB
        toplanan.extend(await scrape_site(page, "https://kamuilan.sbb.gov.tr/", "SBB Kamu İlan"))
        
        # 2. Kariyer Kapısı
        toplanan.extend(await scrape_site(page, "https://kariyerkapisi.cbiko.gov.tr/isealim", "Kariyer Kapısı"))
        
        # 3. GSB Personel
        toplanan.extend(await scrape_site(page, "https://pgm.gsb.gov.tr/", "GSB Personel"))

        await browser.close()

    print(f"\nToplam {len(toplanan)} adet benzersiz ilan toplandı.")

    basarili = 0
    for item in toplanan:
        try:
            supabase.table('ilanlar').upsert(item, on_conflict='link').execute()
            basarili += 1
        except Exception as e:
            pass

    print(f"Supabase'e başarıyla aktarılan ilan sayısı: {basarili}")

if __name__ == "__main__":
    asyncio.run(main())
