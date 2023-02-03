# _*_coding: UTF-8_*_
# 开发作者 ：TXH
# 开发时间 ：2020-09-08 10:20
# 文件名称 ：Qt_Processbar.py
# 开发工具 ：Python 3.7 + Pycharm IDE

from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar
from PyQt5.QtCore import QRect
import sys, time


class ProgressBar(QDialog):
    def __init__(self, parent=None):
        super(ProgressBar, self).__init__(parent)

        # Qdialog窗体的设置
        self.resize(500, 32)  # QDialog窗的大小

        # 创建并设置 QProcessbar
        self.progressBar = QProgressBar(self)  # 创建
        self.progressBar.setMinimum(0)  # 设置进度条最小值
        self.progressBar.setMaximum(100)  # 设置进度条最大值
        self.progressBar.setValue(0)  # 进度条初始值为0
        self.progressBar.setGeometry(QRect(1, 3, 499, 28))  # 设置进度条在 QDialog 中的位置 [左，上，右，下]
        self.show()

    def setValue(self, task_number, total_task_number):  # 设置总任务进度和子任务进度
        if task_number == '0' and total_task_number == '0':
            self.setWindowTitle(self.tr('正在下载中'))
        else:
            label = "正在下载：" + "第" + str(task_number) + "/" + str(total_task_number) + '个章节'
            self.setWindowTitle(self.tr(label))  # 顶部的标题
        self.progressBar.setValue(int(task_number))


class pyqtbar():
    def __init__(self):
        self.app = QApplication(sys.argv)  # 打开系统 app
        self.progressbar = ProgressBar()  # 初始化 ProcessBar实例

    def set_value(self, task_number, total_task_number):
        self.progressbar.setValue(str(task_number), str(total_task_number))  # 更新进度条的值
        QApplication.processEvents()  # 实时刷新显示

    @property
    def close(self):
        self.progressbar.close()  # 关闭进度条
        self.app.exit()  # 关闭系统 app


# total_number    总任务数
# task_id         子任务序号
def third_open(task_id, total_number):
    bar = pyqtbar()  # 创建实例
    for process in range(task_id, total_number):
        bar.set_value(task_id, total_number)  # 刷新进度条
    if task_id >= total_number:
        bar.close  # 关闭 bar 和 app


if __name__ == '__main__':
    third_open(1, 100)
