import flet as ft
import asyncio
import json
import websockets

async def borsa_takip(page: ft.Page):
    page.title = "Mühendislik Portalı - Borsa v1.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.START
    
    # iPhone 13 çentik ve alt bar güvenli alan ayarı
    page.padding = ft.padding.only(top=50, left=10, right=10, bottom=20)

    fiyat_text = ft.Text("Yükleniyor...", size=40, weight="bold", color="yellow")
    derinlik_listesi = ft.ListView(expand=1, spacing=5)

    page.add(
        ft.Text("BTC/USDT CANLI VERİ", size=14, color="grey"),
        fiyat_text,
        ft.Divider(),
        ft.Text("10 KADEMELİ DERİNLİK (ASK/BID)", weight="bold"),
        derinlik_listesi
    )

    # WebSocket üzerinden anlık veri çekme fonksiyonu
    async def veri_akisi():
        url = "wss://stream.binance.com:9443/ws/btcusdt@depth10@100ms"
        async with websockets.connect(url) as ws:
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                
                # Fiyatı ilk Ask (Satış) kademesinden alıyoruz
                fiyat_text.value = f"${float(data['asks'][0][0]):,.2f}"
                
                # Derinlik Listesini Güncelle
                derinlik_listesi.controls.clear()
                for i in range(5): # İlk 5 kademe
                    derinlik_listesi.controls.append(
                        ft.Row([
                            ft.Text(f"S: {data['asks'][i][0]}", color="red"),
                            ft.Text(f"A: {data['bids'][i][0]}", color="green"),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )
                page.update()

    # Arka planda sürekli çalışması için task başlat
    asyncio.create_task(veri_akisi())

ft.app(target=borsa_takip, view=ft.AppView.WEB_BROWSER)