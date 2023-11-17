
import cv2
import time
import numpy as np
from pymavlink import mavutil
import buzzer


master = mavutil.mavlink_connection('udpin:localhost:14550')
master.wait_heartbeat()

buzzer.BUZZER()
def set_rc_channel_pwm(channel_id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        channel_id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if channel_id < 1 or channel_id > 18:
        print("Channel does not exist.")
        return
    
    rc_channel_values = [65535 for _ in range(18)]
    rc_channel_values[channel_id - 1] = pwm
    master.mav.rc_channels_override_send(
        master.target_system,                # target_system
        master.target_component,             # target_component
        *rc_channel_values)
    
set_rc_channel_pwm(2, pwm=1500)
set_rc_channel_pwm(3, pwm=1500)
set_rc_channel_pwm(4, pwm=1500)
set_rc_channel_pwm(5, pwm=1500)

kernel = np.ones((25,25),np.uint8)

cap = cv2.VideoCapture(0)

kontrol = 0
AsYu_D = 1500
islem_sonucu = "merkezde"
islem_sonucu1 = "merkezde"

while True:
    _,frame = cap.read()
    frame= cv2.flip(frame,0)
    frame = cv2.flip(frame,1)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([136, 87, 11])
    upper_red = np.array([180, 255, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    kapatma_filitresi = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)


    Sonuc = frame.copy()
    Olculer = Sonuc.shape
    

    cnts, contours = cv2.findContours(kapatma_filitresi, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    max_genislik = 0
    max_uzunluk = 0
    max_index = -1

    center = cv2.circle(Sonuc, (Olculer[1] // 2, Olculer[0] // 2), 4, (0, 0, 255), -1)
    if len(cnts) == 0:
        
        if kontrol == 0:
            kontrol = 1
            zaman= time.time()
        
        son_zaman = time.time()
        if son_zaman-zaman >=3:
            set_rc_channel_pwm(3, pwm=1580)
            islem_sonucu1 = "engel araniyor..."
            print("engel aranıyo")
    if len(cnts) > 0:
        kontrol = 0
        
        for t in range(len(cnts)):
            cnt = cnts[t]
            x,y, w, h = cv2.boundingRect(cnt)
            if (w > max_genislik and h > max_uzunluk):
                max_uzunluk = h
                max_genislik = w
                max_index = t
        x, y, w, h = cv2.boundingRect(cnts[max_index])
        cv2.rectangle(Sonuc, (x, y), (x + w, y + h), (0, 255, 0), 2)
        merkez = cv2.circle(Sonuc, (x + (w // 2), y + (h // 2)), 2, (0, 255, 0), 2)
        resim_zaman = round(time.time(),0)
        if resim_zaman %2 == 0:
            
            cv2.imwrite(str(resim_zaman)+".jpg",Sonuc)
            

        if (x + (w // 2)) < 260:
            print("sola")
            islem_sonucu1 = str(300 - (x + (w // 2))) + " birim Sola"
            set_rc_channel_pwm(4, pwm=1600)
            set_rc_channel_pwm(5, pwm=1500)
            time.sleep(0.2)


        elif 260 <= (x + (w // 2)) <= 360:
            #print("tamam")
            islem_sonucu1 = "yataya gore merkezde"
            set_rc_channel_pwm(4, pwm=1500)
            set_rc_channel_pwm(5, pwm=1200)
            time.sleep(0.2)

        else:
            #print("sola")
            islem_sonucu1 = str((x + (w // 2)) - 360) + " birim Saga"
            set_rc_channel_pwm(4, pwm=1400)
            set_rc_channel_pwm(5, pwm=1500)
            print("saga")
            time.sleep(0.2)
        if (y + (h // 2)) < 200:
            #print("aşağı")
            islem_sonucu = str(200 - (y + (h // 2))) + " birim yukarı"
            
            if AsYu_D <= 1100:
                pass
            else:
                AsYu_D -= 10
                set_rc_channel_pwm(3, pwm=AsYu_D)
                
            print("yukari")
    
        elif 200 <= (y + (h // 2)) <= 260:
            #print("tamam")
            islem_sonucu = "dikeye gore merkezde"
            set_rc_channel_pwm(3, pwm=1500)
            
        else:
            print("asagi")
            islem_sonucu = str((y + (h // 2)) - 260) + " birim asagı"
            if AsYu_D >= 1900:
                pass
            else:
                AsYu_D += 10
                set_rc_channel_pwm(3, pwm=AsYu_D)
               

            
       
    yazi1 = cv2.putText(Sonuc, islem_sonucu, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    yazi2 = cv2.putText(Sonuc, islem_sonucu1, (320, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    cv2.imshow("goruntu", kapatma_filitresi)
    cv2.imshow("yeho", frame)
    cv2.imshow("mask", mask)
    cv2.imshow("sonuc", Sonuc)
    
    


    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        break




