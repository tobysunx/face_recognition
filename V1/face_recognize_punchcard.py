import dlib  # 人脸识别的库dlib
import numpy as np  # 数据处理的库numpy
import cv2  # 图像处理的库OpenCv
import pandas as pd  # 数据处理的库Pandas
import wx
import os
import csv
import datetime
import _thread
import time
from threading import Thread

from PIL import Image
from time import sleep

# face recognition model, the object maps human faces into 128D vectors
facerec = dlib.face_recognition_model_v1("model/dlib_face_recognition_resnet_model_v1.dat")

# Dlib 预测器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('model/shape_predictor_68_face_landmarks.dat')
bcv2 = cv2
loading = 'icon/loading.png'
pun_fail = 'icon/pun_fail.png'
pun_repeat = 'icon/pun_repeat.png'
pun_success = 'icon/pun_success.png'

path_logcat_csv = "data/logcat.csv"
def read_csv_to_recoders():
    recodes = []
    if os.path.exists(path_logcat_csv):
        with open(path_logcat_csv, "r", newline="") as csvfiler:
            reader = csv.reader(csvfiler)
            for row in reader:
                recodes.append(row)
    else:
        with open(path_logcat_csv, "w", newline="") as csvfilew:
            writer = csv.writer(csvfilew)
            header = ["姓名","日期","时间"]
            writer.writerow(header)
    return recodes
    pass

# 计算两个向量间的欧式距离
def return_euclidean_distance(feature_1, feature_2):
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
    print("欧式距离: ", dist)

    if dist > 0.4:
        return "diff"
    else:
        return "same"

# 处理存放所有人脸特征的csv
path_feature_known_csv = "data/feature_all.csv"

# path_features_known_csv= "/media/con/data/code/python/P_dlib_face_reco/data/csvs/features_all.csv"
try:
    csv_rd = pd.read_csv(path_feature_known_csv,header=None, error_bad_lines=False)
    
except:
    print("ok")
# 存储的特征人脸个数
#print(csv_rd.shape)
#（2，129）

# 用来存放所有录入人脸特征的数组
features_known_arr = []


def testtime(event):
        im = Image.open('data/test1.jpg')
        im2 = np.array(im)
        dets = detector(im2, 1)
        print("aa")

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

@async
def timer(self):
    while 1:
        self.second = self.second + 1
        sleep(1)

#print("s0",csv_rd.shape[0],"s1",csv_rd.shape[1])
for i in range(csv_rd.shape[0]):
    features_someone_arr = []
    for j in range(0, len(csv_rd.ix[i, :])):
        features_someone_arr.append(csv_rd.ix[i, :][j])
    #    print(features_someone_arr)
    features_known_arr.append(features_someone_arr)
print("数据库人脸数:", len(features_known_arr))
sampleList = []
stateList  = []
for item in features_known_arr:
    sampleList.append(item[-1])
    stateList.append("未签到")

print(sampleList)
statecard = dict(zip(sampleList, stateList))


    


# 返回一张图像多张人脸的128D特征  只返回一张人脸
def get_128d_features(img_gray):
    dets = detector(img_gray, 1)
    shape = predictor(img_gray, dets[0])
    face_des = facerec.compute_face_descriptor(img_gray, shape)
    return face_des
    # if len(dets) != 0:
    #     face_des = []
    #     for i in range(len(dets)):
    #         shape = predictor(img_gray, dets[i])
    #         face_des.append(facerec.compute_face_descriptor(img_gray, shape))
    # else:
    #     face_des = []
    # return face_des[0]
class   PunchcardUi(wx.Frame):
    def __init__(self,superion):
        self.second = 0
        wx.Frame.__init__(self,parent=superion,title="刷脸签到",size=(800,590))
        self.SetBackgroundColour('white')
        self.Center()
        font = wx.Font(14, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.OpenCapButton =  wx.Button(parent=self,pos=(50,120),size=(90,60),label='开始/重新签到')
       
        self.listtitle = wx.StaticText(parent=self, style=wx.ALIGN_CENTER_VERTICAL, pos=(50, 190), size=(90, 40), label="签到记录")
        self.statecardlist = []
        for item in sampleList:
            self.statecardlist.append(item + ":"+statecard[item])
        self.listBox = wx.ListBox(self, -1, (50, 220), (150, 200),self.statecardlist, wx.LB_SINGLE)

        self.listtitle.SetBackgroundColour('white')
        self.listtitle.SetForegroundColour('blue')
        self.listtitle.SetFont(font)


        self.resultText = wx.StaticText(parent=self,style=wx.ALIGN_CENTER_VERTICAL,pos=(50,400),size=(90,60),label="签到日志")
        
        self.resultText.SetBackgroundColour('white')
        self.resultText.SetForegroundColour('blue')
        
        self.resultText.SetFont(font)
        self.pun_day_num = 0

        self.contents = wx.TextCtrl(self, pos=(80, 420), size=(600, 100), style=wx.TE_MULTILINE | wx.HSCROLL)



      




        # 封面图片
        self.image_loading = wx.Image(loading, wx.BITMAP_TYPE_ANY).Scale(600, 480)

        self.image_fail = wx.Image(pun_fail, wx.BITMAP_TYPE_ANY).Scale(600, 480)
        self.image_repeat = wx.Image(pun_repeat, wx.BITMAP_TYPE_ANY).Scale(600, 480)
        self.image_success = wx.Image(pun_success, wx.BITMAP_TYPE_ANY).Scale(600, 480)

        # 显示图片
        self.bmp = wx.StaticBitmap(parent=self, pos=(250,50), bitmap=wx.Bitmap(self.image_loading))

        self.Bind(wx.EVT_BUTTON,self.OnOpenCapButtonClicked,self.OpenCapButton)


    def OnOpenCapButtonClicked(self,event):

        """使用多线程，子线程运行后台的程序，主线程更新前台的UI，这样不会互相影响"""
        # 创建子线程，按钮调用这个方法，
        _thread.start_new_thread(self._open_cap, (event,))

    def updateListBox(self):
        self.listBox = wx.ListBox(self, -1, (50, 220), (150, 200), self.statecardlist, wx.LB_SINGLE)

    def detectorface(self,event,im_rd):
        dets = detector(im_rd, 1)

        # 待会要写的字体
        font = cv2.FONT_HERSHEY_SIMPLEX

        # 存储人脸名字和位置的两个 list
        # list 1 (dets): store the name of faces                Jack    unknown unknown Mary
        # list 2 (pos_namelist): store the positions of faces   12,1    1,21    1,13    31,1

        # 人脸的名字
        name = ''
        pos = ''
        # pos_namelist = []
        # name_namelist = []

        if len(dets) != 0:
            # 检测到人脸

            # 获取当前捕获到的图像的所有人脸的特征，存储到 features_bk_arr
            features_cap = ''
            shape = predictor(im_rd, dets[0])
            features_cap = facerec.compute_face_descriptor(
                im_rd, shape)

            # 遍历捕获到的图像中所有的人脸
            # 让人名跟随在矩形框的下方
            # 确定人名的位置坐标
            # 先默认所有人不认识，是 unknown
            name = "unrecognized face"

            # 每个捕获人脸的名字坐标
            pos = tuple(
                [(int)((dets[0].left() + dets[0].right()) / 2) - 50, dets[0].bottom() + 20])

            # 对于某张人脸，遍历所有存储的人脸特征

            # for i in range(len(features_known_arr)):
            #     # 将某张人脸与存储的所有人脸数据进行比对
             
            #     compare = return_euclidean_distance(
            #         features_cap, features_known_arr[i][0:-1])
            #     if compare == "same":  # 找到了相似脸
            #         name = features_known_arr[i][-1]
            #         print(name)
            #         if(statecard[name] != "已签到"):
            #             sleep(0.1)
            #             wx.CallAfter(self.contents.AppendText, name + "--签到成功--" +
            #                          time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
            #             self.statecardlist = []
            #             statecard[name] = "已签到"
            #             for item in sampleList:
            #                 self.statecardlist.append(
            #                     item + ":"+statecard[item])
            #                 wx.CallAfter(self.updateListBox)

            cv2.rectangle(self.imtoshow, tuple([dets[0].left()*4, dets[0].top()*4]), tuple([dets[0].right()*4, dets[0].bottom()*4]), (255, 0, 0), 2)
            height, width = self.imtoshow.shape[:2]
            image1 = cv2.cvtColor(self.imtoshow, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(width, height, image1)
            # 显示图片在panel上
            sleep(0.1)
            wx.CallAfter(self.bmp.SetBitmap, pic)
            
   
        

    def loadimg(self,event,im_rd,imtoshow):
        height, width = imtoshow.shape[:2]
        image1 = cv2.cvtColor(imtoshow, cv2.COLOR_BGR2RGB)
        pic = wx.Bitmap.FromBuffer(width, height, image1)
        # 显示图片在panel上
        wx.CallAfter(self.bmp.SetBitmap, pic)
        _thread.exit()


    def _open_cap(self,event):
        # 创建 cv2 摄像头对象
        self.cap = cv2.VideoCapture(0)
        # cap.set(propId, value)
        # 设置视频参数，propId设置的视频参数，value设置的参数值
        
        timer(self)
        #cap是否初始化成功
        isFirst = True
        while self.cap.isOpened():
        
            # cap.read()
            # 返回两个值：
            #    一个布尔值true/false，用来判断读取视频是否成功/是否到视频末尾
            #    图像对象，图像的三维矩阵
            flag, im_rd = self.cap.read()
            self.imtoshow = cv2.resize(im_rd, (480,320), interpolation=cv2.INTER_CUBIC)
            im_rd = cv2.resize(im_rd, (120, 80),interpolation=cv2.INTER_CUBIC)
            _thread.start_new_thread(self.loadimg, (event, im_rd, self.imtoshow))
            # 每帧数据延时1ms，延时为0读取的是静态帧
            kk = cv2.waitKey(1)

            # 人脸数 dets
            

            if self.second % 2 ==0 :
                if isFirst == True:
                    _thread.start_new_thread(self.detectorface, (event,im_rd))
                    # _thread.start_new_thread(testtime,(event,))
                    isFirst = False
            else:
                isFirst = True
                
                  
                        

                    # 写人脸名字
                    # cv2.putText(im_rd, name, pos, font, 0.8,
                    #             (255, 0, 255), 1, cv2.LINE_AA)

                # cv2.putText(im_rd, "Faces: " + str(len(dets)), (50, 80),
                #             font, 1, (255, 0, 0), 1, cv2.LINE_AA)
            
            
            
            # self.bmp.SetBitmap(pic)
#
# app = wx.App()
# frame = PunchcardUi(None)
# frame.Show()
# app.MainLoop()



