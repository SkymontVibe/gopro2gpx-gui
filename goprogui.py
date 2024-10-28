import wx
import wx.lib.filebrowsebutton as filebrowse
import threading
from gopro2gpx import gopro2gpx
import os
import platform
import subprocess

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
        super().__init__(parent=None, title='gopro2gpx-gui', style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        panel = wx.Panel(self)

        self.CreateStatusBar(style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetStatusText("就绪")

        # 源文件行
        self.source_file_button = filebrowse.FileBrowseButton(
            panel, 
            labelText="原始文件：",
            buttonText="选择...",
            fileMask="带元数据视频 (*.mp4)|*.mp4|二进制 (*.bin, cli 版加 -b 参数)|*.bin",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            )

        # 输出路径行
        self.output_path_button = filebrowse.DirBrowseButton(
            panel,
            labelText="输出目录：",
            buttonText="浏览..."
        )

        # 日志等级行
        log_level_label = wx.StaticText(panel, label='日志等级：')
        self.log_level_slider = wx.Slider(panel, minValue=0, maxValue=3, value=0, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL )

        # 复选框行
        self.checkbox1 = wx.CheckBox(panel, label='完成后打开文件管理器')
        self.checkbox2 = wx.CheckBox(panel, label='跳过坏 GPS 块')

        # 进度条和按钮行
        self.progress_bar = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        self.close_button = wx.Button(panel, id=wx.ID_CLOSE)
        self.close_button.Bind(wx.EVT_BUTTON, self.on_close_button_click)
        self.start_button = wx.Button(panel, id=wx.ID_OK)
        self.start_button.Bind(wx.EVT_BUTTON, self.on_ok_button_click)

        # 使用sizer布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 源文件行布局
        source_file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        source_file_sizer.Add(self.source_file_button, 1, wx.ALL | wx.EXPAND , 5)
        main_sizer.Add(source_file_sizer, 0, wx.EXPAND)

        # 输出路径行布局
        output_path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_path_sizer.Add(self.output_path_button, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(output_path_sizer, 0, wx.EXPAND)

        # 日志等级行布局
        log_level_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_level_sizer.Add(log_level_label, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        log_level_sizer.Add(self.log_level_slider, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(log_level_sizer, 0, wx.EXPAND)

        # 复选框行布局
        checkbox_sizer = wx.GridSizer(2)
        checkbox_sizer.Add(self.checkbox1, 0, wx.ALL, 5)
        checkbox_sizer.Add(self.checkbox2, 0, wx.ALL, 5)
        main_sizer.Add(checkbox_sizer, 0, wx.EXPAND)

        # 进度条和按钮行布局
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
        self.toggle_enable_status(False)
        self.SetStatusText("正在转换：" + self.source_file_button.GetValue())
        # 创建并启动线程执行耗时操作
        args = Args()
        args.files = [self.source_file_button.GetValue()]
        output_file_prefix = os.path.basename(args.files[0])
        args.outputfile = self.output_path_button.GetValue() + "/" + output_file_prefix
        args.binary = True if args.files[0].endswith(".bin") else False
        args.skip = True if self.checkbox2.Value else False
        args.verbose = self.log_level_slider.GetValue()
        
        self.progress_bar.SetValue(0)
        self.progress_bar.Pulse()
        self.long_running_task = threading.Thread(target=self.perform_convertion, args=[args])
        self.long_running_task.start()

    def perform_convertion(self, arglist):
        # 模拟耗时操作
        gopro2gpx.main_core(arglist)

        # 更新状态文本（必须在主线程中执行）
        wx.CallAfter(self.update_status)

    def update_status(self):
        self.SetStatusText("已完成")
        self.toggle_enable_status(True)
        self.progress_bar.SetValue(100)
        if self.checkbox1.Value:
            if platform.system() == "Windows":
                self # TODO
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", self.output_path_button.GetValue()]) 
        
    def toggle_enable_status(self, enabled):
        control_list = [self.output_path_button, self.source_file_button, 
                        self.checkbox1, self.checkbox2, self.log_level_slider,
                        self.close_button, self.start_button]

        if enabled:
            list(map(lambda x: x.Enable(True), control_list))
        else:
            list(map(lambda x: x.Enable(False), control_list))

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()