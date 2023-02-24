# 下载方法


import time, operator, os, json, sys, common
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from bs4 import BeautifulSoup as BS
from concurrent.futures import ThreadPoolExecutor, as_completed

# http://www.b5200.org/ 笔趣阁网站爬虫  作者：陈雨鑫
# 程序实现思路：先获取小说详情页面的标题和目录列表，然后将目录列表分成几块，一块开一个线程循环爬这一块目录的正文内容，然后将这些内容存入一个全局的数组，然后再通过设置好的index来排序，最后导出为一个txt文件
# http://www.b5200.org/172_172233/  从火影开始轮回眼俯瞰忍界 ps:章节数少,可以用来测试
# http://www.b5200.org/100_100402/  新白蛇问仙
# http://www.b5200.org/52_52542/    圣墟
# http://www.b5200.org/159_159674/  一个人的道门
# http://www.b5200.org/0_7/         大主宰
# http://www.b5200.org/32_32745/    重生完美时代
# user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
# user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0"
# headers = {"User-Agent": user_agent,"Content-Type": "utf-8", "Connection": "close"}

url = 'http://www.b5200.org/52_52542/'
headers = {'User-Agent': 'Mozilla/5.0',
           'Content-Type': 'gbk'}
charset = "gbk"

# 成功数量
success_num = 0
# 正文集合
file_list = []
# 目录集合
title_list = []
# 失败章节集合
error_list = []
# 目录数量
directory = 0
# 小说名称
file_name = ''
# 特殊字符数组，按照已经存入的格式新增
sp_string = ["\ufffd", "\u2660", "\u2665", "\u200c", "\xa0"]


# 获取目录列表
# is_del -> 是否删除前面9个多余章节； ps: b5200这个网站爬出来后前面会多出来9个章节，是多余的
# skip_num -> 删除前面的目录后跳过多少个章节  ps: 跳过前面多余的章节，如果前面已经爬过这篇小说且有备份的话，可以跳过已经爬过的章节数，只爬取未爬过的章节，然后手动将两篇合在一起
# flag -> 是否重新组装章节数和章节名   ps: 有的小说的章节数奇奇怪怪的，不是正常的’第...章‘这种格式，所以需要提取章节里面的数字和章节名重新组装，不然txt格式的话掌阅这种软件就识别不了目录，就没有目录
def get_list(is_del=9, skip_num=0, flag=False):
    bf = common.get_method_url(url)
    texts = bf.find_all('div', id='list')
    bf = BS(str(texts[0]), "lxml")
    texts = bf.find_all('a')
    num = 0
    if is_del > 0:
        del texts[0:is_del]
    if skip_num > 0:
        del texts[0:skip_num]
    for ac in texts:
        title = str(ac.text)
        # 判断标题是否包含数字
        if not common.is_number(title):
            continue
        # 包含这些内容的一般不是正常章节
        if operator.contains(title, "请假") or operator.contains(title, "感言"):
            continue
        if operator.contains(title, "地一"):
            title = title.replace("地", "第")

        if flag:
            title = "第" + common.get_str_num_or_txt(title) + "章 " + common.get_str_num_or_txt(title, False)
        row = {
            # 章节下标
            "index": num,
            # 章节名
            "title": title + "\n\n",
            # 章节链接
            "href": ac.attrs['href']
        }
        title_list.append(row)
        num += 1
    # 目录数量
    global directory
    directory = len(title_list)
    print("目录数量：" + str(directory))


# 分割数组  ps: 将目录根据数量分成 [[{}, {}], [{}, {}]] 这个形式的数组
# index  每组数量
# target 原数组
def split_list(index, target):
    if str(type(target)) == r"<class 'list'>":
        list_len = len(target)
        if list_len % index == 0:
            total_index = list_len // index
        else:
            total_index = (list_len // index) + 1
        final_result = []
        for i in range(total_index + 1):
            # 跳过0
            if i != 0:
                result = target[(i - 1) * index:i * index]
                final_result.append(result)
        return final_result


# 获取小说名  ps: 也是文件名
def get_title():
    bf = common.get_method_url(url)
    texts = bf.find_all('div', id='info')
    bs = BS(str(texts[0]), 'lxml')
    title = str(bs.find_all('h1')[0].text).replace("<h1>", "")
    global file_name
    file_name = title.replace("</h1>", "\n")
    print("标题===> ", file_name)
    return file_name


# 替换特殊字符
# string -> 原字符串
# args   -> 特殊字符数组
def replace_sp(string, args):
    for v in args:
        string = string.replace(v, "")
    return string


# 导出文件
# name 导出文件名  ps:不用加格式，默认txt
# txt 正文内容
# txt = [{'index':章节序号,'txt':'章节正文内容'}]
def write_txt(name, txt):
    # 打开或创建文件
    file = open(str(name + ".txt"), 'w')
    if str(type(txt)) == r"<class 'list'>":
        # 排序  根据index的值来排序
        txt.sort(key=lambda x: x['index'], reverse=False)
        # 将原数组里的值取出放入新的数组
        new_txt = []
        for t in txt:
            new_txt.append(t['txt'])
        # 写入数据
        if str(type(new_txt)) == r"<class 'list'>":
            for i in new_txt:
                i = replace_sp(i, sp_string)
                file.write(i)
        else:
            file.write(str(new_txt))
    elif str(type(txt)) == r"<class 'str'>":
        file.write(txt)
    else:
        file.write(str(txt))
    file.flush()
    file.close()


# 当最后导出时运行出错，重新导出文件
def re_try(log_name):
    # 如果错误记录不存在，不执行后面的方法
    if not os.path.exists(log_name + ".txt"):
        return
    file = open(str(log_name + ".txt"))
    data = file.readlines()
    file.close()
    re_file_list = []
    for v in data[0].split("|,|"):
        re_file_list.append(json.loads(v))
    try:
        write_txt(file_name, re_file_list)
        # 导出成功, 删除错误记录文件
        os.remove(log_name + ".txt")
        # 成功后正常退出程序
        sys.exit(0)
    except UnicodeEncodeError as ue:
        common.log("特殊字符编码错误，请根据错误提示将特殊字符加入到全局变量 sp_string 中，再重试...", "\n错误：", ue)
        sys.exit(1)
    except Exception as e:
        common.log("重试失败，请根据错误提示修改代码，再重试...", "\n错误：", e)
        sys.exit(1)


class ProcessBar(QtWidgets.QWidget):

    def __init__(self, maximum, href_url):
        super().__init__()
        global url
        url = href_url
        self.work = Runthread()
        self.maximum = maximum
        # self.run_work()

    def run_work(self, dialog3):
        # 创建线程
        # 连接信号
        self.work._signal.connect(self.call_backlog)  # 进程连接回传到GUI的事件

        # 进度条设置
        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setMinimum(0)  # 设置进度条最小值
        self.pbar.setMaximum(self.maximum)  # 设置进度条最大值
        self.pbar.setValue(0)  # 进度条初始值为0
        self.pbar.setGeometry(QRect(1, 3, 499, 28))  # 设置进度条在 QDialog 中的位置 [左，上，右，下]

        # 窗口初始化
        self.setGeometry(300, 300, 500, 32)
        self.setWindowTitle('正在连接')

        # 开始线程
        self.work.start()

    def call_backlog(self, task_number, total_task_number):
        if task_number == 0 and total_task_number == 0:
            self.setWindowTitle(self.tr('正在连接'))
        else:
            label = "正在下载：" + "第" + str(task_number) + "/" + str(total_task_number) + '个章节'
            self.setWindowTitle(self.tr(label))  # 顶部的标题
        self.pbar.setValue(int(task_number))  # 将线程的参数传入进度条

    def close(self):
        self.work.exit()



class pyqtbar():
    def __init__(self, maximum, href_url):
        self.app = QtWidgets.QApplication(sys.argv)
        self.myshow = ProcessBar(maximum=maximum, href_url=href_url)
        self.myshow.show()
        sys.exit(self.app.exec_())

    def close(self):
        self.myshow.close()
        self.app.close()


# 继承QThread
class Runthread(QThread):
    #  通过类成员对象定义信号对象
    _signal = pyqtSignal(int, int)

    def __init__(self):
        super(Runthread, self).__init__()

    def run(self):
        # 先调用重试方法，是否有错误记录；没有再爬取内容
        re_try(file_name + "_error_record_log")
        get_title()
        get_list(flag=False)
        self.thread_download(threads=100, target_list=title_list)

    # 多线程下载小说
    # threads -> 多少章开一个线程，默认100；每个线程再循环爬取小说
    # error_time -> 重试次数，默认10次; 如果要一直重试，传 -1, 但不建议一直重试
    # target_list -> 章节数组
    # target_list = [{'index':章节序号,'title':'章节标题','href':'章节内容链接'}]
    def thread_download(self, threads=100, target_list=None, error_time=10):
        # 重试次数为0直接返回，不执行后面的方法
        if error_time == 0:
            return
        # 每100章开一个线程
        # 获取线程数workers=根据目录总数除以threads
        if target_list is None:
            target_list = []
        # 判断是否能除尽
        if (len(target_list) % threads) != 0:
            workers = (len(target_list) // threads) + 1
        else:
            workers = len(target_list) // threads
        # 根据threads分割总的目录数组分成 [[{}, {}], [{}, {}]] 这个形式的数组
        split_title = split_list(threads, target_list)
        # 设置线程池
        executor = ThreadPoolExecutor(max_workers=workers)
        # 提交线程
        tasks = [executor.submit(self.download_partner, s_list) for s_list in split_title]

        # 所有任务完成后再结束
        # 并将结果存入全局数组
        for task in as_completed(tasks):
            # 每个线程完成后的返回值，就是download_partner()方法的返回值
            res = task.result()
            if str(type(res)) == r"<class 'list'>":
                file_list.extend(res)

        # 将全局错误数组数据装入新数组，并清空全局错误数组数据
        new_error_list = []
        new_error_list.extend(error_list)
        error_list.clear()
        # wait(tasks, return_when=ALL_COMPLETED)
        # 通过递归重新下载异常的章节
        if new_error_list and error_time > 0:
            error_time = error_time - 1
            if error_time <= 0:
                error_time = 0
            self.thread_download(threads=threads, target_list=new_error_list, error_time=error_time)
        elif new_error_list and error_time < 0:
            self.thread_download(threads=threads, target_list=new_error_list, error_time=error_time)
        # 全部下载完成后导出为txt文件
        try:
            write_txt(file_name, file_list)
        except Exception as e:
            common.log("导出文件错误：", e)
            # 导出文件时错误 将数据转为字符串直接写入文件
            write_txt(file_name + "_error_record_log", '|,|'.join(json.dumps(v) for v in file_list))
            common.log("===>>>特殊字符编码错误，请根据错误提示将特殊字符加入到全局变量 sp_string 中再重试；其他错误请修改代码再重试...", "\n错误：", e)
            sys.exit(1)
            # re_try(file_name + "_error_record_log")

    # 每一个线程下载的一部分章节
    # target_list = [{'index':章节序号,'title':'章节标题','href':'章节内容链接'}]
    def download_partner(self, target_list):
        f_list = []
        global success_num
        for target in target_list:
            try:
                index = target['index']  # 章节序号
                title = target['title']  # 章节标题
                href = target['href']  # 章节内容链接
                bf = common.get_method_url(href)
                texts = bf.find_all('div', id='content')
                ac = [title]
                for k in range(len(texts[0].contents)):
                    line = str(texts[0].contents[k])
                    line = line.replace("</p>", "\n\n")
                    ac.append(line.replace("<p>", ""))
                content = "".join(ac)
                content = content.replace("<content></content>", "")

                row = {
                    "index": index,
                    "txt": common.deal_novel_content(content)
                }
                f_list.append(row)
                success_num = success_num + 1
                # 进度显示
                common.sys_progress(success_num, directory)
                self._signal.emit(success_num, directory)  # 发送实时任务进度和总任务进度
            except Exception as e:
                common.log(e)
                error_list.append(target)
            time.sleep(0.05)
        return f_list


if __name__ == "__main__":
    bar = pyqtbar(51, "http://www.b5200.org/128_128316/")
    bar.close()
