import wx
import os
from importlib import reload
import webbrowser
import face_img_register
import no_person_detect
import face_recognize_punchcard
import sys
main ="icon/main.png"
file_path = os.getcwd()+r'\data\logcat.csv'
class   Mainui(wx.Frame):
    def __init__(self,superion):
        wx.Frame.__init__(self,parent=superion,title="kaoqin",size=(1000,590))
        self.SetBackgroundColour('white')
        self.Center()

        self.frame = ''
        self.RegisterButton = wx.Button(parent=self, pos=(50, 120), size=(80, 50), label='人脸注册')

        self.PunchcardButton = wx.Button(parent=self, pos=(50, 220), size=(80, 50), label='人脸签到')

        self.LogcatButton = wx.Button(parent=self, pos=(50, 320), size=(80, 50), label='定时轮寻')
    
        self.Bind(wx.EVT_BUTTON,self.OnRegisterButtonClicked,self.RegisterButton)
        self.Bind(wx.EVT_BUTTON,self.OnPunchCardButtonClicked,self.PunchcardButton)
        self.Bind(wx.EVT_BUTTON,self.OnLogcatButtonClicked,self.LogcatButton)


        # 
        self.image_cover = wx.Image(main, wx.BITMAP_TYPE_ANY).Scale(520, 360)
        # 
        self.bmp = wx.StaticBitmap(parent=self, pos=(180,80), bitmap=wx.Bitmap(self.image_cover))

    def OnRegisterButtonClicked(self,event):
        reload(face_img_register)
        #del sys.modules['face_img_register']
        #import face_img_register
        #runpy.run_path("face_img_register.py")
        #frame = face_img_register.RegisterUi(None)
        app.frame = face_img_register.RegisterUi(None)
        app.frame.Show()

    def OnPunchCardButtonClicked(self,event):
        #del sys.modules['face_recognize_punchcard']
        reload(face_recognize_punchcard)
        #import face_recognize_punchcard
        app.frame = face_recognize_punchcard.PunchcardUi(None)
        app.frame.Show()

    def OnLogcatButtonClicked(self,event):
        # if os.path.exists(file_path):
        #     #
        #     os.startfile(file_path)
        # else:
        #     wx.MessageBox(message="you must run for a little while", caption="warning")
        # pass
        reload(no_person_detect)
        app.frame = no_person_detect.DetectUi(None)
        app.frame.Show()





class MainApp(wx.App):
    def OnInit(self):
        self.frame = Mainui(None)
        self.frame.Show()
        return True

app = MainApp()
app.MainLoop()
