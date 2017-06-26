from urllib.request import urlopen
import os, time
import wx, io

output_path = 'verifies'
imgurl = 'http://mp.weixin.qq.com/mp/verifycode?cert=%s'

class MainFrame(wx.Frame):
    def __init__(self):
        self.width = 600
        self.height = 400
        self.grid_span = 20
        self.main_sizer = None
        self.ts = 0
        self.img_data = None
        self.sizers = {}
        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        wx.Frame.__init__(self, None, -1, 'Captcha Verify', size=(self.width, self.height))
        self.panel = wx.Panel(self, -1)
        #布局层
        self.sizers['main'] = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.sizers['main'], 1, wx.ALIGN_CENTER|wx.ALL)
        self.SetClientSize((self.width, self.height))
        self.panel.SetSizerAndFit(self.main_sizer)
        self.main_sizer.SetSizeHints(self.panel)
        self.ShowImage()
        self.text_input = wx.TextCtrl(self.panel,wx.ID_ANY, style=wx.TE_PROCESS_ENTER, size=(120,25))
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self.text_input)
        self.sizers['main'].Add(self.text_input, 0, wx.ALIGN_CENTER|wx.ALL, self.grid_span)

    def ShowImage(self):
        self.ts = time.time()
        self.img_data = urlopen(imgurl % self.ts).read()
        stream = io.BytesIO(self.img_data)
        bmp = wx.Image( stream ).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        self.sizers['main'].Prepend(self.bitmap, 0, wx.ALIGN_CENTER|wx.ALL, self.grid_span)

    def OnEnter(self, event):
        name = self.text_input.GetValue()
        print(self.ts, name)
        self.SaveImage(name)
        self.text_input.SetValue('')
        self.sizers['main'].Remove(0)
        self.bitmap.Destroy()
        self.ShowImage()
        self.sizers['main'].Layout()

    def SaveImage(self, name):
        if not name: return
        if len(name) != 4: return
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with open(os.path.join(output_path, '%s_%s.jpg'%(name, self.ts)), 'wb') as f:
            f.write(self.img_data)
 
if __name__ == '__main__':
    app = wx.App()
    mainFrame = MainFrame()
    app.MainLoop()