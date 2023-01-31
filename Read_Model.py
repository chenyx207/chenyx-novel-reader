# �Ķ�����

from PyQt5 import QtCore, QtWidgets
import common_func


class Read_Model(object):

    def __init__(self, title_list, novel_name, current_chap):
        # ԭʼĿ¼�б�
        self.title_list = title_list
        # С˵����
        self.novel_name = novel_name
        # ��ǰ�½�
        self.current_chap = current_chap

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
        self.last_btn.clicked.connect(self.last_btn_func)
        self.next_btn = QtWidgets.QPushButton(Dialog2)
        self.next_btn.setGeometry(QtCore.QRect(800, 100, 75, 23))
        self.next_btn.setObjectName("next_btn")
        self.next_btn.clicked.connect(self.next_btn_func)
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
        Dialog2.setWindowTitle(_translate("Form", "С˵�Ķ���"))
        self.novel_title_2.setText(_translate("Form", self.novel_name))
        self.chapter.setText(_translate("Form", chapter))
        self.last_btn.setText(_translate("Form", "��һ��"))
        self.next_btn.setText(_translate("Form", "��һ��"))

    # ��һ��
    def last_btn_func(self):
        href, title = self.get_near_chapter(0)
        if str(href).__eq__(""):
            return
        bf = common_func.get_method_url(href)
        texts = bf.find_all('div', id='content')
        ac = []
        for k in range(len(texts[0].contents)):
            line = str(texts[0].contents[k])
            line = line.replace("</p>", "\n\n")
            ac.append(line.replace("<p>", ""))
        content = "".join(ac)
        content = content.replace("<content></content>", "")
        self.chapter.clear()
        self.chapter.setText(title)
        self.content.clear()
        self.content.setText(common_func.deal_novel_content(content))

    # ��һ��
    def next_btn_func(self):
        href, title = self.get_near_chapter(1)
        if str(href).__eq__(""):
            return
        bf = common_func.get_method_url(href)
        texts = bf.find_all('div', id='content')
        ac = []
        for k in range(len(texts[0].contents)):
            line = str(texts[0].contents[k])
            line = line.replace("</p>", "\n\n")
            ac.append(line.replace("<p>", ""))
        content = "".join(ac)
        content = content.replace("<content></content>", "")
        self.chapter.clear()
        self.chapter.setText(title)
        self.content.clear()
        self.content.setText(common_func.deal_novel_content(content))

    # ��ȡ�ٽ��½��±꣬0-��һ�¡�1-��һ��
    def get_near_chapter(self, near=0):
        max_chap = len(self.title_list) - 1
        if self.current_chap == max_chap and near == 1:
            return ""
        if self.current_chap == 0 and near == 0:
            return ""
        if near == 1:
            raw = self.title_list[self.current_chap + 1]
        else:
            raw = self.title_list[self.current_chap - 1]
        self.current_chap = raw['index']
        return raw['href'], raw['title']
