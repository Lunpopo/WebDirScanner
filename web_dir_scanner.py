import sys
import os
import random
import requests
import time
from threading import Thread
import queue

from lib.settings import DICT_PATH, IMAGES_PATH, DATA_PATH, HEADER, DICT_LIST_TEXT

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTextEdit, QDesktopWidget,
    QAction, QFileDialog, QApplication, QSlider,
    QLabel, QLineEdit, QCheckBox, QVBoxLayout,
    QHBoxLayout, QGroupBox, QPushButton, QMessageBox
)

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QCoreApplication, QThread, pyqtSignal
from urllib.parse import urlparse
from termcolor import colored


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.target_url_field = QLineEdit()
        self.text_edit = QTextEdit()
        # 控制 thread number 的滑块
        self.thread_slider = QSlider(Qt.Horizontal)
        # 显示 thread number
        self.thread_number = QLineEdit()
        # 显示 file with list of dirs/files 路径
        self.file_path_field = QLineEdit()
        # 列出 List info 弹出框按钮
        self.list_info_button = QPushButton("List info")
        # CheckBox
        self.brute_force_dirs = QCheckBox('Brute Force Dirs')
        self.brute_force_files = QCheckBox('Brute Force Files')
        self.dir_start_field = QLineEdit()
        self.file_extension_field = QLineEdit()
        # display console text area
        self.console_field = QTextEdit()
        # start scan button
        self.start_button = QPushButton('Start')
        self.pause_button = QPushButton('Pause')
        self.pause_button.setEnabled(False)
        # 使用线程处理耗时任务, 避免主窗口阻塞, 这里用于初始化
        self.handle_scan = ""

    def init_ui(self):
        widget = QWidget()
        # 把 QMainWindow 的布局设置为 QWidget, 然后布局 QWidget 就可以了
        self.setCentralWidget(widget)
        self.statusBar()

        # 这里添加 menu 块
        # File menu options
        file_option = QAction(QIcon(os.path.join(IMAGES_PATH, 'Icon.png')), 'Open', self)
        file_option.setShortcut('Ctrl+O')
        file_option.setStatusTip('Open new File')
        file_option.triggered.connect(self.open_file)

        # Options menu
        advance_option = QAction(QIcon(os.path.join(IMAGES_PATH, '设置.png')), 'Advanced Options', self)
        advance_option.setShortcut('Ctrl+G')
        advance_option.setStatusTip('Open Advanced Options Dialogs')
        advance_option.triggered.connect(self.open_advance_frame)

        # About menu options
        license_option = QAction(QIcon(os.path.join(IMAGES_PATH, '认证.png')), 'License', self)
        # license_option.setShortcut('Ctrl+V')
        license_option.setStatusTip('Open License Dialogs')
        license_option.triggered.connect(self.open_license_frame)
        # version menu options
        version_option = QAction(QIcon(os.path.join(IMAGES_PATH, 'blank.png')), 'Version', self)
        # version_option.setShortcut('Ctrl+V')
        version_option.setStatusTip('Open Version Dialogs')
        version_option.triggered.connect(self.open_version_frame)

        # Help menu options
        home_page_option = QAction(QIcon(os.path.join(IMAGES_PATH, '首页.png')), 'Home Page', self)
        home_page_option.setStatusTip('Open Home Page')
        home_page_option.triggered.connect(self.open_home_frame)
        # check for update
        update_option = QAction(QIcon(os.path.join(IMAGES_PATH, 'blank.png')), 'Check for update', self)
        update_option.setStatusTip('Checking for update')
        update_option.triggered.connect(self.open_update_frame)
        # Report a bug
        report_bug_option = QAction(QIcon(os.path.join(IMAGES_PATH, '反馈.png')), 'Report a bug', self)
        report_bug_option.setStatusTip('Reporting a bug')
        report_bug_option.triggered.connect(self.open_report_frame)

        # menu bar object
        menu_bar = self.menuBar()
        # 兼容Mac
        menu_bar.setNativeMenuBar(False)
        # 添加进菜单栏
        # File
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(file_option)
        # Options
        options_menu = menu_bar.addMenu('&Options')
        options_menu.addAction(advance_option)
        # About
        about_menu = menu_bar.addMenu('&About')
        about_menu.addAction(license_option)
        about_menu.addAction(version_option)
        # Help
        help_menu = menu_bar.addMenu('&Help')
        help_menu.addAction(home_page_option)
        help_menu.addAction(update_option)
        help_menu.addAction(report_bug_option)

        # 布局, layout
        # 第一块 target url
        target_url = QLabel('Target URL(eg http://example.com:80/)')
        self.target_url_field.setText('http://')
        self.target_url_field.setFocus()

        # 第二块 Number of threads 滑块
        threads = QLabel('Number of threads')
        self.thread_slider.setMaximum(100)
        self.thread_slider.setMinimum(1)
        self.thread_slider.valueChanged.connect(self.change_thread)
        self.thread_slider.setFixedWidth(300)
        self.thread_number.textChanged.connect(self.change_thread_field)
        self.thread_number.setMaxLength(3)
        self.thread_number.setFixedWidth(50)
        self.thread_number.setText('1')
        go_fast = QCheckBox('Go Fast', self)
        go_fast.stateChanged.connect(self.go_fast)

        # 第三块 File with list of dirs/files
        file_path = QLabel('File with list of dirs/files')
        browser_button = QPushButton("Browser")
        browser_button.clicked.connect(self.open_file)

        # 第四块 Brute options
        dir_to_start = QLabel('Dir to start with: ')
        self.brute_force_dirs.toggle()
        self.brute_force_files.stateChanged.connect(self.brute_file_toggle)
        self.dir_start_field.setText('/')
        self.dir_start_field.setFixedWidth(200)
        file_extension = QLabel('File Extension: ')
        self.file_extension_field.setText('php')
        self.file_extension_field.setFixedWidth(200)
        self.file_extension_field.setDisabled(True)

        # 第五块 Console
        console_label = QLabel('Console')
        self.console_field.setMinimumHeight(150)
        self.console_field.setReadOnly(True)
        exit_button = QPushButton('Exit')
        exit_button.clicked.connect(QCoreApplication.instance().quit)
        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.clear_console)
        self.pause_button.clicked.connect(self.pause_scan)
        self.start_button.clicked.connect(self.start_scanner)

        # main layout
        main_layout = QVBoxLayout()

        # 第一块 target url group box layout
        target_group_box = QGroupBox()
        layout = QVBoxLayout()
        layout.addWidget(target_url)
        layout.addWidget(self.target_url_field)
        target_group_box.setLayout(layout)

        # 第二块 threads number toggle group box layout
        threads_group_box = QGroupBox()
        thread_qh = QHBoxLayout()
        thread_qh.addWidget(threads)
        thread_qh.addWidget(self.thread_slider)
        thread_qh.addWidget(self.thread_number)
        thread_qh.addStretch(1)
        thread_qh.addWidget(go_fast)
        threads_group_box.setLayout(thread_qh)

        # 第三块 dictionary file path group box layout
        dict_path_group_box = QGroupBox()
        # qv是 第一行显示信息"File with list of dirs/files" 的 QVBoxLayout 布局
        dirs_qv = QVBoxLayout()
        dirs_qv.addWidget(file_path)
        # browser 和 List info 按钮布局
        browser_qh = QHBoxLayout()
        browser_qh.addWidget(self.file_path_field)
        browser_qh.addWidget(browser_button)
        browser_qh.addWidget(self.list_info_button)
        dirs_qv.addLayout(browser_qh)
        dict_path_group_box.setLayout(dirs_qv)

        # 第四块 brute force files extension group box layout
        brute_group_box = QGroupBox()
        # first line QVBoxLayout layout
        brute_qv = QVBoxLayout()
        # second line QVBoxLayout layout
        # raw layout in brute first line
        brute_raw_qh1 = QHBoxLayout()
        brute_raw_qh1.addWidget(self.brute_force_dirs)
        brute_raw_qh1.addStretch(1)
        brute_raw_qh1.addWidget(dir_to_start)
        brute_raw_qh1.addWidget(self.dir_start_field)
        # raw layout in brute second line
        brute_raw_qh2 = QHBoxLayout()
        brute_raw_qh2.addWidget(self.brute_force_files)
        brute_raw_qh2.addStretch(1)
        brute_raw_qh2.addWidget(file_extension)
        brute_raw_qh2.addWidget(self.file_extension_field)
        # 添加 两个行布局
        brute_qv.addLayout(brute_raw_qh1)
        brute_qv.addLayout(brute_raw_qh2)
        brute_group_box.setLayout(brute_qv)

        # 第五块 console group box layout
        console_group_box = QGroupBox()
        console_qv = QVBoxLayout()
        console_qv.addWidget(console_label)
        console_qv.addWidget(self.console_field)
        exit_button_qh = QHBoxLayout()
        exit_button_qh.addWidget(exit_button)
        # 默认是所有控件撑满整个布局文件, 在两个控件后增加这一行，相当于水平布局中存在：按钮1-按钮2-stretch，
        # 此时addStretch的参数只要大于0，则表示占满整个布局最后一部分，前面的控件显示为正常大小，不要拉伸
        # stretch可以放在想放的位置
        exit_button_qh.addStretch(1)
        exit_button_qh.addWidget(clear_button)
        exit_button_qh.addWidget(self.pause_button)
        exit_button_qh.addWidget(self.start_button)
        # 将 exit button 集合添加进 console_qv
        console_qv.addLayout(exit_button_qh)
        console_group_box.setLayout(console_qv)

        # 往 main_layout 里面添加东西
        main_layout.addWidget(target_group_box)
        main_layout.addWidget(threads_group_box)
        main_layout.addWidget(dict_path_group_box)
        main_layout.addWidget(brute_group_box)
        main_layout.addWidget(console_group_box)
        # end

        # Widget 中添加布局
        widget.setLayout(main_layout)
        self.resize(550, 700)
        self.center()
        self.setWindowTitle('WebDirScanner V1.0')
        self.setWindowIcon(QIcon('Icon.png'))
        self.show()

    def center(self):
        """将窗口居中"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def change_thread(self, number):
        """通过滑块设置 threads number field 的值, 并且让 thread number field 聚焦"""
        self.thread_number.setFocus()
        self.thread_number.setText(str(number))

    def change_thread_field(self, value):
        """当线程数field值改变的时候触发这个函数"""
        try:
            value = int(value)
        except:
            value = 0
        self.thread_slider.setValue(value)

    def go_fast(self, state):
        """点击了go fast 按钮, 会尽可能多的增加线程"""
        if state == Qt.Checked:
            self.thread_number.setText('100')
        else:
            self.thread_number.setText('1')

    def open_file(self):
        """opening brute dictionary file path"""
        file_name = QFileDialog.getOpenFileName(self, 'Open file', DICT_PATH)

        if file_name[0]:
            # self.text_edit.setText("Selecting {} file".format(file_name[0]))
            self.file_path_field.setText(file_name[0])
            self.statusBar().showMessage("Selected {} file".format(file_name[0]))

    def brute_file_toggle(self, state):
        if state == Qt.Checked:
            self.file_extension_field.setDisabled(False)
        else:
            self.file_extension_field.setDisabled(True)

    def open_advance_frame(self):
        print('点击了 Options 中的Advanced')

    def open_license_frame(self):
        print('点击了 About menu')

    def open_version_frame(self):
        print('点击了 Version menu')

    def open_home_frame(self):
        print('点击了 Home page menu')

    def open_update_frame(self):
        print('点击了 Update menu')

    def open_report_frame(self):
        print('点击了 report bug menu')

    def clear_console(self):
        """clear console text area"""
        self.console_field.clear()

    def pause_scan(self):
        if self.pause_button.text() == 'Pause':
            self.pause_button.setText('Restart')
            # 让暂停属性为 True
            self.handle_scan.pause_scan = True
        elif self.pause_button.text() == 'Restart':
            self.pause_button.setText('Pause')
            self.handle_scan.pause_scan = False
            self.console_field.append('Restarting...')


    def start_scanner(self):
        """
        按了 start 扫描按钮, 获取 1. self.target_url_field 2. self.thread_number 3. self.file_path_field
        4. self.brute_force_dirs 5. self.brute_force_files 6. self.dir_start_field 7. self.file_extension 的内容

        HandleScan() 类是专门另外开一个线程处理 request 任务的, 防止主 window 程序卡死
        :return:
        """
        target_url = self.target_url_field.text()
        threads_number = self.thread_number.text()
        brute_dict_path = self.file_path_field.text()
        is_brute_force_dirs = self.brute_force_dirs.isChecked()
        is_brute_force_files = self.brute_force_files.isChecked()
        dir_start_with = self.dir_start_field.text()
        file_extension = self.file_extension_field.text()

        # 逻辑变换
        if self.start_button.text() == 'Start':
            self.start_button.setText('Stop')
            self.pause_button.setEnabled(True)
        elif self.start_button.text() == 'Stop':
            # 停止扫描
            self.start_button.setText('Start')
            self.pause_button.setText('Pause')
            self.pause_button.setEnabled(False)

        # 是否是变成了Stop, 如果是 Stop, 就开始扫描
        if self.start_button.text() == 'Stop':
            # 首先需要target url 合法, 才进行下一步的诊断
            if not target_url or not urlparse(target_url).netloc:
                reply = QMessageBox.warning(self, "Warning", "Url不能为空 和 不合法值", QMessageBox.Yes)
                self.start_button.setEnabled(True)
                if reply == QMessageBox.Yes:
                    self.target_url_field.setFocus()
            else:
                # 其他项的判断
                if not brute_dict_path:
                    brute_dict_path = None
                if not is_brute_force_files:
                    file_extension = None
                if not dir_start_with:
                    dir_start_with = None
                if not file_extension:
                    file_extension = None

                # get random User-Agent
                with open(os.path.join(DATA_PATH, 'user_agent.txt'), 'rb') as r:
                    user_agent_list = r.readlines()
                # 随机选择一个 User-Agent
                user_agent = random.choice(user_agent_list).strip()
                HEADER['User-Agent'] = user_agent

                # 初始化 HandleScan() 对象
                self.handle_scan = HandleScan(url=target_url, header=HEADER, thread_number=threads_number,
                                         brute_dict_path=brute_dict_path, is_brute_force_dirs=is_brute_force_dirs,
                                         dir_start_with=dir_start_with, file_extension=file_extension)

                # 检查正常 url 是否可用
                result = self.handle_scan.examine_url(target_url)
                if not result:
                    # 连接出错
                    reply = QMessageBox.question(self, "Warning", "目标Url无法建立连接, 需要重试吗?",
                                                 QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        reply_info = QMessageBox.information(self, 'Information', '重试中...', QMessageBox.Yes)
                        self.start_button.setEnabled(True)
                        if reply_info == QMessageBox.Yes:
                            self.start_button.click()
                    elif reply == QMessageBox.No:
                        self.target_url_field.setFocus()
                        self.start_button.setEnabled(True)
                else:
                    # 开启独立发送请求线程, 接收回传数据, 开启独立线程的原因是避免阻塞主Window
                    self.handle_scan.start()
                    self.handle_scan.signal_qt.connect(self.handle_signal)
        elif self.start_button.text() == 'Start':
            # 停止扫描呗
            self.handle_scan.stop_scan = True

    def handle_signal(self, signal):
        self.console_field.append(signal)
        if signal == 'Done':
            # 退出线程
            self.handle_scan.quit()
            self.start_button.setEnabled(True)
            self.start_button.setText('Start')
            self.pause_button.setEnabled(False)
            self.pause_button.setText('Pause')
            QMessageBox.information(self, 'Information', '扫描完成!', QMessageBox.Yes)

        elif signal == 'Paused':
            self.start_button.setEnabled(True)
            QMessageBox.information(self, 'Information', '扫描暂停!', QMessageBox.Yes)

        elif signal == 'Stopped':
            self.handle_scan.quit()
            self.start_button.setEnabled(True)
            QMessageBox.information(self, 'Information', '扫描取消!', QMessageBox.Yes)

        elif signal == 'Error':
            self.handle_scan.quit()
            self.start_button.setEnabled(True)
            QMessageBox.information(self, 'Information', '扫描参数出错!', QMessageBox.Yes)


class ListInfoDialog(QWidget):
    """
    实现弹出 dict 列表的类
    """
    def __init__(self):
        super().__init__()
        # 控制QWidget的初始化的量, 如果 self.count 等于1时, 就初始化界面, 而如果大于1的时候, 仅仅调用 self.show() 即可
        self.count = 1

    def init_ui(self):
        """显示 List Info Dialog UI"""
        dict_list_field = QTextEdit()
        dict_list_field.setMinimumHeight(450)
        dict_list_field.setMinimumWidth(500)
        dict_list_field.setReadOnly(True)
        dict_list_field.setText(DICT_LIST_TEXT)
        exit_button = QPushButton('Close', self)
        exit_button.clicked.connect(self.close_window)

        # 每行的布局
        list_qh = QVBoxLayout()
        list_qh.addWidget(dict_list_field)

        exit_button_qv = QHBoxLayout()
        exit_button_qv.addWidget(exit_button)
        exit_button_qv.addStretch(1)

        list_qh.addLayout(exit_button_qv)

        self.setLayout(list_qh)
        self.resize(500, 500)
        self.center()
        self.setWindowTitle('WebDirScanner 1.0 Brute Forcing List Information')

        self.show()

    def show_ui(self):
        if self.count == 1:
            self.init_ui()
        else:
            self.show()

        self.count += 1

    def center(self):
        """将窗口居中"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def close_window(self):
        self.hide()


def random_choice_dict():
    """随机选择 dict 目录下的字典, 排除 apache_user 目录中的内容"""
    dict_path_list = os.listdir(DICT_PATH)
    try:
        dict_path_list.remove('apache_user')
    except:
        pass
    return random.choice(dict_path_list)


class HandleScan(QThread):
    """
    使用独立的线程类处理 request 请求任务, 避免主 Window 阻塞, 并与 主Window 信号交互
    """
    # 定义类属性
    signal_qt = pyqtSignal(str)
    # 使用队列
    self_queue = queue.Queue()

    def __init__(self, url, header, thread_number, brute_dict_path, is_brute_force_dirs,
                 dir_start_with, file_extension):
        super(HandleScan, self).__init__()
        # 设置工作状态和信号
        self.working = True

        # 正常化 url
        self.url = self.normalization_url(url)
        if not self.url or not urlparse(self.url).netloc:
            print(colored('Please input target url or normal url and do not fuck me, ok?', 'red'))
            sys.exit(1)
        self.header = header
        self.thread_number = thread_number
        if not self.thread_number:
            self.thread_number = 1
        self.brute_dict_path = brute_dict_path
        if not self.brute_dict_path:
            self.brute_dict_path = os.path.join(DICT_PATH, random_choice_dict())
        self.is_brute_force_dirs = is_brute_force_dirs
        self.dir_start_with = dir_start_with
        if not self.dir_start_with:
            self.dir_start_with = '/'
        self.file_extension = file_extension
        # 阈值
        self.threshold = 3
        self.pause_scan = False
        self.stop_scan = False
        self.record_process = 0

    def debug(self):
        """display all of parameter"""
        return "url -> {}, thread_number -> {}, brute_dict_path -> {}, is_brute_force_dicts -> {}, " \
               "dir_start_with -> {}, file_extension -> {}".format(self.url, self.header, self.thread_number,
                                                                   self.brute_dict_path, self.is_brute_force_dirs,
                                                                   self.dir_start_with, self.file_extension)

    def run(self):
        # 获取所有添加好的 payload url, 不启用queue
        if int(self.thread_number) == 1:
            payload_url_list = self.get_payload_list(is_queue=False)
        elif 1 < int(self.thread_number) <= 100:
            payload_url_list = self.get_payload_list(is_queue=True)
        else:
            payload_url_list = []

        timeout = 10
        # threshold: control request failed resend time interval
        threshold = 3
        # flow_threshold: time interval per request
        flow_threshold = 0

        # 监听循环
        while True:
            if self.stop_scan:
                print('老子按了stop')
                self.signal_qt.emit('Stopped')
                break

            # 发送请求
            # send_request threshold 参数是控制重发次数 flow_threshold 是 每发一个的等待时间, 避免速度过快
            if int(self.thread_number) == 1:
                # 如果有记录点, 就从这恢复
                if self.record_process != 0:
                    if not self.pause_scan:
                        payload_url_list = payload_url_list[self.record_process:]
                        # 做完事情之后就重置 self.record_process
                        # self.record_process = 0

                        for url in payload_url_list:
                            if not self.pause_scan and not self.stop_scan:
                                # 如果 pause_scan 为False 和 stop_scan 为False
                                while threshold > 0:
                                    try:
                                        response = requests.get(url, headers=self.header, proxies=None, cookies=None, timeout=timeout)
                                        # 返回给前端, 每命中一个发送一个信号
                                        if response.status_code != 404:
                                            self.signal_qt.emit("[<span style='color: green'>{}</span>]{}".format(response.status_code, url))

                                        # 暂时放着, 看看是不是 QThread 的 sleep 方法
                                        self.sleep(flow_threshold)
                                        break
                                    except requests.ConnectionError:
                                        threshold -= 1
                                        continue
                                    except requests.ConnectTimeout:
                                        threshold -= 1
                                        continue
                                    except:
                                        threshold -= 1
                                        continue

                            elif self.pause_scan and not self.stop_scan:
                                # 如果 pause_scan 为True 和 stop_scan 为False
                                self.record_process = payload_url_list.index(url)
                                break

                            elif self.stop_scan:
                                # 单纯的停止扫描
                                break
                    else:
                        # 如果有记录点, 但是 self.pause 为False 就不执行任何操作
                        time.sleep(2)
                        print("老子在这等待 重新扫描嘞")
                        continue

                else:
                    # 没有任何记录点
                    for url in payload_url_list:
                        if not self.pause_scan and not self.stop_scan:
                            # 如果 pause_scan 为False 和 stop_scan 为False
                            while threshold > 0:
                                try:
                                    response = requests.get(url, headers=self.header, proxies=None, cookies=None, timeout=timeout)
                                    # 返回给前端, 每命中一个发送一个信号
                                    if response.status_code != 404:
                                        self.signal_qt.emit("[<span style='color: green'>{}</span>]{}".format(response.status_code, url))

                                    # 暂时放着, 看看是不是 QThread 的 sleep 方法
                                    self.sleep(flow_threshold)
                                    break
                                except requests.ConnectionError:
                                    threshold -= 1
                                    continue
                                except requests.ConnectTimeout:
                                    threshold -= 1
                                    continue
                                except:
                                    threshold -= 1
                                    continue

                        elif self.pause_scan and not self.stop_scan:
                            # 如果 pause_scan 为True 和 stop_scan 为False
                            self.record_process = payload_url_list.index(url)
                            break

                        elif self.stop_scan:
                            # 单纯的停止扫描
                            break

                    if not self.pause_scan and not self.stop_scan:
                        # 如果 pause_scan 和 stop_scan 都为 False
                        self.signal_qt.emit("Done")
                        # 退出整个的监听循环
                        break

                    elif self.pause_scan and not self.stop_scan:
                        # 如果 pause_scan 为True 和 stop_scan 为 False
                        print('点了暂停的记录点', self.record_process)
                        self.signal_qt.emit("Paused")

                    elif self.stop_scan:
                        # 如果 stop _scan 为 True
                        self.signal_qt.emit('Stopped')
                        # 退出整个的监听循环
                        break

                    else:
                        # 错误了
                        self.signal_qt.emit('Error')
                        # 退出整个的监听循环
                        break

            elif 1 < int(self.thread_number) <= 100:
                for i in range(int(self.thread_number)):
                    # 控制发送速率
                    self.sleep(flow_threshold)
                    t = Thread(target=self.multi_request, args=(timeout, threshold))
                    t.start()

                while True:
                    self.self_queue.join()
                    self.signal_qt.emit("Done")
                    break
            else:
                # 错误的分支
                self.signal_qt.emit('Error')
                # 退出整个的监听循环
                break

            if self.pause_scan:
                # 如果 self.pause_scan 为 true, 就休息2秒, 继续循环等待
                time.sleep(2)
                continue

    def get_payload_list(self, is_queue=False):
        """
        get_payload_list function aim that handle payload dictionary increase to current url and return the new payload
        url list

        :param is_queue: do you use queue?
        :return: all of urls of added payload
        """
        # 所有字典中包含的 "路径"/"文件" 放入 all_dir_path_list
        with open(self.brute_dict_path, 'rb') as r:
            all_dir_path_list = r.readlines()

        # 包含所有的 拼接之后的 url
        payload_url_list = []

        # 拼接成 payload_url, 然后放入 payload_url_list
        for line in all_dir_path_list:
            # 跳过 空行、#开头的、空格开头的 行
            # 解码为 str
            line = line.decode('utf8').strip()
            if line.startswith('#') or line.startswith(' '):
                continue

            # 拼接
            payload_url = self.url + line

            if payload_url.strip() != self.url.strip() or payload_url.strip() != (self.url.strip()+'/'):
                if is_queue:
                    self.self_queue.put(payload_url)
                else:
                    payload_url_list.append(payload_url)

        return payload_url_list

    def multi_request(self, timeout=10, threshold=3):
        """
        处理多线程请求任务

        :param timeout:
        :param threshold: 控制失败重发次数
        :return: None
        """
        while True:
            while threshold > 0:
                try:
                    # url 为从队列中获取
                    url = self.self_queue.get()
                    response = requests.get(url, headers=self.header, proxies=None, cookies=None, timeout=timeout)

                    # 返回给前端, 每命中一个发送一个信号
                    if response.status_code != 404:
                        self.signal_qt.emit("[<span style='color: green'>{}</span>]{}".format(response.status_code, url))
                    # 发一个 task_done() 一个
                    self.self_queue.task_done()

                    break
                except requests.ConnectionError:
                    threshold -= 1
                    continue
                except requests.ConnectTimeout:
                    threshold -= 1
                    continue
                except:
                    threshold -= 1
                    continue

            # 队列为空, 全部发送完, 扫描完成
            if self.self_queue.empty():
                break

    @staticmethod
    def normalization_url(url):
        """
        正常化 url, 添加协议, 去掉末尾的/(如果有的话)

        :param url:
        :return:
        """
        urlparse(url)
        if not urlparse(url).netloc:
            normal_url = "{}{}".format('http://', url)
        else:
            normal_url = url
        if normal_url.endswith('/'):
            normal_url = normal_url[:-1]
        return normal_url

    def examine_url(self, test_url):
        """
        检查target url是否可连接, 默认测试3次, timeout为10

        :param test_url: url
        :return: Bool
        """
        is_connect = False
        count = self.threshold

        while count > 0:
            try:
                requests.get(test_url, timeout=10)
                is_connect = True
                break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
                count -= 1
        return is_connect


if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    qt_main_window = MainWindow()

    # 显示 MainWindow UI
    qt_main_window.init_ui()

    # 显示 dict list 弹出框
    list_info_window = ListInfoDialog()
    # 点击"List info"按钮, 弹出 UI
    qt_main_window.list_info_button.clicked.connect(list_info_window.show_ui)

    sys.exit(qt_app.exec_())
