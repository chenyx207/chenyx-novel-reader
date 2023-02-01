# 公共方法

import requests, re, time
from bs4 import BeautifulSoup as BS

# 公共方法集合
headers = {'User-Agent': 'Mozilla/5.0',
           'Content-Type': 'gbk'}
charset = "gbk"


# 判断字符串是否包含中文数字或阿拉伯数字
def is_number(string):
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
def get_str_num_or_txt(string, str_type=True):
    if str_type:
        if is_number(string):
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


# 用BS4解析网页
def bs_html(html):
    return BS(html, "lxml")


# 获取章节内容
def get_content(content_url):
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


# 分割数组
def split_title(title_list, index):
    total = len(title_list)
    res = []
    if total <= 0:
        return 0
    if (total % index) != 0:
        column = (total // index) + 1
    else:
        column = (total // index)
    for i in range(column + 1):
        if i != 0:
            result = title_list[(i - 1) * index:i * index]
            res.append(result)
    return column, res


# 获取小说标题
def get_title(href_url):
    bf = get_method_url(href_url)
    texts = bf.find_all('div', id='info')
    bs = bs_html(str(texts[0]))
    title = str(bs.find_all('h1')[0].text).replace("<h1>", "")
    return title.replace("</h1>", "\n")


# 打印日志
def log(*args):
    file = open("b5200_error_log.txt", 'a')
    file.write("[" + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "]:   " + "".join(args) + "\n")
    file.flush()
    file.close()
