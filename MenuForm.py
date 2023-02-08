# 目录界面

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView, QAbstractItemView

import common
from ProgressBar import Runthread, pyqtbar
from ReadModel import Read_Model


class Menu_Form(object):

    def __init__(self, title_list, novel_name, href_url):
        # 原始所有目录列表
        self.title_list = title_list
        # 小说名字
        self.novel_name = novel_name
        # 目录列表：第一次点击目录确定是哪一章
        self.menu_data = []
        # 小说详情页链接
        self.href_url = href_url

    def setupUi(self, Dialog1):
        Dialog1.setObjectName("Dialog1")
        Dialog1.resize(827, 581)
        self.dialog1 = Dialog1
        self.novel_title = QtWidgets.QLabel(Dialog1)
        self.novel_title.setGeometry(QtCore.QRect(340, 20, 171, 31))
        self.novel_title.setAlignment(QtCore.Qt.AlignCenter)
        self.novel_title.setObjectName("novel_title")
        self.menu_tag = QtWidgets.QLabel(Dialog1)
        self.menu_tag.setGeometry(QtCore.QRect(50, 70, 101, 21))
        self.menu_tag.setObjectName("menu_tag")

        self.download_btn = QtWidgets.QPushButton(Dialog1)
        self.download_btn.setGeometry(QtCore.QRect(690, 70, 75, 23))
        self.download_btn.setObjectName("download_btn")
        self.download_btn.clicked.connect(self.download)

        self.menu_list = QtWidgets.QTableView(Dialog1)
        self.menu_list.setGeometry(QtCore.QRect(40, 110, 741, 441))
        self.menu_list.setObjectName("menu_list")

        # 获取列数, 分割后的数组
        column, res = common.split_title(self.title_list, 4)
        model = QStandardItemModel(column, 4)
        if res:
            for i in range(column):
                row = res[i]
                index = []
                for c in range(len(row)):
                    row1 = row[c]
                    model.setItem(i, c, QStandardItem(row1['title']))
                    index.append(row1)
                self.menu_data.append(index)
            self.menu_list.setModel(model)
            # 水平方向标签拓展剩下的窗口部分，填满表格
            self.menu_list.horizontalHeader().setStretchLastSection(True)
            # 水平方向，表格大小拓展到适当的尺寸
            self.menu_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # 设置表格内容不可编辑
            self.menu_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.menu_list.clicked.connect(self.show_chapter)

        self.retranslateUi(Dialog1)
        QtCore.QMetaObject.connectSlotsByName(Dialog1)

    def retranslateUi(self, Dialog1):
        _translate = QtCore.QCoreApplication.translate
        Dialog1.setWindowTitle(_translate("Form", "小说阅读器"))
        self.novel_title.setText(_translate("Form", self.novel_name))
        self.download_btn.setText(_translate("Form", "下载"))
        self.menu_tag.setText(_translate("Form", "目录"))

    # 打开阅读界面
    def show_chapter(self):
        self.dialog1.hide()
        dialog2 = QtWidgets.QDialog()
        row = self.menu_list.currentIndex().row()
        column = self.menu_list.currentIndex().column()
        try:
            raw = self.menu_data[row][column]
            current_chap = raw['index']
        except Exception as e:
            print("获取章节错误：", e)
            return
        ui3 = Read_Model(title_list=self.title_list, novel_name=self.novel_name, current_chap=current_chap)
        ui3.setupUi(dialog2, common.get_content(raw['href']), self.menu_list.currentIndex().data())
        dialog2.show()
        dialog2.exec_()

    def download(self):
        work = Runthread(self.href_url)
        bar = pyqtbar(work, len(self.title_list))
        bar.close
