from playsound3 import playsound3
from gtts import gTTS
import speech_recognition as sr
import os
import time
from datetime import datetime
import random
from random import choice
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import json
import re
import psutil
import cv2

translator = Translator()
r = sr.Recognizer()

def kayit(ask = False):
    with sr.Microphone() as kaynak:
        if ask:
            print(ask)
        audio = r.listen(kaynak)
        ses = ""
        try:
            ses = r.recognize_google(audio, language="tr-TR")
        except sr.UnknownValueError:
            print("Dediğini anlamadım")
        except sr.RequestError:
            print("Sistem çalışmıyor")
        return ses
    
def cevap(ses):
    if "selam" in ses:
        soyle("Sana da selam")
        soyle("Yardımcı olmamı istediğin konuyu lütfen söyler misin?")
    elif "merhaba" in ses:
        soyle("Merhaba hoşgeldin")
        soyle("Bugün ne yapmamı istiyorsun")

    elif "görüşürüz" in ses:
        soyle("Görüşürüz tekrardan beklerim")
        exit()
    elif "sistemi kapat" in ses:
        soyle("Sistem 3 saniye sonra kapanacak")
        time.sleep(3)
        exit()

    elif "hangi gündeyiz" in ses:
        gün = time.strftime("%A")
        gün.capitalize()

        if gün == "Monday":
            gün = "Pazartesi"
        if gün == "Tuesday":
            gün = "Salı"
        if gün == "Wednesday":
            gün = "Çarşamba"
        if gün == "Thursday":
            gün = "Perşembe"
        if gün == "Friday":
            gün = "Cuma"
        if gün == "Saturday":
            gün = "Cumartesi"
        if gün == "Sunday":
            gün = "Pazar"
        soyle(gün)
        print(gün)

    elif "saat kaç" in ses or "zamanı söyle" in ses:
        seçim = ["Şu an saat", "Hemen söylüyorum: "]
        seçim = random.choice(seçim)
        saat = datetime.now().strftime("%H:%M")
        soyle(seçim + saat)

    elif "video aç" in ses or "şarkı aç" in ses or "youtube aç" in ses:
        soyle("Ne açmamı istiyorsun")
        bilgi = kayit()
        soyle("{} açılıyor...".format(bilgi))
        time.sleep(1)
        url = "https://www.youtube.com/results?search_query={}".format(bilgi)
        google = webdriver.Chrome()
        google.get(url)
        buton = google.find_element(By.XPATH, "//*")
    elif "google arama" in ses or "google aç" in ses:
        soyle("Ne araştırmak istiyorsun google'da")
        arama=kayit()
        soyle("{} için çıkan sonuçlar".format(arama))
        gogle = webdriver.Chrome()
        gogle.get(url)
        time.sleep(9000)

    elif "çevir" in ses:
        soyle("Lütfen çevirmek istediğiniz cümleyi söyleyin")
        cumle = kayit()
        cevrilen_cumle = translator.translate(cumle, src="tr", dest="en").text
        soyle("Çeviri: " + cevrilen_cumle)
        dosya = "cevir.txt"
        with open(dosya,"w",encoding="utf-8") as f:
            f.write(cevrilen_cumle)
        print("Çeviri kaydedildi.")
        soyle("Çeviri kaydedildi.")

    elif "not tut" in ses or "not al" in ses:
        soyle("Dosyanın ismi ne olsun?")
        belge = kayit() + ".txt"
        soyle("Ne yazdırmak istiyorsun?")
        thetext = kayit()
        f = open(belge, "w", encoding="utf-8")
        f.writelines(thetext)
        f.close()
    elif "hava durumu" in ses:
        soyle("Hangi şehirin hava durumunu öğrenmek istersiniz?")
        sehir = kayit()
        hava_durumu = hava_raporu(sehir)
        soyle(hava_durumu)
        print(hava_durumu)

    elif "sistem bilgisi" in ses or "bilgisayarın durumu" in ses:
        sistem_bilgisi()

    elif "fotoğraf çek" in ses:
        kamera = cv2.VideoCapture(0)
        cekildi, goruntu = kamera.read()
        if cekildi:
            cv2.imwrite("anlik_fotograf"+str(random.randint(0,20)),goruntu)
            cv2.imshow("Anlık Fotoğraf", goruntu)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            soyle("Fotoğraf kaydedildi.")
        else:
            soyle("Kamera Hatası")

    elif "video çek" in ses:
        kamera = cv2.VideoCapture(0)
        codec = cv2.VideoWriter_fourcc(*"XVID")
        dosya_adı = ("video" + str(random.randint(0,30))+".avi")
        fps = 30.0
        video_kaydedici = cv2.VideoWriter(dosya_adı, codec, fps,(640,480))

        while True:
            cekildi, goruntu = kamera.read()
            if cekildi:
                cv2.imshow("Video",goruntu)
                video_kaydedici.write(goruntu)
                if cv2.waitKey(1) == ord("q"):
                    break
            else: break

        kamera.release()
        video_kaydedici.release()
        cv2.destroyAllWindows()
        
def sistem_bilgisi():
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    bilgi = f"CPU Kullanımı: {cpu_usage}%, RAM Kullanımı: {ram_usage}%, Disk Kullanımı: {disk_usage}%"
    soyle(bilgi)
    print(bilgi)

API_KEY = ""

def hava_raporu(sehir):
    hava_url = ""
    params = {
        "q":sehir,
        "appid": API_KEY,
        "units": "metric",
        "lang": "tr"
    }
    cevap = requests.get(hava_url, params=params)
    veri = cevap.json()

    if veri["cod"] == "404":
        return "Şehir Bulunumadı"
    
    hava_tipi = veri["weather"][0]["description"]
    sıcaklık = veri["main"]["temp"]
    nem = veri["main"]["humidity"]

    hava_bilgisi = "{} şehrinde hava {}. Sıcaklık {} derece, nem oranı ise %{}".format(sehir,hava_tipi,sıcaklık,nem)
    return hava_bilgisi

def soyle(string):
    tts = gTTS(text=string, lang="tr")
    dosya = "cevap.mp3"
    tts.save(dosya)
    playsound3.playsound(dosya)
    os.remove(dosya)

# playsound3("beep6.mp3")
soyle("Selam")
print("Kullanabildiğim özellikler: Youtube Açma, Google Açma, Sistem Bilgisi, Hava Durumu, Foroğraf ve Video Çekme, Not Tutma, Çeviri, Saat ve Gün")


while True:
    ses = kayit()
    if ses!='':
        ses = ses.lower()
        print(ses)
        cevap(ses)