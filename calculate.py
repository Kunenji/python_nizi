# -*- coding:utf-8 -*-
import requests
import json
import datetime
from math import pi, e, atan, sin, cos, tan, radians, asin, degrees, ceil, log
from staticmap import StaticMap
from PIL import ImageDraw
import schedule
from time import sleep





def main():
    now1 = datetime.datetime.now()
    now = now1 + datetime.timedelta(minutes=30)
    #太陽高度・太陽方位角を求める
    def sun_altitude():
        year = int(now.year) - 2000
        month = int(now.month)
        if  month == 1 or month == 2:
            month += 12
            year -= 1
        day = int(now.day)
        K_prime = 365 * year + 30 * month + day - 33.875 + ((3 * month + 3) // 5) + (year//4)

        hour = int(now.hour)
        minute = int(now.minute)
        K_delta = (hour+minute/60)/24
        T_delta = year + 65
        T = (K_prime + K_delta + (T_delta/86400))/365.25
        s_lambda = (280.4603 + 360.00769 * T + (1.9146-0.00005*T) * sin(radians(357.538+359.991*T)) + 0.02 * sin(radians(355.05+719.981*T)) + 0.0048 * sin(radians(234.95+19.341*T)) + 0.002 * sin(radians(247.1+329.64*T))
                    + 0.0018 * sin(radians(251.3+0.2*T)) + 0.0015 * sin(radians(343.2+450.37*T)) + 0.0013 * sin(radians(81.4+225.18*T)) + 0.0008 * sin(radians(132.5+659.29*T))
                    + 0.0007 * sin(radians(153.3+90.38*T)) + 0.0007 * sin(radians(206.8+30.35*T))  + 0.0006 * sin(radians(29.8+337.18*T)) + 0.0005 * sin(radians(207.4+1.5*T))
                    + 0.0005 * sin(radians(291.2+22.81*T)) + 0.0004 * sin(radians(234.9+315.56*T)) + 0.0004 * sin(radians(157.3+299.3*T)) + 0.0004 * sin(radians(21.1+720.02*T))
                    + 0.0003 * sin(radians(352.5+1079.97*T)) + 0.0003 * sin(radians(329.7+44.43*T)))
        s_lambda -=  360 * (s_lambda // 360)
        epsilon = 23.439291 - 0.000130042 * T
        lat_tokyo = 35.6544
        lon_tokyo = 139.7447
        Theta = 325.4606+360.007700536 * T + 0.00000003879 * T * T + 360 * K_delta + lon_tokyo
        tanalpha = tan(radians(s_lambda)) * cos(radians(epsilon))
        if 0<= s_lambda <180:
            if tanalpha > 0:
                alpha = degrees(atan(tanalpha))
            else:
                alpha = 180 + degrees(atan(tanalpha))
        elif 180 <= s_lambda <= 360: 
            if tanalpha > 0:
                alpha = degrees(atan(tanalpha)) + 180
            else:
                alpha = 360 + degrees(atan(tanalpha))
        delta = asin(sin(radians(s_lambda)) * sin(radians(epsilon)))
        t = radians(Theta - alpha)

        tanA = (-cos(delta) * sin(t)) / (sin(delta) * cos(radians(lat_tokyo)) - cos(delta) * sin(radians(lat_tokyo)) * cos(t)) 
        h = degrees(asin(sin(delta) * sin(radians(lat_tokyo)) + cos(delta) * cos(radians(lat_tokyo)) * cos(t)))
        A = degrees(atan(tanA))     
        if 7 <= hour < 13 and tanA < 0:
            A = degrees(atan(tanA)) + 180
        elif 11 <= hour < 18 and tanA > 0: 
            A = degrees(atan(tanA)) + 180
        elif (14 <= hour <= 23 or hour == 0) and tanA < 0:
            A = degrees(atan(tanA)) + 360    


        """  
        if -cos(delta) * sin(t) > 0:
            A = degrees(atan(tanA))

        elif -cos(delta) * sin(t) < 0:
            if hour >=16:
                A = degrees(atan(tanA)) + 360
            else:
                A = degrees(atan(tanA)) + 180

            
        else:
            if sin(t) < 0:
                A = 90
            if sin(t) == 0:
                h = 90
        """        

        return(h,A)      



    #exit()条件
    altitude, angle = sun_altitude()
    if altitude <= 0 or 37 < altitude:
        print('見られません', now1)
        return False



    #　タイルと緯度経度の返還
    def tile2latlon(x, y):
        lon = (x / 2.0**15) * 360 - 180 # 経度（東経）
        mapy = (y / 2.0**15) * 2 * pi - pi
        lat = 2 * atan(e ** (- mapy)) * 180 / pi - 90 # 緯度（北緯）
        return lon, lat
            


    # Yahoo weather APIにて気象情報を取得する
    rainfall_list = [[0]*40 for _ in range(40)]    
    for i in range(40):
        for j in range(4):
            lonlatlist = []
            x = 29084 + 10 * j
            y = 12886 + i
            for k in range(10):
                lon, lat = tile2latlon(x+k,y)
                lon_lat = str(lon) + ',' +str(lat)
                lonlatlist.append(lon_lat)
                lonlat = ' '.join(lonlatlist)
            yahoo_url = "https://map.yahooapis.jp/weather/V1/place?appid={appid}&coordinates={lat_lon}&output={output}&date={date}"
            yahoo_url = yahoo_url.format(appid="dj00aiZpPThKVm5Wckw5RVRYQyZzPWNvbnN1bWVyc2VjcmV0Jng9OWQ-", lat_lon= lonlat, output="json",
                                date=now1.strftime("%Y%m%d%H%M"))
            yahoo_json = requests.get(yahoo_url).json()
            for k in range(10):
                yahoo_rainfall = yahoo_json["Feature"][k]["Property"]["WeatherList"]["Weather"][3]["Rainfall"]
                rainfall_list[i][10*j+k] = round(yahoo_rainfall)



    #降水量の強い場所を求める
    strong_rain = []
    for i in range(40):
        for j in range(40):
            if rainfall_list[i][j] >= 15:
                strong_rain.append([i,j])
    if len(strong_rain) == 0:
        print('見られません', now1) 
        return False           



    #虹が見れる座標を求める
    rainbow = []
    rainbowfake = []
    for i in range(40):
        for j in range(40):
            if rainfall_list[i][j] > 0:
                Flag = False
                for k in range(len(strong_rain)):
                    if (i - strong_rain[k][0]) ** 2 + (j - strong_rain[k][1]) ** 2 < 50:
                        Flag = True
                if Flag == True:
                    minx = int(sin(radians(angle)) / (2 * tan(radians(42 - altitude))))
                    maxx = int(3*sin(radians(angle)) / (2 * tan(radians(42 - altitude))))
                    if minx <= maxx:
                        for dx in range(minx,maxx+1):
                            dy = -ceil(dx/tan(radians(angle)))
                            if 4 <= i+dy < 36 and 4 <= j+dx < 36:
                                if rainfall_list[i+dy][j+dx] == 0:    
                                    if [i+dy,j+dx] not in rainbowfake:
                                        rainbowfake.append([i+dy,j+dx])    
                                        resultx, resulty = tile2latlon(j+dx+29089, i+dy+12891)
                                        rainbow.append([resultx, resulty])          

                    else:
                        for dx in range(maxx,minx+1):
                            dy = -ceil(dx/tan(radians(angle)))
                            if 4 <= i+dy < 36 and 4 <= j+dx < 36:
                                if rainfall_list[i+dy][j+dx] == 0:
                                    if [i+dy,j+dx] not in rainbowfake:
                                        rainbowfake.append([i+dy,j+dx])  
                                        resultx, resulty = tile2latlon(j+dx+29089, i+dy+12891)
                                        rainbow.append([resultx, resulty])    
    if rainbow == []:
        print("見られません", now1)
        return False


    def lon_to_pixel(lon, map):
        # 経度→タイル番号
        if not (-180 <= lon <= 180):
            lon = (lon + 180) % 360 - 180
        x = ((lon + 180.) / 360) * pow(2, map.zoom)
        # タイル番号→キャンバスの座標
        pixel = (x - map.x_center) * map.tile_size + map.width / 2
        return int(round(pixel))

    def lat_to_pixel(lat, map):
        # 緯度→タイル番号
        if not (-90 <= lat <= 90):
            lat = (lat + 90) % 180 - 90
        y = (1 - log(tan(lat * pi / 180) + 1 / cos(lat * pi / 180)) / pi) / 2 * pow(2, map.zoom)
        # タイル番号→キャンバスの座標
        pixel = (y - map.y_center) * map.tile_size + map.height / 2
        return int(round(pixel))
        
    def simple_map():
        map = StaticMap(1280, 1280, url_template="https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png")
        
        img = map.render(zoom=12, center=[139.7588499, 35.6769883])
        # 表示
        draw = ImageDraw.Draw(img)
        for point in rainbow:
            x = lon_to_pixel(point[0], map)
            y = lat_to_pixel(point[1], map)
            draw.ellipse([(x-10,y-10),(x+10,y+10)], fill = 'red')
        img.save('rainbow.png', format='PNG') 
    simple_map()


    # 取得したTokenを代入
    line_notify_token = 'TfSpQccfUviGgTOl03p62BRb4XuMkxX5UYZsUcCtE5V'

    # 送信したいメッセージ
    message = '30分後に虹が見えると予測される場所'

    # Line Notifyを使った、送信部分
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'{message}'}
    # 送信用の画像を準備
    files = {"imageFile": open("rainbow.png", "rb")}
    requests.post(line_notify_api, headers=headers, data=data, files=files)



schedule.every(30).minutes.do(main)


#03 イベント実行
while True:
    schedule.run_pending()
    sleep(1)

