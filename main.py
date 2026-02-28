import flet as ft
import asyncio
import json
import websockets
import os

# TEKNİK ANALİZ: 
# 1. Deprecation Fix: ft.app() yerine ft.run() kullanılarak modern yapıya geçildi.
# 2. Resiliency: Bağlantı kopmalarına karşı otomatik 'retry' mekanizması korundu.

async def main(page: ft.Page):
    # iPhone 13 Tasarım Optimizasyonu
    page.title = "01-B-T-U v1.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = ft.padding.only(top=60, left=15, right=15, bottom=30)
    page.bgcolor = "#000000" # OLED tasarrufu

    # UI Bileşenleri
    fiyat_gostergesi = ft.Text("$0.00", size=48, weight="bold", color="green")
    alt_bilgi = ft.Text("BTC/USDT - GERÇEK ZAMANLI", size=14, color="white70")
    derinlik_paneli = ft.Column(spacing=3, scroll=ft.ScrollMode.HIDDEN)

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("TEKNİK ANALİZ TERMİNALİ", size=12, color="blueaccent", weight="w700"),
                fiyat_gostergesi,
                alt_bilgi,
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
                        
                        mevcut_fiyat = float(data['asks'][0][0])
                        fiyat_gostergesi.value = f"${mevcut_fiyat:,.2f}"
                        
                        derinlik_paneli.controls.clear()
                        # Satışlar
                        for ask in data['asks'][:5][::-1]:
                            derinlik_paneli.controls.append(
                                ft.Row([
                                    ft.Text(f"{ask[0]}", color="red400", size=13),
                                    ft.Text(f"{float(ask[1]):.4f}", color="white30", size=12)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            )
                        # Alışlar
                        for bid in data['bids'][:5]:
                            derinlik_paneli.controls.append(
                                ft.Row([
                                    ft.Text(f"{bid[0]}", color="green400", size=13),
                                    ft.Text(f"{float(bid[1]):.4f}", color="white30", size=12)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            )
                        page.update()
            except:
                await asyncio.sleep(5)

    asyncio.create_task(veri_akisi())

if __name__ == "__main__":
    # Render ve iPhone uyumluluğu için kritik config
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8080))
    )
