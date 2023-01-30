import operator
import sys
import time, requests, re
import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QCheckBox

import b5200_novel_download as down
from bs4 import BeautifulSoup as BS

from PyQt5 import QtCore, QtGui, QtWidgets

url = 'http://www.b5200.org/modules/article/search.php?searchkey='

headers = {'User-Agent': 'Mozilla/5.0',
           'Content-Type': 'gbk'}
charset = "gbk"
list_novels = []
novel_url = ""
title_list = []
title_list_2 = []
novel_title_main = ""
menu_list_main = []
title_list_main = []


class Ui_Form(object):

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

    def select_novel(self):
        list_novels.clear()
        old_model = self.result_list.model()
        if old_model is not None:
            old_model.removeColumns(0, old_model.rowCount())
        r = requests.get(url + str(self.search_key.toPlainText()), headers=headers)
        r.encoding = charset
        html = r.text
        bf = BS(html, "lxml")
        texts = bf.find_all('table')
        if len(texts) <= 0:
            return
        bs = BS(str(texts[0]), 'lxml')
        novels = bs.find_all('tr')
        if len(novels) > 0:
            for i in range(len(novels)):
                tr = BS(str(novels[i]), 'lxml')
                if not str(tr).__contains__("td"):
                    continue
                tds = tr.find_all('td')
                td2 = BS(str(tds[0]), 'lxml')
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

    def get_list(self):
        title_list.clear()
        title_list_main.clear()
        href_url = self.result_list.currentIndex().data()
        bf = get_method_url(href_url)
        texts = bf.find_all('div', id='list')
        bf = BS(str(texts[0]), "lxml")
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
        self.get_title(href_url)
        self.show_menu()

    def get_title(self, href_url):
        bf = get_method_url(href_url)
        texts = bf.find_all('div', id='info')
        bs = BS(str(texts[0]), 'lxml')
        title = str(bs.find_all('h1')[0].text).replace("<h1>", "")
        global novel_title_main
        novel_title_main = title.replace("</h1>", "\n")

    def show_menu(self):
        self.form.hide()
        dialog1 = QtWidgets.QDialog()
        ui2 = self.Menu_Form()
        ui2.setupUi(dialog1)
        dialog1.show()
        dialog1.exec_()
        self.form.show()

    class Menu_Form(object):
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

            # 获取列数
            column = self.split_title()
            model = QStandardItemModel(column, 4)
            print(title_list_2)
            if title_list_2:
                for i in range(column):
                    row = title_list_2[i]
                    index = []
                    for c in range(len(row)):
                        row1 = row[c]
                        model.setItem(i, c, QStandardItem(row1['title']))
                        index.append(row1)
                    title_list_main.append(index)
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
            self.novel_title.setText(_translate("Form", str(novel_title_main)))
            self.menu_tag.setText(_translate("Form", "目录"))

        def show_chapter(self):
            self.dialog1.hide()
            dialog2 = QtWidgets.QDialog()
            row = self.menu_list.currentIndex().row()
            column = self.menu_list.currentIndex().column()
            raw = title_list_main[row][column]
            last_chap, next_chap = self.get_last_next(int(raw['index']))
            ui3 = self.Ui_Dialog2(last_chap, next_chap)
            ui3.setupUi(dialog2, self.get_content(raw['href']), self.menu_list.currentIndex().data())
            dialog2.show()
            dialog2.exec_()
            self.dialog1.show()

        def split_title(self):
            total = len(title_list)
            if total <= 0:
                return 0
            if (total % 4) != 0:
                column = (total // 4) + 1
            else:
                column = (total // 4)
            for i in range(column+1):
                if i != 0:
                    result = title_list[(i - 1) * 4:i * 4]
                    title_list_2.append(result)
            return column

        def get_last_next(self, index):
            last_chap = ""
            next_chap = ""
            for i in title_list:
                if index == 0:
                    break
                if index - 1 == i:
                    tag = title_list[index - 1]
                    last_chap = tag['href']
                    continue
                if index + 1 == i:
                    tag = title_list[index + 1]
                    next_chap = tag['href']
                    continue
            return last_chap, next_chap

        def get_content(self, content_url):
            bf = get_method_url(content_url)
            texts = bf.find_all('div', id='content')
            ac = []
            for k in range(len(texts[0].contents)):
                line = str(texts[0].contents[k])
                line = line.replace("</p>", "\n\n")
                ac.append(line.replace("<p>", ""))
            content = "".join(ac)
            content = content.replace("<content></content>", "")
            return deal_novel_content(content)

        class Ui_Dialog2(object):
            def __init__(self, current_index):
                self.current_index = current_index

            def setupUi(self, Dialog2, content, chapter):
                Dialog2.setObjectName("Dialog2")
                Dialog2.resize(961, 929)
                self.novel_title_2 = QtWidgets.QLabel(Dialog2)
                self.novel_title_2.setGeometry(QtCore.QRect(30, 10, 111, 21))
                self.novel_title_2.setObjectName("novel_title_2")
                self.chapter = QtWidgets.QLabel(Dialog2)
                self.chapter.setGeometry(QtCore.QRect(360, 50, 241, 21))
                self.chapter.setAlignment(QtCore.Qt.AlignCenter)
                self.chapter.setObjectName("chapter")
                self.last_btn = QtWidgets.QPushButton(Dialog2)
                self.last_btn.setGeometry(QtCore.QRect(50, 90, 75, 23))
                self.last_btn.setObjectName("last_btn")
                self.next_btn = QtWidgets.QPushButton(Dialog2)
                self.next_btn.setGeometry(QtCore.QRect(800, 100, 75, 23))
                self.next_btn.setObjectName("next_btn")
                self.content = QtWidgets.QTextBrowser(Dialog2)
                self.content.setEnabled(True)
                self.content.setGeometry(QtCore.QRect(30, 140, 901, 771))
                self.content.setText(content)
                self.content.setObjectName("content")
                self.content.setFocusPolicy(QtCore.Qt.NoFocus)

                self.retranslateUi(Dialog2, chapter)
                QtCore.QMetaObject.connectSlotsByName(Dialog2)

            def retranslateUi(self, Dialog2, chapter):
                _translate = QtCore.QCoreApplication.translate
                Dialog2.setWindowTitle(_translate("Form", "小说阅读器"))
                self.novel_title_2.setText(_translate("Form", novel_title_main))
                self.chapter.setText(_translate("Form", chapter))
                self.last_btn.setText(_translate("Form", "上一章"))
                self.next_btn.setText(_translate("Form", "下一章"))

            def last_btn(self):
                bf = get_method_url(self.last_chap)
                texts = bf.find_all('div', id='content')
                ac = []
                for k in range(len(texts[0].contents)):
                    line = str(texts[0].contents[k])
                    line = line.replace("</p>", "\n\n")
                    ac.append(line.replace("<p>", ""))
                content = "".join(ac)
                content = content.replace("<content></content>", "")
                self.content.clear()
                self.content.setText(deal_novel_content(content))

            def next_btn(self):
                print(self.next_chap)
                bf = get_method_url(self.next_chap)
                texts = bf.find_all('div', id='content')
                ac = []
                for k in range(len(texts[0].contents)):
                    line = str(texts[0].contents[k])
                    line = line.replace("</p>", "\n\n")
                    ac.append(line.replace("<p>", ""))
                content = "".join(ac)
                content = content.replace("<content></content>", "")
                self.content.clear()
                self.content.setText(deal_novel_content(content))


# 判断字符串是否包含中文数字或阿拉伯数字
def isNumber(string):
    return bool(re.search(r'[零一二三四五六七八九十百千万]', string)) or bool(re.search(r'\d', string))


# 处理小说章节正文内容
def deal_novel_content(content):
    enter_count = content.count("\n")
    if enter_count < 10:
        content1 = content
        if str(content).__contains__("。"):
            content1 = content1.replace("。", "。\n\n　　")
        if str(content).__contains__("”"):
            content1 = content1.replace("”", "”\n\n　　")
        if str(content).__contains__("!"):
            content1 = content1.replace("!", "!\n\n　　")
        if str(content).__contains__("】"):
            content1 = content1.replace("】", "】\n\n　　")
        if str(content1).__contains__("。\n\n　　”"):
            content1 = content1.replace("。\n\n　　”", "。”")
        return content1
    return content


# 获取字符串里的数字或字符
# str_type 获取结果类型---->  True:获取数字，False：获取字符串；默认True
def getStrNumOrTxt(string, str_type=True):
    if str_type:
        if isNumber(string):
            num = re.findall(r"\d+", string)
            if not num:
                num = re.findall(r'[零一二三四五六七八九十百千万]+', string)
            return "".join(num)
        else:
            return ""
    else:
        num_txt = re.findall(r"\d+", string)
        if not num_txt:
            num_txt = re.findall(r'[零一二三四五六七八九十百千万]+', string)
        for num in num_txt:
            string = string.replace(num, "")
        return string.replace("第", "").replace("章", "").replace(" ", "").replace(".", "")


# 进度显示
# i -> 当前数量
# num -> 总数量
def sys_progress(i, num):
    num = num - 1
    out = '\r正在下载...  {:.2%}'.format(i / num)
    print(out, end="")


# get方法获取网页
def get_method_url(f_url):
    r = requests.get(f_url, headers=headers)
    r.encoding = charset
    html = r.text
    bf = BS(html, "lxml")
    return bf


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_Form()

    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
