import requests, time, operator, re, os, json, sys
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
success_num = -1
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
# 开始时间
start = 0


# 多线程下载小说
# threads -> 多少章开一个线程，默认100；每个线程再循环爬取小说
# error_time -> 重试次数，默认10次; 如果要一直重试，传 -1, 但不建议一直重试
# target_list -> 章节数组
# target_list = [{'index':章节序号,'title':'章节标题','href':'章节内容链接'}]
def thread_download(threads=100, target_list=None, error_time=10):
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
    tasks = [executor.submit(download_partner, s_list) for s_list in split_title]

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
        thread_download(threads=threads, target_list=new_error_list, error_time=error_time)
    elif new_error_list and error_time < 0:
        thread_download(threads=threads, target_list=new_error_list, error_time=error_time)
    # 全部下载完成后导出为txt文件
    try:
        write_txt(file_name, file_list)
    except Exception as e:
        print("导出文件错误：", e)
        # 导出文件时错误 将数据转为字符串直接写入文件
        write_txt(file_name + "_error_record_log", '|,|'.join(json.dumps(v) for v in file_list))
        print("===>>>特殊字符编码错误，请根据错误提示将特殊字符加入到全局变量 sp_string 中再重试；其他错误请修改代码再重试...", "\n错误：", e)
        t_end = time.time()
        print("\nfinished; 耗时：", '%.2f' % ((t_end - start) / 60), "分")
        sys.exit(1)
        # re_try(file_name + "_error_record_log")


# 每一个线程下载的一部分章节
# target_list = [{'index':章节序号,'title':'章节标题','href':'章节内容链接'}]
def download_partner(target_list):
    f_list = []
    global success_num
    for target in target_list:
        try:
            index = target['index']  # 章节序号
            title = target['title']  # 章节标题
            href = target['href']  # 章节内容链接
            bf = get_method_url(href)
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
                "txt": deal_novel_content(content)
            }
            f_list.append(row)
            success_num += 1
            # 进度显示
            sys_progress(success_num, directory)
        except Exception:
            error_list.append(target)
        time.sleep(1)
    return f_list


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


# 获取目录列表
# is_del -> 是否删除前面9个多余章节； ps: b5200这个网站爬出来后前面会多出来9个章节，是多余的
# skip_num -> 删除前面的目录后跳过多少个章节  ps: 跳过前面多余的章节，如果前面已经爬过这篇小说且有备份的话，可以跳过已经爬过的章节数，只爬取未爬过的章节，然后手动将两篇合在一起
# flag -> 是否重新组装章节数和章节名   ps: 有的小说的章节数奇奇怪怪的，不是正常的’第...章‘这种格式，所以需要提取章节里面的数字和章节名重新组装，不然txt格式的话掌阅这种软件就识别不了目录，就没有目录
def get_list(is_del=9, skip_num=0, flag=False):
    bf = get_method_url(url)
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
        if not isNumber(title):
            continue
        # 包含这些内容的一般不是正常章节
        if operator.contains(title, "请假") or operator.contains(title, "感言"):
            continue
        if operator.contains(title, "地一"):
            title = title.replace("地", "第")

        if flag:
            title = "第" + getStrNumOrTxt(title) + "章 " + getStrNumOrTxt(title, False)
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
    bf = get_method_url(url)
    texts = bf.find_all('div', id='info')
    bs = BS(str(texts[0]), 'lxml')
    title = str(bs.find_all('h1')[0].text).replace("<h1>", "")
    global file_name
    file_name = title.replace("</h1>", "\n")
    print("标题===> ", file_name)
    return file_name


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


# 替换特殊字符
# string -> 原字符串
# args   -> 特殊字符数组
def replace_sp(string, args):
    for v in args:
        string = string.replace(v, "")
    return string


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
        r_end = time.time()
        print("\nfinished; 耗时：", '%.2f' % ((r_end - start) / 60), "分")
        # 成功后正常退出程序
        sys.exit(0)
    except UnicodeEncodeError as ue:
        print("特殊字符编码错误，请根据错误提示将特殊字符加入到全局变量 sp_string 中，再重试...", "\n错误：", ue)
        r_end = time.time()
        print("\nfinished; 耗时：", '%.2f' % ((r_end - start) / 60), "分")
        sys.exit(1)
    except Exception as e:
        print("重试失败，请根据错误提示修改代码，再重试...", "\n错误：", e)
        r_end = time.time()
        print("\nfinished; 耗时：", '%.2f' % ((r_end - start) / 60), "分")
        sys.exit(1)


# 判断字符串是否包含中文数字或阿拉伯数字
def isNumber(string):
    return bool(re.search(r'[零一二三四五六七八九十百千万]', string)) or bool(re.search(r'\d', string))


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


# 其他方法调用下载
def third_download(url_href, threads, flag=False):
    global url
    url = url_href
    get_title()
    get_list(flag=flag)
    thread_download(threads=threads, target_list=title_list)


if __name__ == '__main__':
    start = time.time()
    get_title()
    # 先调用重试方法，是否有错误记录；没有再爬取内容
    re_try(file_name + "_error_record_log")
    get_list()
    thread_download(target_list=title_list)
    end = time.time()
    print("\nfinished; 耗时：", '%.2f' % ((end - start) / 60), "分")
