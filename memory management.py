# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import threading
from PyQt5.QtCore import Qt

# 表示进程所处状态的全局列表
p_wait = []
p_exe = []
p_finish = []
# 空闲块列表
freelist = []
mode = 1


class MySignal(QObject):
    output = pyqtSignal(str)  # 定义自定义信号


# 重定向sys.stdout以捕获所有标准输出
class MyStream:
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, text):
        self.text_edit.insertPlainText(text)


# 进程类
class Process:
    count = 0

    def __init__(self, size=0, time=0):
        Process.count += 1
        self.id = self.count
        self.size = size
        self.time = time
        self.state = -1  # 默认为-1


# 根据用户输入创建一个空闲块列表
def creat_freelist(freesize):
    freelist.append([0, freesize])


# 创建进程,并将进程放入等待队列中
def creat_process(size, time):
    p = Process(size, time)
    p_wait.append(p)
    result = '创建进程：{0}，大小为：{1}，所需执行时间为{2}\n'.format(p.id, p.size, p.time)
    main.output.emit(result)


# 最先适配思想，找到一个合适的大小就结束
def first_allocate():
    if len(p_wait) == 0:
        return
    elif len(freelist) == 0:
        result = "暂无空闲块，无法放置进程{0}\n"
        main.output.emit(result)
        return
    else:
        for p in p_wait:
            for item in freelist:
                if p.size <= item[1]:  # 有位置能放下
                    # 改变process状态
                    p.state = item[0]
                    p_exe.append(p)
                    p_wait.remove(p)
                    # 更新空闲区放入process
                    if p.size == item[1]:
                        freelist.remove(item)
                    else:
                        item[0] = p.state + p.size
                        item[1] = item[1] - p.size
                    break
            if p.state == -1:
                result = "暂无合适空闲块，无法放置进程{0}\n".format(p.id)
                main.output.emit(result)


def best_allocate():
    if len(p_wait) == 0:
        return
    elif len(freelist) == 0:
        result = "暂无空闲块，无法放置进程{0}\n"
        main.output.emit(result)
        return
    else:
        freelist.sort(key=lambda x: x[1])  # 按照空闲块由小到大排序
        for p in p_wait:
            best = None
            for i in range(len(freelist)):
                if p.size <= freelist[i][1]:  # 能放下且更合适
                    best = i
                    break
            # 放不下
            if best is None:
                result = "暂无合适空闲块，无法放置进程{0}\n".format(p.id)
                main.output.emit(result)
            # 能放下
            else:
                # 改变process状态
                item = freelist[best]
                p.state = item[0]
                p_exe.append(p)
                p_wait.remove(p)
                # 更新空闲区放入process
                if p.size == item[1]:
                    freelist.remove(item)
                else:
                    item[0] = p.state + p.size
                    item[1] = item[1] - p.size
# 进程执行结束，释放内存
def free():
    while True:
        finish = []
        for p in p_exe:
            if p.time == 0:
                # 改变进程状态
                finish.append(p)
                result = '释放进程：{0}\n'.format(p.id)
                main.output.emit(result)
                freelist.append([p.state, p.size])
        # 移出已完成的进程
        for p in finish:
            p_exe.remove(p)
        # 如果没有进程被移除，退出循环
        if len(finish) == 0:
            break


def check():
    freelist.sort(key=lambda x: x[0])  # 排序
    for i in range(len(freelist)):
        if i + 1 < len(freelist):
            if freelist[i][0] + freelist[i][1] == freelist[i + 1][0]:
                freelist[i][1] = freelist[i][1] + freelist[i + 1][1]
                freelist.remove(freelist[i + 1])


def print_freelist():
    result = '空闲块列表：{0}\n'.format([item for item in freelist])
    main.output.emit(result)


class MainWindow(QWidget):  # 主窗口
    output = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.to_paint = False
        self.initUI()

    def initUI(self):
        wlayout = QGridLayout()  # 总体布局：纵向
        # 创建QWidget对象作为主窗口的中心部件
        wlayout.setSpacing(0)  # 网格内部间距为0
        self.setGeometry(500, 500, 680, 600)  # 设置窗口大小和位置
        self.setStyleSheet("background-color:#F1F6F9;")
        self.setLayout(wlayout)  # 窗体本体设置全局布局

        # 创建下拉菜单
        self.comboBox = QComboBox(self)
        self.comboBox.addItems(['1.首次适应算法', '2.最佳适应算法'])
        self.comboBox.setFocusPolicy(Qt.NoFocus)  # 禁用焦点
        self.comboBox.setCurrentIndex(0)  # 将默认值设置为第一个选项
        self.comboBox.setStyleSheet("background-color: #F6F1F1")

        # 连接 activated 信号和槽函数
        self.comboBox.activated.connect(self.on_combo_box_activated)
        wlayout.addWidget(self.comboBox, 0, 0, 30, 640)

        # 创建640个格子 四个参数
        self.line1 = QFrame(self)
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setLineWidth(2)
        wlayout.addWidget(self.line1, 30, 0, 600, -1)
        self.line2 = QFrame(self)
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setLineWidth(2)
        wlayout.addWidget(self.line2, 90, 0, 600, -1)

        # 添加文本框
        self.textbox = QTextEdit()
        self.textbox.setStyleSheet("background-color: white; border-style: solid;\
                                             border-width: 2px; border-radius: 10px; padding: 5px;\
                                             font-family: Arial; font-size: 18px; color: #333;")

        self.textbox.setReadOnly(True)  # 设置为只读模式，避免用户输入
        wlayout.addWidget(self.textbox, 40, 0, 2, 640)
        # 将信号和槽函数关联，当信号被触发时，槽函数会被执行
        self.output.connect(self.handle_output)

        # 加入两个创建进程的输入框

        self.psize_edit = QLineEdit()
        self.ptime_edit = QLineEdit()
        # 设置样式
        self.psize_edit.setStyleSheet("background-color: white; border-style: solid;\
                                                     border-width: 2px; border-radius: 10px; padding: 5px;\
                                                     font-family: Arial; font-size: 18px; color: #333;")
        self.ptime_edit.setStyleSheet("background-color: white; border-style: solid;\
                                                     border-width: 2px; border-radius: 10px; padding: 5px;\
                                                     font-family: Arial; font-size: 18px; color: #333;")
        # 将 QLineEdit 添加到布局中
        wlayout.addWidget(QLabel('进程大小：'), 50, 0, 1, 3)
        wlayout.addWidget(self.psize_edit, 50, 4, 1, 20)
        wlayout.addWidget(QLabel('执行时间：'), 50, 60, 1, 3)
        wlayout.addWidget(self.ptime_edit, 50, 64, 1, 20)

        self.creatbutton = QPushButton('创建进程', self)
        # 连接到创建进程的函数上
        self.creatbutton.clicked.connect(self.create_process)
        self.creatbutton.setStyleSheet("background-color: #F6F1F1")

        wlayout.addWidget(self.creatbutton, 50, 120, 1, 20)

        # 创建按钮
        self.button1 = QPushButton('下一步', self)
        self.button1.clicked.connect(run)
        self.button1.clicked.connect(self.enable_painting)
        self.button1.setStyleSheet("background-color: #F6F1F1")
        self.button1.setFont(QFont("Microsoft YaHei"))

        self.button2 = QPushButton('结束', self)
        self.button2.clicked.connect(QApplication.instance().quit)
        self.button2.setFont(QFont("Microsoft YaHei"))
        self.button2.setStyleSheet("background-color: #F6F1F1")

        wlayout.addWidget(self.button1, 600, 1, 1, 20)
        wlayout.addWidget(self.button2, 600, 50, 1, 20)

    def handle_output(self, result):
        # 将接收到的输出内容添加到 QTextEdit 中
        self.textbox.insertPlainText(result)

    def create_process(self):
        psize = int(self.psize_edit.text())
        ptime = int(self.ptime_edit.text())
        creat_process(psize, ptime)

    def on_combo_box_activated(self):
        global mode
        # 获取用户选择的选项
        selected_option = self.comboBox.currentText()

        # 根据选项的值来设置 mode 值
        if selected_option == '1.首次适应算法':
            mode = 1
        elif selected_option == '2.最佳适应算法':
            mode = 2

    def enable_painting(self):
        self.to_paint = True
        self.update()

    def paintEvent(self, event):
        if self.to_paint:
            qp = QPainter()
            qp.begin(self)

            # 获取两条分割线的位置和宽度
            line1_x = self.line1.geometry().x()
            line1_y = self.line1.geometry().y()

            # 遍历p_exe列表，绘制每个元组对应的方块
            for i, p in enumerate(p_exe):
                # 计算方块的起点和大小
                x = line1_x + p.state
                y = line1_y
                w = p.size
                h = 140

                # 设置方块颜色
                hue = int(p.id * 10) % 360  # 将状态数值映射到 [0, 360) 区间
                color = QColor.fromHsv(hue, 255, 255)  # 根据 hue 值计算颜色值
                qp.setBrush(color)

                # 绘制方块
                qp.drawRect(x, y, w, h)

                # 在方块上标注p.state和p.size
                text = f"{p.state}, {p.size}"
                qp.drawText(x + w // 2, y + h // 2, text)

            qp.end()


def run_gui():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


def run_function():
    # size = int(input("创建空闲块列表，请输入内存大小："))
    creat_freelist(640)
    # run()


def run():
    if mode == 1:
        first_allocate()
    elif mode == 2:
        best_allocate()
    free()
    for p in p_exe:
        p.time -= 1
    check()
    print_freelist()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()

    # gui_thread = threading.Thread(target=run_gui)
    function_thread = threading.Thread(target=run_function)

    # gui_thread.start()
    function_thread.start()

    # gui_thread.join()
    function_thread.join()

    sys.exit(app.exec_())
