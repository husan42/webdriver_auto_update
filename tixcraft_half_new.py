#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''
加入狀態變已售完時暫停重整網頁
加入設定想要購買的區域
'''


# In[2]:


import threading
import time,re,json
from datetime import datetime
import requests
from selenium import webdriver
#for selenium v4
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException ,NoSuchWindowException


from Model.webdriver_auto_update import check_driver
from PIL import Image
import numpy as np
from keras.models import load_model, Model
import cv2
import tensorflow as tf
#gpu_options = tf.GPUOptions(allow_growth=True)##per_process_gpu_memory_fraction = 0.8
#sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
import urllib
import shutil
import random

import sys,os

#隱藏tensorflow log
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

# Pass in the folder used for storing/downloading chromedriver
#download_latest_version("110.0.5481.77","Model")
check_driver("Model")
# In[1]:


run = True  # global variable to control whether send packet or not
stop = False  # global variable to control quit the program


# In[3]:


def test_predict():
    prediction1 = model.predict(np.stack([np.array(Image.open('Model/init_model.png'))/255.0]), verbose=0)
    print("pre predict")
    
print("初始化model...")
model = load_model("Model/model_pic1.h5")
LETTERSTR = "abcdefghijklmnopqrstuvwxyz"
test_predict()

# In[4]:

def init_chrome():
    print("初始化chrome...")
    #chrome_options = Options()
    chrome_options=webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=1280,1024")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("detach", True)#driver關閉時瀏覽器保持開啟
    chrome_options.page_load_strategy = 'eager'# normal、eager、none
    #chrome_options.add_argument('--headless') #隱藏瀏覽器
    ser = Service(r"Model/chromedriver")
    driver = webdriver.Chrome(service=ser,options=chrome_options)
    driver.get('https://tixcraft.com/')
    time.sleep(1)
    wait = WebDriverWait(driver, 5)
    try:
        element = wait.until(EC.element_to_be_clickable((By.ID,"onetrust-accept-btn-handler")))
        element.click()
    except TimeoutException:
        print("無接受Cookie按鈕")
    '''
    if len(driver.find_elements(By.ID,"onetrust-accept-btn-handler")) != 0:
        print("接受所有Cookie")
        driver.find_elements(By.ID,"onetrust-accept-btn-handler")[0].click()
    '''
    print("開啟chrome瀏覽器...OK")
    return driver

driver = init_chrome()
# In[ ]:





# In[ ]:


def ticket():
    global config
    w_ticket_num = config['w_ticket_num']
    #print (driver.get_window_size())
    driver.save_screenshot('Model/captcha.png')
   # print (driver.find_element_by_id('yw0').location)#id="TicketForm_verifyCode-image"
    location = driver.find_element(By.ID,"TicketForm_verifyCode-image").location
    x, y = location['x'] ,location['y']
    #print (x,y)
    im = Image.open('Model/captcha.png')
    #im = im.crop((1024, 1257, 1324, 1507))
    im = im.crop((x, y, x+120, y+100))
    im.convert("RGB").save('Model/code.png', 'PNG')
    #im.save('code.png')
    img1 = Image.open('Model/code.png')
    img1 = img1.resize((120, 100), Image.Resampling.BILINEAR)
    img1.save('Model/code1.png')
    
    prediction1 = model.predict(np.stack([np.array(Image.open('Model/code1.png'))/255.0]), verbose=0)#
    answer = ""
    
    for predict in prediction1:
        answer += LETTERSTR[np.argmax(predict[0])]
    print ("預測驗證碼:",answer)
    
    #sl = Select(driver.find_element_by_id('TicketForm_ticketPrice_01'))#01第幾區
    
    num = 1
    tic = False
    while not tic:
        if (num >= 120):
            tic = True
        else:
            try:
                if (num < 10):
                    find_id = 'TicketForm_ticketPrice_0'+ str(num)
                    sl = Select(driver.find_element(By.ID,find_id))
                    #print (tic)
                    tic = True
                else:
                    find_id = 'TicketForm_ticketPrice_'+ str(num)
                    sl = Select(driver.find_element(By.ID,find_id))
                    #print (tic)
                    tic = True
            except:
                num += 1


    if len (sl.options) - 1 < w_ticket_num:
        driver.find_element(By.ID,find_id).send_keys(len (sl.options) - 1)
        print(f"少於想要數量，選擇全部數量:{len (sl.options) - 1}")
    else:
        driver.find_element(By.ID,find_id).send_keys(w_ticket_num)
        print(f"選擇想要數量:{w_ticket_num}")
    driver.find_element(By.ID,'TicketForm_verifyCode').clear()
    driver.find_element(By.ID,'TicketForm_verifyCode').send_keys(answer)
    driver.find_element(By.ID,'TicketForm_agree').click()
    driver.find_element(By.CLASS_NAME,"btn-green").click()#class="btn btn-primary btn-green"
    try:
        driver.switch_to_alert().accept()
    except:
        print('',end='')


# In[ ]:


def find_verify():
    global run
    found = False
    while run:
        try:
            driver.find_element(By.ID,'TicketForm_verifyCode')
            ticket()
            #found = True
        except:
            continue


# In[1]:

#回到選位頁面
def back_choose_area(driver,config):
    driver.get(f"https://tixcraft.com/ticket/area/{config['concert']}/{config['ticket_day']}")
    return True

#列出所有可購區域，隨機點選區域    
def show_can_buy_area(driver,config):
    concert,ticket_day = guest_area()
    #driver.find_elements(By.CLASS_NAME,"select_form_a")
    can_buy_area_a = [el for el in driver.find_elements(By.CLASS_NAME,r"select_form_a")]
    can_buy_area_b = [el for el in driver.find_elements(By.CLASS_NAME,r"select_form_b")]
    can_buy_area = can_buy_area_a + can_buy_area_b
    if len(can_buy_area) == 0:
        print("無可選區域")
        return False
    else:
        
        ran = random.choice(can_buy_area)
        print("選擇:",ran.text)
        ran.click()
        return True
        
        
def ticket_handle():
    '''
    10>購買失敗
    11>驗證碼錯誤
    12>無連續座位
    13>無足夠數量
    14>已售完
    
    1>detail頁面
    2>game頁面
    3>回答問題頁面
    4>area選位頁面
    5>ticket驗證碼頁面
    6>轉圈...
    7>check
    8>payment
    9>購票成功-測試
    10>首頁
    
    403>Forbidden
    404>Not Found
    502>Gateway Timeout
    '''
    global run
    try:
        WebDriverWait(driver, 0.5).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')
        alert = driver.switch_to.alert
        print("通知:",alert.text)
        alert_notice = alert.text
        alert.accept()#關閉通知
        print("關閉通知。")
        #購買失敗繼續重新選購
        
        '''
        通知: 您所輸入的驗證碼適用下列

        購票驗證，答對方可進入購票

        驗證碼正確，請按確認到下一頁
        關閉通知。
        您所輸入的驗證碼適用下列

        購票驗證，答對方可進入購票

        驗證碼正確，請按確認到下一頁
        '''
        if "驗證碼不正確" in alert_notice:
            print(alert_notice)
            #ticket()
            return 11
        elif "無足夠連續座位" in alert_notice:
            print(alert_notice)
            return 12
        elif "已無足夠數量" in alert_notice:
            print(alert_notice)
            return 13
        elif "已售完" in alert_notice:
            print(alert_notice)
            return 14
        print(alert_notice)
        return 10
    except NoSuchWindowException:
        print("未開啟瀏覽器，請輸入openweb開啟瀏覽器。")
        run = False
    except :#TimeoutException
        #1>還在轉圈
        #2>購買成功變成ticket/payment
        try:
            #print(driver.current_url)
            if "activity/detail" in driver.current_url:
                print("——————購票頁——————")
                return 1
            elif "activity/game" in driver.current_url:
                print("————等待購買頁————")
                return 2
            elif "ticket/verify" in driver.current_url: 
                #https://tixcraft.com/ticket/verify/19_Jolin/5818
                #https://tixcraft.com/ticket/verify/23_afkh/14181
                print("————回答問題頁————")
                return 3
            elif "ticket/area" in driver.current_url:
                print("————選擇座位頁————")
                return 4
            elif "ticket/ticket" in driver.current_url:
                print("———輸入驗證碼頁———")
                return 5
            elif "ticket/order" in driver.current_url:
                #print('already in wait order...')
                print(".",end='')
                return 6
            elif "ticket/check" in driver.current_url:
                #https://tixcraft.com/ticket/checkout
                print('————確認訂單頁————')
                return 7
            elif "ticket/payment" in driver.current_url:
                print("—————購票成功—————")
                return 8
            elif "tixcraft.com/login" in driver.current_url:
                print("———購票成功-測試———")
                return 9
            elif "https://tixcraft.com/" == driver.current_url:
                print("———————首頁———————")
                return 10
            else:
                return 99
        except Exception as e:
            print(e)
        
def auto_choose():
    #"ticket/area"
    global config, run
    while run:
        back_choose_area(driver,config)
        if show_can_buy_area(driver,config):
            if len (driver.find_elements(By.ID,'TicketForm_verifyCode')) != 0:
                print("進入購票頁")
                ticket()
                while run:
                    state = ticket_handle()
                    if state == 6:#還在轉圈
                        time.sleep(1)
                        continue
                    elif state == 11:#驗證碼錯誤
                        ticket()
                    elif state == 7 or state == 8 or state == 9:#成功
                        sent_notify("qf5B3khYoGH08KAvDBfKZgYsDQmbqhNVE7ah4WGxlHg","購票成功!!")
                        run = False#程式停止
                        break
                    else:
                        break
        print("---")
        time.sleep(config['rate'])#選位頁面F5速度

#detail to game
def detail():
    global config
    if "activity/detail" in driver.current_url:
        url = driver.current_url
        url = url.split("/")
        concert = url[5]
        config['concert'] = concert#設定concert
        driver.get(f"https://tixcraft.com/activity/game/{concert}")#轉game
        print(f"https://tixcraft.com/activity/game/{concert}")
        return f"https://tixcraft.com/activity/game/{concert}"
    else:
        return False

#game
def game():
    global config
    #config['sale_time'] = "15:30:00"#開賣時間
    #config['num_button'] = 0 #購買按鈕第幾個
    if "activity/game" in driver.current_url:
        #等待開賣重整網頁，可能延遲需要再次重整網頁 要判斷時間
        #有按鈕後點選按鈕
        time_now = datetime.now()
        current_time = time_now.strftime("%H:%M:%S")
        if current_time >= config['sale_time']:
            print(current_time ,">=",config['sale_time'],"，已開賣")#開賣 next
            
            try:
                driver.refresh()
                #應該要等網頁出來class="btn btn-primary text-bold m-0"
                button_list = [name for name in driver.find_elements(By.XPATH,'//button[@class="btn btn-primary text-bold m-0"]')]
                if len(button_list) != 0:
                    ticket_day = button_list[config['num_button'] - 1].get_attribute("data-href").split("/")[6]
                    config['ticket_day'] = ticket_day #設定ticket_day
                    button_list[config['num_button'] - 1].click()#點擊立即訂購按鈕
                    return True
                else:
                    print("無立即購買按鈕...")
                    return False
            except Exception as e:
                print(e)
                return False
        else:
            #未開賣，繼續等
            print(current_time ,"<",config['sale_time'],"，尚未開賣")
    else:
        return False

#選位子
def area():
    global config, run
    if "ticket/area" in driver.current_url:
        concert,ticket_day = guest_area()
        #driver.find_elements(By.CLASS_NAME,"select_form_a")
        can_buy_area_a = [el for el in driver.find_elements(By.CLASS_NAME,r"select_form_a") if config['want_area'] in el.text]
        can_buy_area_b = [el for el in driver.find_elements(By.CLASS_NAME,r"select_form_b") if config['want_area'] in el.text]
        can_buy_area = can_buy_area_a + can_buy_area_b #所有可購買與符合想購買的位置清單
        if len(can_buy_area) == 0:
            print("無符合想要位置，隨機選擇位置")
            can_buy_area_a = [el for el in driver.find_elements(By.CLASS_NAME,r"select_form_a")]
            can_buy_area_b = [el for el in driver.find_elements(By.CLASS_NAME,r"select_form_b")]
            can_buy_area = can_buy_area_a + can_buy_area_b #所有可購買的位置清單
        if len(can_buy_area) == 0:
            print(f"無可選位置，等待{config['rate']}秒重新整理網頁...")
            time.sleep(config['rate'])#選位頁面F5速度
            back_choose_area(driver,config)#重整網頁
            return False
        else:
            #選擇位置
            #random
            ran = random.choice(can_buy_area)
            print("選擇:",ran.text)
            ran.find_element(By.XPATH,'a').click()
            return True
    else:
        return False

#order
def order():
    print("轉圈等待中...")
    time.sleep(1)
    return True

"""
開賣時間
按鈕位置
位置名稱
"""
def core():
    global run, config
    while run:
        state = ticket_handle()
        if (state in [1,2,10,99]) and config['auto'] and config['concert'] and config['ticket_day']:
            print("有設定日期代碼，直達選位")
            back_choose_area(driver,config)
        elif state == 10 and config['concert']:
            print("driver轉game")
            driver.get(f"https://tixcraft.com/activity/game/{config['concert']}")#轉game
        elif state == 10 and config['auto'] and not config['concert']:
            print("自動購票模式，未設定購買節目!")
        elif state == 1 and config['auto']:
            print("driver轉game")
            detail()
        elif state == 2 and config['auto']:
            print("等開賣重整網頁")
            game()
        elif state == 3 and config['auto']:
            print("輸入問題頁面")
        elif state == 4 and config['auto']:
            print("自動選位置，如沒有要的位置改成隨機選")
            area()
        elif state == 5:
            print("驗證碼頁面，選張數 ")
            ticket()
        elif state == 6:
            #轉圈等待中
            order()
        elif state == 7:
            #確認訂單畫面
            sent_notify("qf5B3khYoGH08KAvDBfKZgYsDQmbqhNVE7ah4WGxlHg","購票成功!!")
            run = False#程式停止
        elif state == 8:
            #payment
            sent_notify("qf5B3khYoGH08KAvDBfKZgYsDQmbqhNVE7ah4WGxlHg","購票成功!!")
            run = False#程式停止
        elif state == 9:
            #登入畫面
            #sent_notify("qf5B3khYoGH08KAvDBfKZgYsDQmbqhNVE7ah4WGxlHg","購票成功!!")
            run = False#程式停止
        elif state == 99 and config['auto']:
            back_choose_area(driver,config)
        elif not config['auto']:
            print("",end="")
        else:
            print("not define web",state,config['auto'])


def guest_area():
    print("猜區域")
    url = driver.current_url
    url = url.split("/")
    try:
        concert = url[5]
        try:
            ticket_day = url[6]
        except:
            ticket_day = None
    except:
        concert, ticket_day = None,None
    print("concert:",concert,",ticket_day:",ticket_day)
    return concert,ticket_day

#傳送line notify
def sent_notify(token,message):
#token="qf5B3khYoGH08KAvDBfKZgYsDQmbqhNVE7ah4WGxlHg"
    headers = {
        "Authorization":"Bearer " + token,
        "Content-Type":"application/x-www-form-urlencoded"
    }
    params = {
        "message": message
    }
    r = requests.post("https://notify-api.line.me/api/notify",headers=headers,params=params)
    return r.status_code

def handle_process():
    global run, stop, isset, config
    while True:
        try:
            if isset:
                setup()
                isset = False #setup done
                continue
            if run:
                #do run
                '''
                if config['auto'] == False:
                    #print("手動選位")
                    find_verify()
                else:
                    #print("清票模式")
                    auto_choose()
                '''
                core()
                continue
            elif stop:
                break
            time.sleep(0.5)
        except Exception as e:
            print(e)
            print("重啟process...")
            time.sleep(3)


# In[2]:


def handle_user_input():
    global run, stop, isset, config
    while True:
        if not isset:
            print("狀態:run > ",str(run),",stop > ",str(stop),",isset > ",str(isset),",auto > ",config['auto'])
            flag = input("Input the command?(run/pause/setup/openweb/quit)：")
            #print(flag.casefold())
            clear_output(wait=False) # 立即清空目前 cell 的內容

            if flag.casefold() == 'run':
                print('開始執行')
                run = True
            elif flag.casefold() == 'pause':
                print('暫停執行')
                run = False
            elif flag.casefold() == 'setup':
                print('設定')
                isset = True
                print('暫停執行')#設定時暫停執行
                run = False
            elif flag.casefold() == 'quit':
                run = False
                stop = True
                break
            elif flag.casefold() == 'openweb':
                global driver
                driver = init_chrome()
            elif flag.casefold() == 'show':
                print(config)
            elif flag.casefold() == 'save':
                # create json object from dictionary
                conf_json = json.dumps(config)
                # open file for writing, "w" 
                f = open("Model/config.json","w")
                # write json object to file
                f.write(conf_json)
                # close file
                f.close()
            elif flag.casefold() == 'load':
                with open("Model/config.json") as conf_json:
                    config = json.load(conf_json)
                print("load save config")
                print(config)
            elif flag == '':
                continue
            elif flag == '?' or flag.casefold() == 'help' or flag.casefold() == 'h':
                print("—————————————————————————","run > 開始執行","pause > 暫停程式","setup > 設定搶票參數","save > 將參數儲存","load > 將上次儲存參數載入","openweb > 開啟瀏覽器","quit > 關閉程式","—————————————————————————",sep='\n')
                continue
            else:
                print("Invalid command.")
        
    


# In[ ]:


def setup():
    global run, stop, config
    print("------------------------------------")
    try:
        w_ticket_num = int(input("想要買幾張票?：") or "4")
        config['w_ticket_num'] = w_ticket_num
        
        auto = input("開啟清票模式?(yes/no)：")
        if auto.casefold() == "yes":
            config['auto'] = True
            concert,ticket_day = guest_area()
            if concert :
                ans =input(f"演唱會代碼:{concert}? (yes/no) :")
                if ans.casefold() == "yes":
                    config['concert'] = concert
                else:
                    config['concert'] = input("輸入演唱會代碼：")
            else:
                config['concert'] = input("輸入演唱會代碼：")
            
            if ticket_day:
                ans =input(f"日期代碼:{ticket_day}? (yes/no) :")
                if ans.casefold() == "yes":
                    config['ticket_day'] = ticket_day
                else:
                    config['ticket_day'] = input("輸入日期代碼，若未知可留空：")
            else:
                config['ticket_day'] = input("輸入日期代碼，若未知可留空：")
            
            if not config['concert'] or not config['ticket_day']:
                config['num_button'] = int(input(f"第幾個按鈕，從1開始，預設1：") or "1")
            else:
                config['num_button'] = 1
            config['sale_time'] = input(f"開賣時間，例如12:00:00，預設00:00:01：") or "00:00:01"
            config['want_area'] = input(f"輸入想要購買的位置關鍵字，若無可留空：") or ""
            config['rate'] = int(input("選位頁重整速度/秒，預設1次/秒：") or "1")
        else:
            config['auto'] = False
            config['concert'] = None
            config['ticket_day'] = None
            config['sale_time'] = "00:00:01"
            config['num_button'] = 1
            config['want_area'] = ""
            config['rate'] = 1
        
        
        '''
        priority = input("Input priority?(up/down)：")
        config['priority'] = priority
        '''
    except:
        print("設定錯誤，請重新設定!!!")
    
    print("------------------------------------")
    print("w_ticket_num:",config['w_ticket_num'])
    print("auto:",config['auto'],",演唱會:",config['concert'],",日期代碼:",config['ticket_day'])
    ###print("priority:",config['priority'])
    print("------------------------------------")
    


# In[ ]:


import threading,time
from IPython.display import clear_output
if __name__ == "__main__":
    run = False  # global variable to control whether send packet or not
    stop = False  # global variable to control quit the program
    isset = True
    config={
        "w_ticket_num":4,
        "auto":False,
        "priority":"up",
        "concert": None,
        "ticket_day":None
    }
    th1 = threading.Thread(target=handle_user_input)
    th2 = threading.Thread(target=handle_process)
    th1.start()
    th2.start()
    th1.join()
    th2.join()
    sys.exit("Bye~~")
    
