#coding=utf-8
import wx
import wx.grid
import sqlite3
from time import localtime,strftime
import datetime
import os
import random
from skimage import io as iio
import io
import zlib
import dlib  # 人脸识别的库dlib
import numpy as np  # 数p据处理的库numpy
import cv2  # 图像处理的库OpenCv
import _thread
from time import sleep
from threading import Thread

ID_NEW_REGISTER = 160
ID_FINISH_REGISTER = 161

ID_START_PUNCHCARD = 190
ID_END_PUNCARD = 191

ID_OPEN_LOGCAT = 283
ID_CLOSE_LOGCAT = 284

ID_WORKER_UNAVIABLE = -1

PICNUM = 5


def return_euclidean_distance(feature_1, feature_2):
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))

    if dist > 0.4:
        return "diff"
    else:
        return "same"


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


@async
def timer(self):
    while 1:
        if self.turnoffcap:
            break
        self.second = (self.second+1)
          
        sleep(random.uniform(0.7,1.2))
  


class WAS(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent=None,title="员工考勤系统",size=(920,560))
        self.initData(0)
        self.initFaceDetectorProcess()
        # self.initMenu()
        self.initInfoText()
        # self.initGallery()
        self.initProcessBar()
        # self.clearDatabase()
        self.initDatabase()
        
        
       

    def initData(self,type):
        if type == 0: #full init
            self.name = ""
            self.id =ID_WORKER_UNAVIABLE
        if type == 1: # regist duplicate init save the name and id
            pass
        self.face_feature = ""
        self.pic_num = 0
        self.flag_registed = False
        self.puncard_time = "09:00:00"
        self.loadDataBase(1)
        self.imgsavelist = []
        self.second = 0
        self.turnoffcap = False
        self.finishinitfd = 0
        timer(self)

    def callinitfd(self):
        _thread.start_new_thread(self.initFaceDetector, ('temp',))
    
    def fdpSetValue(self,num):
        self.fdp.SetValue(num)

    def _initInfoText(self):
        self.infoText = wx.TextCtrl(parent=self, size=(320, 500),
                                    style=(wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY))

    def initFaceDetector(self,event):
        # face recognition model, the object maps human faces into 128D vectors
        self.facerec = dlib.face_recognition_model_v1("model/dlib_face_recognition_resnet_model_v1.dat")
        wx.CallAfter(self.fdpSetValue,30)
        # Dlib 预测器
        self.detector = dlib.get_frontal_face_detector()
        wx.CallAfter(self.fdpSetValue, 60)
        self.predictor = dlib.shape_predictor('model/shape_predictor_68_face_landmarks.dat')
        wx.CallAfter(self.fdpSetValue, 100)
        self.fdp.Hide()
        self.detectLabel.Hide()
        wx.CallAfter(self.initMenu)
        # self.initGallery()
        wx.CallAfter(self._initInfoText)

        


    def clearDatabase(self):
        conn = sqlite3.connect("inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象
        cur.execute('''drop table worker_info''')
        cur.execute('''drop table logcat''')
        cur.close()
        conn.commit()
        conn.close()

    def initMenu(self):

        menuBar = wx.MenuBar()  #生成菜单栏
        menu_Font = wx.Font()#Font(faceName="consolas",pointsize=20)
        menu_Font.SetPointSize(14)
        menu_Font.SetWeight(wx.BOLD)


        registerMenu = wx.Menu() #生成菜单
        self.new_register = wx.MenuItem(registerMenu,ID_NEW_REGISTER,"新建录入")
        self.new_register.SetBitmap(wx.Bitmap("drawable/new_register.png"))
        self.new_register.SetTextColour("SLATE BLUE")
        self.new_register.SetFont(menu_Font)
        registerMenu.Append(self.new_register)

        self.finish_register = wx.MenuItem(registerMenu,ID_FINISH_REGISTER,"完成录入")
        self.finish_register.SetBitmap(wx.Bitmap("drawable/finish_register.png"))
        self.finish_register.SetTextColour("SLATE BLUE")
        self.finish_register.SetFont(menu_Font)
       
        registerMenu.Append(self.finish_register)


        puncardMenu = wx.Menu()
        self.start_punchcard = wx.MenuItem(puncardMenu,ID_START_PUNCHCARD,"开始签到")
        self.start_punchcard.SetBitmap(wx.Bitmap("drawable/start_punchcard.png"))
        self.start_punchcard.SetTextColour("SLATE BLUE")
        self.start_punchcard.SetFont(menu_Font)
        puncardMenu.Append(self.start_punchcard)

        self.end_puncard = wx.MenuItem(puncardMenu,ID_END_PUNCARD,"结束签到")
        self.end_puncard.SetBitmap(wx.Bitmap("drawable/end_puncard.png"))
        self.end_puncard.SetTextColour("SLATE BLUE")
        self.end_puncard.SetFont(menu_Font)
        puncardMenu.Append(self.end_puncard)

        logcatMenu = wx.Menu()
        self.open_logcat = wx.MenuItem(logcatMenu,ID_OPEN_LOGCAT,"打开日志")
        self.open_logcat.SetBitmap(wx.Bitmap("drawable/open_logcat.png"))
        self.open_logcat.SetFont(menu_Font)
        self.open_logcat.SetTextColour("SLATE BLUE")
        logcatMenu.Append(self.open_logcat)

        self.close_logcat = wx.MenuItem(logcatMenu, ID_CLOSE_LOGCAT, "关闭日志")
        self.close_logcat.SetBitmap(wx.Bitmap("drawable/close_logcat.png"))
        self.close_logcat.SetFont(menu_Font)
        self.close_logcat.SetTextColour("SLATE BLUE")
        logcatMenu.Append(self.close_logcat)

        menuBar.Append(registerMenu,"&人脸录入")
        menuBar.Append(puncardMenu,"&刷脸签到")
        menuBar.Append(logcatMenu,"&考勤日志")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,self.OnNewRegisterClicked,id=ID_NEW_REGISTER)
        self.Bind(wx.EVT_MENU,self.OnEndPunchCardClicked,id=ID_FINISH_REGISTER)
        self.Bind(wx.EVT_MENU,self.OnStartPunchCardClicked,id=ID_START_PUNCHCARD)
        self.Bind(wx.EVT_MENU,self.OnEndPunchCardClicked,id=ID_END_PUNCARD)
        self.Bind(wx.EVT_MENU,self.OnOpenLogcatClicked,id=ID_OPEN_LOGCAT)
        self.Bind(wx.EVT_MENU,self.OnCloseLogcatClicked,id=ID_CLOSE_LOGCAT)

    def initProcessBar(self):
        self.processCount = 0
        self.getfaceProcess = wx.Gauge(self, -1, 100, (410, 400),(480, 25))
        self.getfaceProcess.SetBezelFace(3)
        self.getfaceProcess.SetShadowWidth(3)
        self.getfaceProcess.Hide()
        # self.Bind(wx.EVT_IDLE, self.OnIdle)
    def initFaceDetectorProcess(self):
        self.detectLabel = wx.StaticText(parent=self, style=wx.ALIGN_CENTER_VERTICAL, pos=(350, 350), size=(200, 60), label="正在加载dlib,请稍等")
        self.fdp = wx.Gauge(self, -1, 100, (200, 400), (480, 25))
        self.fdp.SetBezelFace(3)
        self.fdp.SetShadowWidth(3)
        self.fdpcount = 0
        wx.CallAfter(self.callinitfd)


    def OnIdle(self, event):
        sleep(0.1)
        self.processCount = self.processCount + 1
        if self.processCount >= 80:
            self.processCount = 0
        self.getfaceProcess.SetValue(self.processCount)
        
    


    def OnOpenLogcatClicked(self,event):
        self.hideDetectLabel('temp')
        try:
            self.grid.Hide()
        except:
            pass
        self.loadDataBase(2)
        self.grid = wx.grid.Grid(self,pos=(320,0),size=(600,500))
        self.grid.CreateGrid(100, 4)
        for i in range(100):
            for j in range(4):
                self.grid.SetCellAlignment(i,j,wx.ALIGN_CENTER,wx.ALIGN_CENTER)
        self.grid.SetColLabelValue(0, "工号") #第一列标签
        self.grid.SetColLabelValue(1, "姓名")
        self.grid.SetColLabelValue(2, "打卡时间")
        self.grid.SetColLabelValue(3, "是否迟到")

        self.grid.SetColSize(0,100)
        self.grid.SetColSize(1,100)
        self.grid.SetColSize(2,150)
        self.grid.SetColSize(3,150)


        self.grid.SetCellTextColour("NAVY")
        for i,id in enumerate(self.logcat_id):
            self.grid.SetCellValue(i,0,str(id))
            self.grid.SetCellValue(i,1,self.logcat_name[i])
            self.grid.SetCellValue(i,2,self.logcat_datetime[i])
            self.grid.SetCellValue(i, 3, self.logcat_late[i])

        pass

    def OnCloseLogcatClicked(self,event):
        try:
            self.grid.Hide()
        except:
            pass
        

    def appendMsg(self,id,name,message):
        self.infoText.AppendText("工号:"+str(id)+"-姓名:"+name+"-"+message+"\r\n")
        if message == "成功录入":
            wx.MessageBox(message="成功录入", caption="成功")
        if message == "人脸已经录入":
            wx.MessageBox(message="人脸已经录入", caption="警告")
    def register_cap(self,event):
        # 创建 cv2 摄像头对象
        print("人脸注册启动")
        firstdetect = True
        self.cap = cv2.VideoCapture(0)
   
        detectflag = True
        while self.cap.isOpened():
            if self.turnoffcap:
               
                _thread.exit()
            # try:
            flag,im_rd = self.cap.read()
            imgtoshow = cv2.resize(
                im_rd, (480, 320), interpolation=cv2.INTER_CUBIC)
            
            # except:
                # print("didididid")

       
            if self.second % 4 == 2 or self.second % 4 == 0:
                if detectflag == True:
               
                    detectflag = False
                    flag, im_rd = self.cap.read()
                    imgtoshow = cv2.resize(
                        im_rd, (480, 320), interpolation=cv2.INTER_CUBIC)
                    imgtodetect = cv2.resize(
                        im_rd, (120, 80), interpolation=cv2.INTER_CUBIC)


                  
                   
                    # 人脸数 dets
                    dets = self.detector(imgtodetect, 1)

                    # 检测到人脸
                    if len(dets) != 0:
                        biggest_face = dets[0]
                        #取占比最大的脸
                        maxArea = 0
                        for det in dets:
                            w = det.right() - det.left()
                            h = det.top()-det.bottom()
                            if w*h > maxArea:
                                biggest_face = det
                                maxArea = w*h
                                # 绘制矩形框

                        cv2.rectangle(imgtoshow, tuple([biggest_face.left()*4, biggest_face.top()*4]),
                                            tuple([biggest_face.right()*4, biggest_face.bottom()*4]),
                                            (255, 0, 0), 2)
                        img_height, img_width = imgtoshow.shape[:2]
                        image1 = cv2.cvtColor(imgtoshow, cv2.COLOR_BGR2RGB)
                        pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
                        # 显示图片在panel上
                        # self.bmp.SetBitmap(pic)
                        wx.CallAfter(self.bmp.SetBitmap, pic)

                        self.pic_num += 1

                        self.imgsavelist.append(imgtodetect)

                        wx.CallAfter(self.updateDetectProcess,(self.pic_num / PICNUM) * 100,0)
                        

                        

                        

                        # 获取当前捕获到的图像的所有人脸的特征，存储到 features_cap_arr
                        if firstdetect==True:
                            firstdetect = False
                            shape = self.predictor(imgtodetect, biggest_face)
                            features_cap = self.facerec.compute_face_descriptor(
                                imgtodetect, shape)

                            # 对于某张人脸，遍历所有存储的人脸特征
                            for i,knew_face_feature in enumerate(self.knew_face_feature):
                                # 将某张人脸与存储的所有人脸数据进行比对
                                compare = return_euclidean_distance(features_cap, knew_face_feature)
                                if compare == "same":  # 找到了相似脸
                                    # self.infoText.AppendText(self.getDateAndTime()+"工号:"+str(self.knew_id[i])
                                    #                         +" 姓名:"+self.knew_name[i]+" 的人脸数据已存在\r\n")
                                    # wx.CallAfter(self.appendMsg,
                                    #               self.id, self.name, "人脸已经录入")
                                    self.flag_registed = True
                                    wx.CallAfter(self.duplicateRegist,self.knew_id[i])
                                    # self.duplicateRegist = wx.MessageDialog(None, u"消息对话框测试", u"标题信息", wx.YES_NO | wx.ICON_QUESTION);
                                    self.OnFinishRegisterClicked('temp')

                                    _thread.exit()

                        


                        if self.pic_num == PICNUM:
                            self.OnFinishRegister()
                            _thread.exit()
            else:
                detectflag = True  

            img_height, img_width = imgtoshow.shape[:2]
            image1 = cv2.cvtColor(imgtoshow, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
            wx.CallAfter(self.bmp.SetBitmap, pic)

            


    def OnNewRegisterClicked(self,event):
        try:
            self.OnEndPunchCardClicked("temp")
        except:
            pass
        
        try:
            self.getfaceProcess.SetValue(0)
            self.getfaceProcess.Hide()
        except:
            pass
        
        self.initData(0)
        self.loadDataBase(1)
        self.initGallery()
        self.id = 0
        self.name == ''
        while self.id == 0:
            self.id = wx.GetNumberFromUser(message="请输入工号",
                                            prompt="工号", caption="温馨提示",
                                            value=0,
                                            parent=self.bmp,max=100000000)
        
            if self.id > 0:
                if len(self.knew_id) > 0:
                    for knew_id in self.knew_id:
                        if knew_id == self.id:
                            self.id = 0
                            wx.MessageBox(message="工号已存在，请重新输入", caption="警告")
                        else:
                            while self.name == '':
                                self.name = wx.GetTextFromUser(message="请输入姓名",
                                                            caption="温馨提示",
                                                        default_value="", parent=self.bmp)
                            _thread.start_new_thread(self.register_cap, (event,))
                            wx.CallAfter(self.showDetectProcess)
                else:
                    while self.name == '':
                        self.name = wx.GetTextFromUser(message="请输入姓名",
                                                            caption="温馨提示",
                                                        default_value="", parent=self.bmp)
                        _thread.start_new_thread(self.register_cap, (event,))
                        wx.CallAfter(self.showDetectProcess)


        else:
            if self.id == 0:
                wx.MessageBox(message="工号输入非法，请重新输入", caption="警告")



    def OnFinishRegister(self):
        self.turnoffcap = True
        # cv2.destroyAllWindows()
        self.cap.release()
        wx.CallAfter(self.updateDetectProcess,0,1);


        if self.pic_num>0:
            feature_list = []
            feature_average = []
            for i in range(len(self.imgsavelist)):
                img_gray = cv2.cvtColor(self.imgsavelist[i], cv2.COLOR_BGR2RGB)
                dets = self.detector(img_gray, 1)
                if len(dets) != 0:
                    shape = self.predictor(img_gray, dets[0])
                    face_descriptor = self.facerec.compute_face_descriptor(img_gray, shape)
                    feature_list.append(face_descriptor)
                else:
                    face_descriptor = 0
                wx.CallAfter(self.updateDetectProcess, ((i+1) / PICNUM) * 100, 1)
            if len(feature_list) > 0:
                for j in range(128):
                    #防止越界
                    feature_average.append(0)
                    for i in range(len(feature_list)):
                        feature_average[j] += feature_list[i][j]
                    feature_average[j] = (feature_average[j]) / len(feature_list)
                self.insertARow([self.id,self.name,feature_average],1)
                wx.CallAfter(self.appendMsg,self.id,self.name,"成功录入")

            pass

        else:
            pass
        self.initData(0)

    def showPunchcard(self,temp):
        try:
            self.infoText.Hide()
        except:
            pass
        self._initInfoText()
        for i in range(len(self.logcat_id)):
            self.infoText.AppendText("工号:"+str(self.logcat_id[i])+"-姓名-"+self.logcat_name[i]+"今日已签到\r\n")
            

    def duplicateRegist(self,work_id):
        dlg = wx.MessageDialog(None, u"当前人脸已经录入于工号"+str(work_id)+"，是否重新录入", u"警告",
                            wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            print(work_id)
            self.deleteARow(work_id)
            self.loadDataBase(1)
            # self.OnNewRegisterClicked("temp");
            self.initData(1)
            _thread.start_new_thread(self.register_cap, ("temp",))
            wx.CallAfter(self.showDetectProcess)

    def OnFinishRegisterClicked(self,event):
        wx.CallAfter(self.hideDetectLabel,'hide detectlabel')
        self.turnoffcap = True
        # cv2.destroyAllWindows()
        # self.cap.release()
        # self.OnEndPunchCardClicked('temp')
        # self.OnFinishRegister()
        # pass

    def showDetectProcess(self):
        try:
            self.getfaceProcess.Show()
        except:
            pass

    def updateDetectProcess(self, p, type):
        if type == 0:
            self.getfaceProcess.SetValue(p)    
            try:
                self.detectLabel.Hide()
            except:
                pass
            self.detectLabel = wx.StaticText(parent=self, style=wx.ALIGN_CENTER_VERTICAL, pos=(
                410, 350), size=(200, 60), label="正在截取头像："+str(self.pic_num)+"/"+str(PICNUM))
            if self.pic_num == PICNUM:
                sleep(0.1)
                try:
                    self.detectLabel.Hide()
                except:
                    pass
                
                self.detectLabel = wx.StaticText(parent=self, style=wx.ALIGN_CENTER_VERTICAL, pos=(
                    410, 350), size=(200, 60), label="正在读取头像信息")
        else:
            self.getfaceProcess.SetValue(p)
            if p == 100:
                try:
                    self.detectLabel.Hide()
                    self.detectLabel = wx.StaticText(parent=self, style=wx.ALIGN_CENTER_VERTICAL, pos=(410, 350), size=(200, 60), label="录入成功")
                    pass
                except:
                    pass

    
    def hideDetectLabel(self,temp):
        try:
            self.detectLabel.Hide()
            self.getfaceProcess.Hide()
        except:
            pass
      

    def punchcard_cap(self,event):
        self.hideDetectLabel('temp')
        print("人脸签到启动")
        wx.CallAfter(self.showPunchcard,'show the people had puncharded')
        # 创建 cv2 摄像头对象
        firstdetect = True
        self.cap = cv2.VideoCapture(0)
        detectflag = True
        while self.cap.isOpened():
            if  self.turnoffcap:
                _thread.exit()

        
            flag, im_rd = self.cap.read()
            try:
                imgtoshow = cv2.resize(im_rd, (480, 320), interpolation=cv2.INTER_CUBIC)
            except:
                pass
          
            if self.second % 4 == 2 or self.second % 4 == 0:
                if detectflag == True:
                    detectflag = False
                    flag, im_rd = self.cap.read()
                    imgtoshow = cv2.resize(
                        im_rd, (480, 320), interpolation=cv2.INTER_CUBIC)
                    imgtodetect = cv2.resize(
                        im_rd, (120, 80), interpolation=cv2.INTER_CUBIC)

                    # 人脸数 dets
                    dets = self.detector(imgtodetect, 1)

                    # 检测到人脸
                    if len(dets) != 0:
                        biggest_face = dets[0]
                        #取占比最大的脸
                        maxArea = 0
                        for det in dets:
                            w = det.right() - det.left()
                            h = det.top()-det.bottom()
                            if w*h > maxArea:
                                biggest_face = det
                                maxArea = w*h
                                # 绘制矩形框

                        cv2.rectangle(imgtoshow, tuple([biggest_face.left()*4, biggest_face.top()*4]),
                                      tuple([biggest_face.right()*4,
                                             biggest_face.bottom()*4]),
                                      (255, 0, 0), 2)
                        img_height, img_width = imgtoshow.shape[:2]
                        image1 = cv2.cvtColor(imgtoshow, cv2.COLOR_BGR2RGB)
                        pic = wx.Bitmap.FromBuffer(
                            img_width, img_height, image1)
                        # 显示图片在panel上
                        # self.bmp.SetBitmap(pic)
                        wx.CallAfter(self.bmp.SetBitmap, pic)
                        
                        

                        # 获取当前捕获到的图像的所有人脸的特征，存储到 features_cap_arr
                        if True:
                            firstdetect = False
                            shape = self.predictor(imgtodetect, biggest_face)
                            features_cap = self.facerec.compute_face_descriptor(
                                imgtodetect, shape)

                            # 对于某张人脸，遍历所有存储的人脸特征
                            for i, knew_face_feature in enumerate(self.knew_face_feature):
                                # 将某张人脸与存储的所有人脸数据进行比对
                                compare = return_euclidean_distance(
                                    features_cap, knew_face_feature)
                                if compare == "same":  # 找到了相似脸
                                    flag = 0
                                    nowdt = self.getDateAndTime()
                                    for j, logcat_id in enumerate(self.logcat_id):
                                        if logcat_id == self.knew_id[i]:
                                        # wx.CallAfter(self.appendMsg, str(
                                        #     self.knew_id[i]), self.knew_name[i], "重复签到")
                                            flag = 1
                                            break
                                    if flag == 1:
                                        break
                                    wx.CallAfter(self.appendMsg, str(
                                        self.knew_id[i]), self.knew_name[i], "签到成功")
                                    self.insertARow(
                                        [self.knew_id[i], self.knew_name[i], nowdt, "否"], 2)

                                    self.loadDataBase(2)
                                    break

              
            else:
                detectflag = True

            img_height, img_width = imgtoshow.shape[:2]
            image1 = cv2.cvtColor(imgtoshow, cv2.COLOR_BGR2RGB)
            pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
            wx.CallAfter(self.bmp.SetBitmap, pic)
        

                

    def OnStartPunchCardClicked(self,event):
        # cur_hour = datetime.datetime.now().hour
        # print(cur_hour)
        # if cur_hour>=8 or cur_hour<6:
        #     wx.MessageBox(message='''您错过了今天的签到时间，请明天再来\n
        #     每天的签到时间是:6:00~7:59''', caption="警告")
        #     return
        self.initData(0)
        self.loadDataBase(2)
        try:
            self.getfaceProcess.Hide()
        except:
            pass
        self.initGallery()
        _thread.start_new_thread(self.punchcard_cap,(event,))
        pass

    def OnEndPunchCardClicked(self,event):
        self.turnoffcap = True
        # cv2.destroyAllWindows()
        try:
            # self.cap.release()
            self.getfaceProcess.Hide()
            
        except:
            pass
        
        pass

    def initInfoText(self):
        #少了这两句infoText背景颜色设置失败，莫名奇怪
        resultText = wx.StaticText(parent=self, pos = (30,30),size=(90, 60))
        

        self.info = "\r\n"+self.getDateAndTime()+"程序初始化成功\r\n"
        #第二个参数水平混动条
        self.infoText = wx.TextCtrl(parent=self,size=(0,0),
                   style=(wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY))
        #前景色，也就是字体颜色
        self.infoText.SetForegroundColour("black")
        self.infoText.SetLabel(self.info)

        font = wx.Font()
        font.SetPointSize(12)

        self.infoText.SetFont(font)
        
        pass


    def initGallery(self):
        self.pic_index = wx.Image("drawable/index.png", wx.BITMAP_TYPE_ANY).Scale(600, 500)
        self.bmp = wx.StaticBitmap(parent=self, pos=(400,0), bitmap=wx.Bitmap(self.pic_index))
        
        pass

    # def getDateAndTime(self):
    #     dateandtime =   ("%Y-%m-%d %H:%M:%S",localtime())
    #     return "["+dateandtime+"]"

    def getDateAndTime(self):
        dateandtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
        return "["+dateandtime+"]"

    #数据库部分
    #初始化数据库
    def initDatabase(self):
        conn = sqlite3.connect("inspurer.db")  #建立数据库连接
        cur = conn.cursor()             #得到游标对象
        cur.execute('''create table if not exists worker_info
        (name text not null,
        id int not null primary key,
        face_feature array not null)''')
        cur.execute('''create table if not exists logcat
         (datetime text not null,
         id int not null,
         name text not null,
         late text not null)''')
        cur.close()
        conn.commit()
        conn.close()

    def adapt_array(self,arr):
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)

        dataa = out.read()
        # 压缩数据流
        return sqlite3.Binary(zlib.compress(dataa, zlib.Z_BEST_COMPRESSION))

    def convert_array(self,text):
        out = io.BytesIO(text)
        out.seek(0)

        dataa = out.read()
        # 解压缩数据流
        out = io.BytesIO(zlib.decompress(dataa))
        return np.load(out)

    def insertARow(self,Row,type):
        conn = sqlite3.connect("inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象
        if type == 1:
            cur.execute("insert into worker_info (id,name,face_feature) values(?,?,?)",
                    (Row[0],Row[1],self.adapt_array(Row[2])))
            print("写人脸数据成功")
        if type == 2:
            cur.execute("insert into logcat (id,name,datetime,late) values(?,?,?,?)",
                        (Row[0],Row[1],Row[2],Row[3]))
            print("写日志成功")
            pass
        cur.close()
        conn.commit()
        conn.close()
        pass

    def deleteARow(self,work_id):
        conn = sqlite3.connect("inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象
        cur.execute("delete from worker_info where id = ?", (work_id,))
        cur.close()
        conn.commit()
        conn.close()
        print("人脸已删除")


    def isToday(self,dt):
        detester = dt
        date = datetime.datetime.strptime(detester, '[%Y-%m-%d %H:%M:%S]')
        year = date.year
        month = date.month
        day = date.day
        if year == localtime().tm_year and month == localtime().tm_mon and day == localtime().tm_mday:
            return True
        else:
            return False



    def loadDataBase(self,type):

        conn = sqlite3.connect("inspurer.db")  # 建立数据库连接
        cur = conn.cursor()  # 得到游标对象

        if type == 1:
            self.knew_id = []
            self.knew_name = []
            self.knew_face_feature = []
            cur.execute('select id,name,face_feature from worker_info')
            origin = cur.fetchall()
            for row in origin:
               
                self.knew_id.append(row[0])
            
                self.knew_name.append(row[1])
           
                self.knew_face_feature.append(self.convert_array(row[2]))
        if type == 2:
            self.logcat_id = []
            self.logcat_name = []
            self.logcat_datetime = []
            self.logcat_late = []
            cur.execute('select id,name,datetime,late from logcat')
            origin = cur.fetchall()
            
            for row in origin:
                if self.isToday(row[2]):
                  
                    self.logcat_id.append(row[0])
             
                    self.logcat_name.append(row[1])
                  
                    self.logcat_datetime.append(row[2])
               
                    self.logcat_late.append(row[3])

app = wx.App()
frame = WAS()
frame.Show()
app.MainLoop()
