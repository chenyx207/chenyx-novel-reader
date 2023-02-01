import sys, common_func as common
from Menu_Form import Menu_Form

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView, QAbstractItemView
from PyQt5 import QtCore, QtWidgets

url = 'http://www.b5200.org/modules/article/search.php?searchkey='

list_novels = []
novel_url = ""
title_list = []


class Main_View(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(806, 539)
        self.form = Form
        self.search_tag = QtWidgets.QLabel(Form)
        self.search_tag.setGeometry(QtCore.QRect(30, 60, 231, 21))
        self.search_tag.setObjectName("search_tag")

        self.search_key = QtWidgets.QTextEdit(Form)
        self.search_key.setGeometry(QtCore.QRect(260, 50, 221, 31))
        self.search_key.setObjectName("search_key")

        self.search_btn = QtWidgets.QPushButton(Form)
        self.search_btn.setGeometry(QtCore.QRect(500, 50, 71, 31))
        self.search_btn.setObjectName("search_btn")
        self.search_btn.clicked.connect(self.select_novel)

        self.result_tip = QtWidgets.QLabel(Form)
        self.result_tip.setGeometry(QtCore.QRect(600, 50, 141, 31))
        self.result_tip.setObjectName("result_tip")

        self.result_list = QtWidgets.QTableView(Form)
        self.result_list.setGeometry(QtCore.QRect(30, 110, 721, 401))
        self.result_list.setObjectName("result_list")
        self.result_list.doubleClicked.connect(self.get_list)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "小说阅读器"))
        self.search_tag.setText(_translate("Form", "请输入小说名字(可以少字但不能错字):"))
        self.search_btn.setText(_translate("Form", "搜索"))
        self.result_tip.setText(_translate("Form", "共搜索到10条结果"))
        self.result_tip.setHidden(True)

    # 查询小说
    def select_novel(self):
        list_novels.clear()
        old_model = self.result_list.model()
        if old_model is not None:
            old_model.removeColumns(0, old_model.rowCount())
        bf = common.get_method_url(url + str(self.search_key.toPlainText()))
        texts = bf.find_all('table')
        if len(texts) <= 0:
            return
        bs = common.bs_html(str(texts[0]))
        novels = bs.find_all('tr')
        if len(novels) > 0:
            for i in range(len(novels)):
                tr = common.bs_html(str(novels[i]))
                if not str(tr).__contains__("td"):
                    continue
                tds = tr.find_all('td')
                td2 = common.bs_html(str(tds[0]))
                a = td2.find('a')
                row = {
                    'index': i,
                    'href': a['href'],
                    'name': a.string,
                    'author': str(tds[2]).replace('<td class="odd">', '').replace('</td>', '')
                }
                list_novels.append(row)
        self.result_tip.setHidden(False)
        self.result_tip.setText("共搜索到" + str(len(list_novels)) + "条结果")
        model = QStandardItemModel(len(list_novels), 3)
        model.setHorizontalHeaderLabels(["标题", "作者", "链接"])
        for i in range(len(list_novels)):
            row = list_novels[i]
            title_item = QStandardItem(row['name'])
            title_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            title_item.setEnabled(False)
            model.setItem(i, 0, title_item)
            author_item = QStandardItem(row['author'])
            author_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            author_item.setEnabled(False)
            model.setItem(i, 1, author_item)
            href_item = QStandardItem(row['href'])
            href_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            model.setItem(i, 2, href_item)
            # for column in range(3):
            #     item = QStandardItem('row %s,column %s' % (i, column))
            #     # 设置每个位置的文本值
            #     self.result_list.setItem(i, column, item)
        self.result_list.setModel(model)
        # 水平方向标签拓展剩下的窗口部分，填满表格
        self.result_list.horizontalHeader().setStretchLastSection(True)
        # 水平方向，表格大小拓展到适当的尺寸
        self.result_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格内容不可编辑
        self.result_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # 获取小说目录
    def get_list(self):
        # 重新查询时先清理历史数据
        title_list.clear()
        # 获取当前选中框的数据
        href_url = self.result_list.currentIndex().data()
        bf = common.get_method_url(href_url)
        texts = bf.find_all('div', id='list')
        bf = common.bs_html(str(texts[0]))
        texts = bf.find_all('a')
        num = 0
        del texts[0:9]
        for ac in texts:
            title = str(ac.text)
            row = {
                # 章节下标
                "index": num,
                # 章节名
                "title": title,
                # 章节链接
                "href": ac.attrs['href']
            }
            title_list.append(row)
            num += 1
        self.show_menu(href_url)

    # 获取小说标题

    # 打开目录界面
    def show_menu(self, href_url):
        self.form.hide()
        dialog1 = QtWidgets.QDialog()
        ui2 = Menu_Form(title_list=title_list, novel_name=common.get_title(href_url), href_url=href_url)
        ui2.setupUi(dialog1)
        dialog1.show()
        dialog1.exec_()
        self.form.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Main_View()

    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
