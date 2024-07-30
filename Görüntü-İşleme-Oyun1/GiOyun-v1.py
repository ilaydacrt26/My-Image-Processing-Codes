import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import numpy as np
import cvzone
import time
import random

# Webcam başlatma
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Genişlik
cap.set(4, 720)   # Yükseklik

# El tespitçisi başlatma
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Mesafe fonksiyonu için veriler
x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x, y, 2)

# Oyun değişkenleri
cx, cy = 250, 250  # Butonun başlangıç konumu
color = (255, 0, 255)  # Buton rengi
counter = 0  # Butona dokunma sayacı
score = 0  # Oyuncunun skoru
timeStart = time.time()  # Oyun süresi başlangıcı
totalTime = 20  # Toplam oyun süresi (saniye)

while True:
    success, img = cap.read()  # Kameradan görüntüyü oku
    img = cv2.flip(img, 1)  # Görüntüyü yatay olarak çevir
    
    if time.time() - timeStart < totalTime:  # Oyun süresi kontrolü
        
        # Elleri tespit et
        hands, img = detector.findHands(img, draw=False)
        
        if hands and len(hands) > 0:
            lmList = hands[0]['lmList']  # El noktaları listesi
            bbox = hands[0]['bbox']  # Elin sınırlayıcı kutusu (bounding box)
            
            x1, y1 = lmList[5][0], lmList[5][1]  # İşaret parmağı noktası
            x2, y2 = lmList[17][0], lmList[17][1]  # Serçe parmak noktası
            
            # İki nokta arasındaki mesafe hesaplama
            distance = int(math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2))
            A, B, C = coff
            distanceCM = A * distance ** 2 + B * distance + C
            
            # Belirli bir mesafenin üzerindeyse butonu kontrol et
            if distanceCM > 40:
                if bbox[0] < cx < bbox[0] + bbox[2] and bbox[1] < cy < bbox[1] + bbox[3]:
                    counter = 1
            
            # Elin sınırlayıcı kutusunu çiz
            cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (255, 0, 255), 3)
            cvzone.putTextRect(img, f'{int(distanceCM)} cm', (bbox[0] + 5, bbox[1] - 10))
        
        if counter:
            counter += 1
            color = (0, 255, 0)
            if counter == 3:
                cx = random.randint(100, 1100)  # Butonun yeni x konumu
                cy = random.randint(100, 600)  # Butonun yeni y konumu
                color = (255, 0, 255)
                score += 1
        
        # Butonu çiz
        cv2.circle(img, (cx, cy), 30, color, cv2.FILLED)
        cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 20, (255, 255, 255), 2)
        cv2.circle(img, (cx, cy), 30, (50, 50, 50), 2)
        
        # Oyun ekranı üzerinde bilgileri göster
        cvzone.putTextRect(img, f'Zaman: {int(totalTime - (time.time() - timeStart))}', (1000, 75), scale=3, offset=20)
        cvzone.putTextRect(img, f'Skor: {str(score).zfill(2)}', (60, 75), scale=3, offset=20)
    
    else:
        # Oyun bittiğinde sonuçları göster
        cvzone.putTextRect(img, 'Oyun Bitti', (300, 400), scale=9, offset=30, thickness=20)
        cvzone.putTextRect(img, f'Skorunuz: {score}', (475, 500), scale=3, offset=20)
        cvzone.putTextRect(img, 'Yeniden Baslatmak Icin R Tusuna Basiniz.', (350, 575), scale=2, offset=10)
    
    cv2.imshow("Image", img)  # Görüntüyü göster
    
    key = cv2.waitKey(1)  # Klavye girişini bekle
    
    if key == ord('r'):  # R tuşuna basıldığında oyunu yeniden başlat
        timeStart = time.time()
        score = 0
    
    if key == 27:  # ESC tuşuna basıldığında çıkış yap
        break

# Kamerayı serbest bırak ve pencereyi kapat
cap.release()
cv2.destroyAllWindows()
