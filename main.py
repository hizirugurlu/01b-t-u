import flet as ft
import asyncio
import json
import websockets
import os

# TEKNİK ANALİZ: 
# 1. Port Çakışması: Render dinamik port atadığı için os.getenv("PORT") eklendi.
# 2. Host Erişimi: Dış dünyaya açılması için host="0.0.0.0" olarak set edildi.
# 3. Performans: WebSocket 100ms asenkron döngüde bloklanmadan çalışır.

async def main(page: ft.Page):
    # iPhone 13 Tasarım Ayarları
    page.title = "01-B-T-U v1.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = ft.padding.only(top=50, left=15, right=15, bottom=30)
    page.bgcolor = "#000000"  # OLED Ekran için tam siyah

    # UI Bileşenleri
    fiyat_gostergesi = ft.Text("$0.00", size=45, weight="bold", color="green")
    degisim_yuzdesi = ft.Text("BTC/USDT CANLI", size=18, color="white70")
    derinlik_paneli = ft.Column(spacing=2, scroll=ft.ScrollMode.HIDDEN)

    # Arayüz Yapısı
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("MÜHENDİS ANALİZ TERMİNALİ", size=12, color="blueaccent", weight="w500"),
                fiyat_gostergesi,
                degisim_yuzdesi,
            ]),
            margin=ft.margin.only(bottom=20)
        ),
        ft.Divider(height=1, color="white10"),
        ft.Text("10 KADEMELİ DERİNLİK (L2 DATA)", size=14, weight="bold", color="white"),
        ft.Container(content=derinlik_paneli, expand=True)
    )

    async def veri_akisi():
        uri = "wss://stream.binance.com:9443/ws/btcusdt@depth10@100ms"
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    while True:
                        raw_data = await websocket.recv()
                        data = json.loads(raw_data)
                        
                        # Anlık Fiyat
                        mevcut_fiyat = float(data['asks'][0][0])
                        fiyat_gostergesi.value = f"${mevcut_fiyat:,.2f}"
                        
                        # Derinlik Listesi Güncelleme
                        derinlik_paneli.controls.clear()
                        
                        # Satışlar (Asks)
                        for ask in data['asks'][:5][::-1]:
                            derinlik_paneli.controls.append(
                                ft.Row([
                                    ft.Text(f"{ask[0]}", color="red400", size=13),
                                    ft.Text(f"{float(ask[1]):.4f}", color="white30", size=12)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            )

                        # Alışlar (Bids)
                        for bid in data['bids'][:5]:
                            derinlik_paneli.controls.append(
                                ft.Row([
                                    ft.Text(f"{bid[0]}", color="green400", size=13),
                                    ft.Text(f"{float(bid[1]):.4f}", color="white30", size=12)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            )
                        
                        page.update()
            except Exception as e:
                print(f"Bağlantı Hatası: {e}. 5 saniye içinde yeniden denenecek...")
                await asyncio.sleep(5)

    # Veri çekme görevini başlat
    asyncio.create_task(veri_akisi())

if __name__ == "__main__":
    # Render için kritik port ve host konfigürasyonu
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
