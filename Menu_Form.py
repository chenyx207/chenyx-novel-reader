# Ŀ¼����

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView, QAbstractItemView

import common_func
from Read_Model import Read_Model


class Menu_Form(object):

    def __init__(self, title_list, novel_name):
        # ԭʼ����Ŀ¼�б�
        self.title_list = title_list
        # С˵����
        self.novel_name = novel_name
        # Ŀ¼�б���һ�ε��Ŀ¼ȷ������һ��
        self.menu_data = []

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
        self.menu_list = QtWidgets.QTableView(Dialog1)
        self.menu_list.setGeometry(QtCore.QRect(40, 110, 741, 441))
        self.menu_list.setObjectName("menu_list")

        # ��ȡ����
        column = common_func.split_title(self.title_list, 4)
        model = QStandardItemModel(column, 4)
        if self.menu_list:
            for i in range(column):
                row = self.menu_list[i]
                index = []
                for c in range(len(row)):
                    row1 = row[c]
                    model.setItem(i, c, QStandardItem(row1['title']))
                    index.append(row1)
                self.menu_data.append(index)
            self.menu_list.setModel(model)
            # ˮƽ�����ǩ��չʣ�µĴ��ڲ��֣��������
            self.menu_list.horizontalHeader().setStretchLastSection(True)
            # ˮƽ���򣬱���С��չ���ʵ��ĳߴ�
            self.menu_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # ���ñ�����ݲ��ɱ༭
            self.menu_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.menu_list.clicked.connect(self.show_chapter)

        self.retranslateUi(Dialog1)
        QtCore.QMetaObject.connectSlotsByName(Dialog1)

    def retranslateUi(self, Dialog1):
        _translate = QtCore.QCoreApplication.translate
        Dialog1.setWindowTitle(_translate("Form", "С˵�Ķ���"))
        self.novel_title.setText(_translate("Form", self.novel_name))
        self.menu_tag.setText(_translate("Form", "Ŀ¼"))

    # ���Ķ�����
    def show_chapter(self):
        self.dialog1.hide()
        dialog2 = QtWidgets.QDialog()
        row = self.menu_list.currentIndex().row()
        column = self.menu_list.currentIndex().column()
        try:
            raw = self.menu_data[row][column]
            current_chap = raw['index']
        except Exception as e:
            print("��ȡ�½ڴ���", e)
            return
        ui3 = Read_Model(title_list=self.title_list, novel_name=self.novel_name, current_chap=current_chap)
        ui3.setupUi(dialog2, common_func.get_content(raw['href']), self.menu_list.currentIndex().data())
        dialog2.show()
        dialog2.exec_()
        self.dialog1.show()
