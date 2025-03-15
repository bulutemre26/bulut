from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from binance.client import Client
import pandas as pd
import numpy as np
import datetime

# Binance API Anahtarsız halka açık istemci
client = Client()

# Veriyi Binance'ten çek
def get_binance_data(symbol, interval, limit=500):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 
                                       'Close_time', 'Quote_asset_volume', 'Number_of_trades', 
                                       'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'Ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['Close'] = df['Close'].astype(float)
    return df[['timestamp', 'Close']]

# Fibonacci seviyelerini hesapla
def fibonacci_levels(start_price, end_price):
    difference = end_price - start_price
    return {
        "23.6": end_price - 0.236 * difference,
        "38.2": end_price - 0.382 * difference,
        "50": end_price - 0.5 * difference,
        "61.8": end_price - 0.618 * difference,
        "78.6": end_price - 0.786 * difference,
    }

# Harmonık formasyonları tespit et
def detect_gartley(stock_data):
    prices = stock_data['Close']
    timestamps = stock_data['timestamp']
    n = len(prices)
    results = []

    for i in range(3, n - 2):
        X, A, B, C, D = prices.iloc[i - 3], prices.iloc[i - 2], prices.iloc[i - 1], prices.iloc[i], prices.iloc[i + 1]
        fib_levels = fibonacci_levels(A, B)
        
        if fib_levels["61.8"] < C < fib_levels["78.6"]:
            results.append(f"Gartley Formasyonu Tespit Edildi!\nTarih: {timestamps.iloc[i]}\nX: {X}, A: {A}, B: {B}, C: {C}, D: {D}\n")
    
    return results

# Kivy Arayüzü
class HarmonicApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.scroll_view = ScrollView()
        self.result_label = Label(text="Formasyonlar burada gösterilecek...", size_hint_y=None, height=500)
        
        self.scroll_view.add_widget(self.result_label)
        layout.add_widget(self.scroll_view)

        check_button = Button(text="Formasyonları Tara", size_hint_y=None, height=50)
        check_button.bind(on_press=self.scan_market)
        layout.add_widget(check_button)

        return layout

    def scan_market(self, instance):
        self.result_label.text = "Veri çekiliyor..."
        stock_data = get_binance_data("EOSUSDT", Client.KLINE_INTERVAL_15MINUTE, limit=500)
        
        if stock_data.empty:
            self.result_label.text = "Veri alınamadı, tekrar deneyin."
            return
        
        formations = detect_gartley(stock_data)
        if formations:
            self.result_label.text = "\n\n".join(formations)
        else:
            self.result_label.text = "Son bir hafta içinde formasyon bulunamadı."

# Uygulamayı başlat
if __name__ == "__main__":
    HarmonicApp().run()
