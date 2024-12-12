import wx
import wx.lib.filebrowsebutton as filebrowse
import threading
from gopro2gpx import gopro2gpx
import os
import platform
import subprocess
import sys

class Args(object):
    def __init__(self):
        self.binary = False
        self.skip = False
        self.verbose = 0
        self.files = []
        self.outputfile = None
        self.skip_dop = False
        self.dop_limit = 2000

class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='gopro2gpx-gui', 
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        panel = wx.Panel(self)

        self.CreateStatusBar(style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetStatusText("就绪")

        self.source_file_button = filebrowse.FileBrowseButton(
            panel, 
            labelText="原始文件：",
            buttonText="选择...",
            fileMask="带元数据视频 (*.mp4)|*.mp4|二进制 (*.bin, cli 版加 -b 参数)|*.bin",
            )

        self.output_path_button = filebrowse.DirBrowseButton(
            panel,
            labelText="输出目录：",
            buttonText="浏览..."
        )

        log_level_label = wx.StaticText(panel, label='日志等级：')
        self.log_level_slider = wx.Slider(panel, minValue=0, maxValue=3, value=0, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL )

        self.checkbox1 = wx.CheckBox(panel, label='完成后打开文件管理器')
        self.checkbox2 = wx.CheckBox(panel, label='跳过坏 GPS 块')

        self.progress_bar = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        self.close_button = wx.Button(panel, id=wx.ID_CLOSE)
        self.close_button.Bind(wx.EVT_BUTTON, self.on_close_button_click)
        self.start_button = wx.Button(panel, id=wx.ID_OK)
        self.start_button.Bind(wx.EVT_BUTTON, self.on_ok_button_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        source_file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        source_file_sizer.Add(self.source_file_button, 1, wx.ALL | wx.EXPAND , 5)
        main_sizer.Add(source_file_sizer, 0, wx.EXPAND)

        output_path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_path_sizer.Add(self.output_path_button, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(output_path_sizer, 0, wx.EXPAND)

        log_level_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_level_sizer.Add(log_level_label, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        log_level_sizer.Add(self.log_level_slider, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(log_level_sizer, 0, wx.EXPAND)

        checkbox_sizer = wx.GridSizer(2)
        checkbox_sizer.Add(self.checkbox1, 0, wx.ALL, 5)
        checkbox_sizer.Add(self.checkbox2, 0, wx.ALL, 5)
        main_sizer.Add(checkbox_sizer, 0, wx.EXPAND)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.progress_bar, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        button_sizer.Add(self.close_button, 0, wx.ALL, 5)
        button_sizer.Add(self.start_button, 0, wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.EXPAND)

        panel.SetSizer(main_sizer)

        # Get the height of the status bar
        status_bar_height = self.GetStatusBar().GetSize().GetHeight()

        # Get the current frame size and increase the height by the status bar's height
        frame_width, frame_height = self.GetSize()
        self.SetSize(frame_width, frame_height + status_bar_height)

        self.Show()

    def on_close_button_click(self, event):
        self.Close(True)

    def on_ok_button_click(self, event):
        if not self.source_file_button.GetValue():
            wx.MessageBox("原始文件不能为空！", "错误",
                          style=wx.OK | wx.CENTER | wx.ICON_ERROR)
            return
        
        if not self.output_path_button.GetValue():
            wx.MessageBox("输出目录不能为空！", "错误",
                          style=wx.OK | wx.CENTER | wx.ICON_ERROR)
            return
        
        self.toggle_enable_status(False)
        self.SetStatusText("正在转换：" + self.source_file_button.GetValue())
        args = Args()
        args.files = [self.source_file_button.GetValue()]
        _, output_file_prefix = os.path.split(args.files[0])
        args.outputfile = self.output_path_button.GetValue() + os.path.sep + output_file_prefix
        args.binary = True if args.files[0].endswith(".bin") else False
        args.skip = True if self.checkbox2.Value else False
        args.verbose = self.log_level_slider.GetValue()
        
        self.progress_bar.SetValue(0)
        self.progress_bar.Pulse()
        self.long_running_task = threading.Thread(target=self.perform_convertion, args=[args])
        self.long_running_task.start()

    def perform_convertion(self, arglist):
        result_txt = "已完成"
        try:
            gopro2gpx.main_core(arglist)
            if self.checkbox1.Value:
                if platform.system() == "Windows":
                   subprocess.run(["explorer.exe", self.output_path_button.GetValue()])
                elif platform.system() == "Linux":
                   subprocess.run(["xdg-open", self.output_path_button.GetValue()]) 
        except Exception as e:
            result_txt = "失败"
            wx.MessageBox("处理时出错，请检查输入文件！\n\n错误信息：" + str(e), "错误",
                    style=wx.OK | wx.CENTER | wx.ICON_ERROR)

        wx.CallAfter(self.update_status, result_txt)

    def update_status(self, txt):
        self.SetStatusText(txt)
        self.toggle_enable_status(True)
        self.progress_bar.SetValue(100)
        
        
    def toggle_enable_status(self, enabled):
        control_list = [self.output_path_button, self.source_file_button, 
                        self.checkbox1, self.checkbox2, self.log_level_slider,
                        self.close_button, self.start_button]

        if enabled:
            list(map(lambda x: x.Enable(True), control_list))
        else:
            list(map(lambda x: x.Enable(False), control_list))

if __name__ == '__main__':
    if platform.system() == "Windows" and getattr(sys, 'frozen', False):
        print("Running in pyinstaller bundle")
        os.environ["PATH"] = os.environ["PATH"] + ";" + os.path.abspath(os.path.join(os.path.dirname(__file__), 'prebuilt')) + ";"
        print("PATH:  ", os.environ["PATH"])

    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
