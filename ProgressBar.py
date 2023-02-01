# _*_coding: UTF-8_*_
# �������� ��TXH
# ����ʱ�� ��2020-09-08 10:20
# �ļ����� ��Qt_Processbar.py
# �������� ��Python 3.7 + Pycharm IDE

from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QLabel, QLineEdit, QProgressBar, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDialogButtonBox
from PyQt5.QtCore import Qt, QBasicTimer, QThread, QRect
import sys


class ProgressBar(QDialog):
    def __init__(self, parent=None):
        super(ProgressBar, self).__init__(parent)

        # Qdialog���������
        self.resize(500, 32)  # QDialog���Ĵ�С

        # ���������� QProcessbar
        self.progressBar = QProgressBar(self)  # ����
        self.progressBar.setMinimum(0)  # ���ý�������Сֵ
        self.progressBar.setMaximum(100)  # ���ý��������ֵ
        self.progressBar.setValue(0)  # ��������ʼֵΪ0
        self.progressBar.setGeometry(QRect(1, 3, 499, 28))  # ���ý������� QDialog �е�λ�� [���ϣ��ң���]
        self.show()

    def setValue(self, task_number, total_task_number, value):  # ������������Ⱥ����������
        if task_number == '0' and total_task_number == '0':
            self.setWindowTitle(self.tr('���ڴ�����'))
        else:
            label = "���ڴ���" + "��" + str(task_number) + "/" + str(total_task_number) + '������'
            self.setWindowTitle(self.tr(label))  # �����ı���
        self.progressBar.setValue(value)


class pyqtbar():
    '''
    task_number�� total_task_number��Ϊ 0 ʱ������ʾ��ǰ���е��������
    task_number<total_task_number ��Ϊ��������������ý����ִ�����ʾ����δ���ñ�����

    # ʹ��ʾ��
    import time
    bar = pyqtbar() # ����ʵ��
    total_number=10
    # ����1
    task_id=1
    for process in range(1, 100):
        time.sleep(0.05)
        bar.set_value(task_id,total_number,process) # ˢ�½�����
    # ����2
    task_id = 2
    for process in range(1, 100):
        time.sleep(0.05)
        bar.set_value(task_id, total_number,process)
    bar.close # �ر� bar �� app
    '''

    def __init__(self):
        self.app = QApplication(sys.argv)  # ��ϵͳ app
        self.progressbar = ProgressBar()  # ��ʼ�� ProcessBarʵ��

    def set_value(self, task_number, total_task_number, i):
        self.progressbar.setValue(str(task_number), str(total_task_number), i + 1)  # ���½�������ֵ
        QApplication.processEvents()  # ʵʱˢ����ʾ

    @property
    def close(self):
        self.progressbar.close()  # �رս�����
        self.app.exit()  # �ر�ϵͳ app


if __name__ == '__main__':

    import time

    # ʹ��ʾ��
    bar = pyqtbar()  # ����ʵ��
    total_number = 10  # ��������
    # ����1
    task_id = 1  # ���������
    for process in range(1, 100):
        time.sleep(0.05)
        bar.set_value(task_id, total_number, process)  # ˢ�½�����
    # ����2
    task_id = 2
    for process in range(1, 100):
        time.sleep(0.05)
        bar.set_value(task_id, total_number, process)

    bar.close  # �ر� bar �� app