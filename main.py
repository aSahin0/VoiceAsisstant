
import os
import time
import random
import re
from datetime import datetime

# Konuşma ve ses tanıma
import speech_recognition as sr
from gtts import gTTS
from playsound3 import playsound

# Web otomasyonu ve veri çekme
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Çeviri
from googletrans import Translator

# Sistem ve kamera işlemleri
import psutil
import cv2

class VoiceAssistant:
    """
    Sesli komutlarla çeşitli görevleri yerine getiren bir asistan sınıfı.
    """
    def __init__(self):
        """Asistanı başlatır ve gerekli araçları hazırlar."""
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        
       
        self.OPENWEATHERMAP_API_KEY = "BURAYA_API_ANAHTARINIZI_GIRIN"
        self.WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
        
       
        self.commands = {
            ("merhaba", "selam"): self.greet,
            ("görüşürüz", "sistemi kapat"): self.shutdown,
            ("hangi gündeyiz",): self.tell_day,
            ("saat kaç", "zamanı söyle"): self.tell_time,
            ("youtube aç", "video aç", "şarkı aç"): self.open_youtube,
            ("google aç", "google'da ara"): self.search_google,
            ("çevir",): self.translate_text,
            ("not tut", "not al"): self.take_note,
            ("hava durumu",): self.get_weather,
            ("sistem bilgisi", "bilgisayarın durumu"): self.get_system_info,
            ("fotoğraf çek",): self.take_photo,
            ("video çek",): self.record_video,
        }

    def _speak(self, text):
        """Verilen metni sesli olarak okur."""
        print(f"Asistan: {text}")
        try:
            tts = gTTS(text=text, lang="tr")
            # Dosyaya kaydet, çal ve sil.
            temp_file = "response.mp3"
            tts.save(temp_file)
            playsound(temp_file)
            os.remove(temp_file)
        except Exception as e:
            print(f"Seslendirme hatası: {e}")

    def _listen(self, prompt=None):
        """Mikrofondan ses dinler ve metne çevirir."""
        with sr.Microphone() as source:
            if prompt:
                self._speak(prompt)
            print("Dinliyorum...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)
            
            try:
                command = self.recognizer.recognize_google(audio, language="tr-TR").lower()
                print(f"Kullanıcı: {command}")
                return command
            except sr.UnknownValueError:
                self._speak("Ne dediğinizi anlayamadım, lütfen tekrar eder misiniz?")
                return None
            except sr.RequestError:
                self._speak("Sistemde bir hata oluştu, lütfen internet bağlantınızı kontrol edin.")
                return None

    def _get_unique_filename(self, prefix, extension):
        """Zaman damgası ile benzersiz dosya adı oluşturur."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"

    def greet(self):
        """Kullanıcıyı selamlar."""
        responses = ["Merhaba!", "Selam, nasıl yardımcı olabilirim?", "Merhaba, hoş geldin!"]
        self._speak(random.choice(responses))

    def shutdown(self):
        """Asistanı kapatır."""
        self._speak("Görüşmek üzere, hoşça kal!")
        exit()

    def tell_day(self):
        """Haftanın gününü Türkçe olarak söyler."""
        days_tr = {
            "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
            "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"
        }
        day_en = datetime.now().strftime("%A")
        self._speak(f"Bugün günlerden {days_tr.get(day_en, 'Bilinmeyen Gün')}")

    def tell_time(self):
        """Şu anki saati söyler."""
        current_time = datetime.now().strftime("%H:%M")
        self._speak(f"Şu an saat {current_time}")

    def open_youtube(self):
        """Kullanıcıdan aldığı girdiye göre YouTube'da arama yapar."""
        search_query = self._listen("YouTube'da ne aramak istersiniz?")
        if search_query:
            self._speak(f"{search_query} YouTube'da açılıyor.")
        
            encoded_query = re.sub(r'\s+', '+', search_query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            self._open_browser(url)
            
    def search_google(self):
        """Kullanıcıdan aldığı girdiye göre Google'da arama yapar."""
        search_query = self._listen("Google'da ne aramak istersiniz?")
        if search_query:
            self._speak(f"{search_query} için Google sonuçları açılıyor.")
            encoded_query = re.sub(r'\s+', '+', search_query)
            url = f"https://www.google.com/search?q={encoded_query}"
            self._open_browser(url)
            
    def _open_browser(self, url):
        """Verilen URL'yi bir tarayıcıda açar."""
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            driver.get(url)
        except Exception as e:
            self._speak("Tarayıcıyı başlatırken bir hata oluştu.")
            print(f"Tarayıcı hatası: {e}")

    def translate_text(self):
        """Bir cümleyi Türkçe'den İngilizce'ye çevirir ve kaydeder."""
        sentence = self._listen("Çevirmek istediğiniz cümleyi söyleyin.")
        if sentence:
            try:
                translated = self.translator.translate(sentence, src="tr", dest="en")
                self._speak(f"Çevirisi: {translated.text}")
                
                filename = self._get_unique_filename("ceviri", "txt")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"Orijinal: {sentence}\n")
                    f.write(f"Çeviri: {translated.text}\n")
                self._speak(f"Çeviri {filename} dosyasına kaydedildi.")
            except Exception as e:
                self._speak("Çeviri sırasında bir hata oluştu.")
                print(f"Çeviri hatası: {e}")

    def take_note(self):
        """Kullanıcının söylediklerini bir metin dosyasına kaydeder."""
        filename_prompt = self._listen("Dosyanın adı ne olsun?")
        if filename_prompt:
            filename = filename_prompt.replace(" ", "_") + ".txt"
            note_content = self._listen("Lütfen notunuzu söyleyin.")
            if note_content:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(note_content)
                self._speak(f"Notunuz {filename} dosyasına kaydedildi.")

    def get_weather(self):
        """Belirtilen şehrin hava durumu bilgisini verir."""
        if self.OPENWEATHERMAP_API_KEY == "BURAYA_API_ANAHTARINIZI_GIRIN":
            self._speak("Hava durumu servisini kullanmak için lütfen bir API anahtarı girin.")
            return
            
        city = self._listen("Hangi şehrin hava durumunu öğrenmek istersiniz?")
        if city:
            params = {"q": city, "appid": self.OPENWEATHERMAP_API_KEY, "units": "metric", "lang": "tr"}
            try:
                response = requests.get(self.WEATHER_API_URL, params=params)
                response.raise_for_status() # HTTP hatalarını kontrol et
                data = response.json()

                if data["cod"] == 200:
                    description = data["weather"][0]["description"]
                    temp = data["main"]["temp"]
                    humidity = data["main"]["humidity"]
                    report = f"{city} şehrinde hava {description}. Sıcaklık {temp:.0f} derece ve nem oranı %{humidity}."
                    self._speak(report)
                else:
                    self._speak(f"{city} için hava durumu bilgisi bulunamadı.")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    self._speak("Şehir bulunamadı. Lütfen tekrar deneyin.")
                else:
                    self._speak("Hava durumu servisine bağlanırken bir hata oluştu.")
                print(f"API hatası: {e}")
            except Exception as e:
                self._speak("Hava durumu alınırken beklenmedik bir hata oluştu.")
                print(f"Genel hata: {e}")


    def get_system_info(self):
        """CPU, RAM ve Disk kullanım bilgilerini sesli olarak bildirir."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        info = f"Sistem kaynak kullanımı şöyle: CPU yüzde {cpu}, RAM yüzde {ram}, ve disk yüzde {disk}."
        self._speak(info)

    def take_photo(self):
        """Kameradan anlık bir fotoğraf çeker ve kaydeder."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self._speak("Kamera bulunamadı veya açılamadı.")
            return

        ret, frame = cap.read()
        if ret:
            filename = self._get_unique_filename("fotograf", "jpg")
            cv2.imwrite(filename, frame)
            self._speak(f"Fotoğraf {filename} olarak kaydedildi.")
            cv2.imshow('Çekilen Fotoğraf', frame)
            cv2.waitKey(3000) # 3 saniye göster
            cv2.destroyAllWindows()
        else:
            self._speak("Görüntü alınamadı. Kamera hatası olabilir.")
        cap.release()
        
    def record_video(self):
        """Kameradan video kaydı yapar. Durdurmak için 'q' tuşuna basılır."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self._speak("Kamera bulunamadı veya açılamadı.")
            return

        filename = self._get_unique_filename("video", "avi")
        codec = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, codec, 20.0, (640, 480))

        self._speak("Video kaydı başladı. Kaydı durdurmak için kamera penceresi seçiliyken Q tuşuna basın.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                self._speak("Görüntü alınamadı, kayıt durduruluyor.")
                break
            
            out.write(frame)
            cv2.imshow('Video Kaydı (Durdurmak için Q)', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self._speak("Video kaydı tamamlandı ve kaydedildi.")
        cap.release()
        out.release()
        cv2.destroyAllWindows()


    def run(self):
        """Asistanı çalıştırır ve komutları dinlemeye başlar."""
        self.greet()
        print("\n--- Kullanılabilir Komutlar ---")
        print("Selam, Görüşürüz, Saat kaç, Hangi gündeyiz, Youtube aç, Google'da ara")
        print("Hava durumu, Not tut, Çevir, Sistem bilgisi, Fotoğraf çek, Video çek\n")
        
        while True:
            command = self._listen()
            if command:
                found_command = False
                for keywords, function in self.commands.items():
                    for keyword in keywords:
                        if keyword in command:
                            function()
                            found_command = True
                            break
                    if found_command:
                        break # ana döngüden çık
                
                if not found_command:
                    self._speak("Bu komutu anlayamadım.")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
