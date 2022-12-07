from flask import Flask
from flask_restx import Resource, Api
from werkzeug.serving import WSGIRequestHandler
import time
import os
import win32api
import win32print
from pywinauto.application import Application
import shutil
from glob import glob
import psutil
from pywinauto import application
from flask_cors import CORS
import requests


WSGIRequestHandler.protocol_version = "HTTP/1.1"

app = Flask(__name__)
app.config['RESTFUL_JSON'] = {'ensure_ascii': False}
app.config['JSON_AS_ASCII'] = False
app.secret_key = 'mufiHome'
CORS(app)
api = Api(app)

# url ="C://Users/cndls/OneDrive/Desktop/프로그래밍/MUFI/mufiKiosk/userpicture/" #이미지 저장하는 위치 변경
url = "D:/Kiosk_photo/"
path = "D:/Users/Kiosk_QR/"


@api.route('/send/img/file/<string:imageCount>/<string:orderid>/<string:printCount>/<string:pin>')
class sendImage(Resource):
    def get(self, imageCount, orderid, printCount, pin):
        now = time.localtime()
        print(now)
        f = {}

        while (1):
            if os.path.isfile(url+''+pin+'0.png'):
                break
            time.sleep(0.1)

        # 보내고자하는 파일을 'rb'(바이너리 리드)방식 열고
        for i in range(int(imageCount)):
            files = open(url+pin+str(i)+".png", 'rb')
            f['image'+str(i)] = files

        # request.post방식으로 파일전송.
        #res = requests.post('http://www.muinfilm.shop/kiosk/pictures/upload/'+orderid +'/'+str(now.tm_year)+str(now.tm_mon)+str(now.tm_mday)+'/'+imageCount, files=f)

        all_printers = [printer[2] for printer in win32print.EnumPrinters(2)]

        printer_num = 0
        for n, p in enumerate(all_printers):
            if (p == "Canon SELPHY CP1300"):
                printer_num = n
                break

        printer = win32print.SetDefaultPrinter(all_printers[printer_num])

        printer["pDevMode"].Copies = int(printCount)

        pdf_dir = url+''+pin+"0.png"
        for fp in glob(pdf_dir, recursive=True):
            win32api.ShellExecute(0, "print", fp, None,  ".",  0)

        app = application.Application().connect(process=os.getpid())
        dialog = app.window()

        time.sleep(3)
        # 에러시 time.sleep(8)

        time.sleep(4)
        dialog.Button.click()

        time.sleep(1)

        return "success"


@app.route('/count_image/<string:imagecut>')
def get(imagecut):

    if imagecut == '0':
        return str(len(os.listdir(path + 'image_4')))

    elif imagecut == '1':
        return str(len(os.listdir(path + 'image_6')))

    else:
        print("dsa")
        return 'fali'


re_userid = ''


@app.route('/test/123/<string:userid>')
def conn(userid):
    global re_userid
    re_userid = userid
    print(re_userid)
    return 'Succ'


# 키오스크 번호와 가게 ID도 라우트 처리할 때 들어가게
# 그러면 키오스크도 자신의 번호와 ID에 들어갔을 때 다른 사람이 들어왔는지 확인 가능
@app.route('/msg')
def mess():
    global re_userid

    if re_userid:
        tmp = re_userid
        re_userid = ''
        return tmp

    return 'Fail'


# 찍은 사진을 폴더 별로 모아주는 코드
@app.route('/chmod/<string:pinNum>')
def chmod(pinNum):
    shutil.copytree("D:/Kiosk_photo/", "D:/Kiosk_photo_backup/"+pinNum)
    shutil.rmtree("D:/Kiosk_photo/")
    os.mkdir("D:/Kiosk_photo")
    return 'success'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
