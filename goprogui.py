import wx
import wx.lib.filebrowsebutton as filebrowse


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='gopro2gpx-gui', style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        panel = wx.Panel(self)

        self.CreateStatusBar(style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetStatusText("Welcome to wxPython!")

        # 源文件行
        source_file_button = filebrowse.FileBrowseButton(
            panel, 
            labelText="原始文件：",
            buttonText="选择...",
            fileMask="带元数据视频 (*.mp4)|*.mp4|二进制 (*.bin, cli 版加 -b 参数)|*.bin"
            )

        # 输出路径行
        output_path_button = filebrowse.DirBrowseButton(
            panel,
            labelText="输出目录：",
            buttonText="浏览..."
        )

        # 日志等级行
        log_level_label = wx.StaticText(panel, label='日志等级：')
        log_level_slider = wx.Slider(panel, minValue=0, maxValue=3, value=0, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL )

        # 复选框行
        checkbox1 = wx.CheckBox(panel, label='完成后打开文件管理器')
        checkbox2 = wx.CheckBox(panel, label='跳过坏GPS块')

        # 进度条和按钮行
        progress_bar = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        close_button = wx.Button(panel, id=wx.ID_CLOSE)
        start_button = wx.Button(panel, id=wx.ID_OK)

        # 使用sizer布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 源文件行布局
        source_file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        source_file_sizer.Add(source_file_button, 1, wx.ALL | wx.EXPAND , 5)
        main_sizer.Add(source_file_sizer, 0, wx.EXPAND)

        # 输出路径行布局
        output_path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_path_sizer.Add(output_path_button, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(output_path_sizer, 0, wx.EXPAND)

        # 日志等级行布局
        log_level_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_level_sizer.Add(log_level_label, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        log_level_sizer.Add(log_level_slider, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(log_level_sizer, 0, wx.EXPAND)

        # 复选框行布局
        checkbox_sizer = wx.GridSizer(2)
        checkbox_sizer.Add(checkbox1, 0, wx.ALL, 5)
        checkbox_sizer.Add(checkbox2, 0, wx.ALL, 5)
        main_sizer.Add(checkbox_sizer, 0, wx.EXPAND)

        # 进度条和按钮行布局
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(progress_bar, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        button_sizer.Add(close_button, 0, wx.ALL, 5)
        button_sizer.Add(start_button, 0, wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.EXPAND)

        panel.SetSizer(main_sizer)

        # Get the height of the status bar
        status_bar_height = self.GetStatusBar().GetSize().GetHeight()

        # Get the current frame size and increase the height by the status bar's height
        frame_width, frame_height = self.GetSize()
        self.SetSize(frame_width, frame_height + status_bar_height)

        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()