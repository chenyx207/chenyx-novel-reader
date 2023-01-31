# ��������

import requests, re
from bs4 import BeautifulSoup as BS

# ������������
headers = {'User-Agent': 'Mozilla/5.0',
           'Content-Type': 'gbk'}
charset = "gbk"


# �ж��ַ����Ƿ�����������ֻ���������
def is_number(string):
    return bool(re.search(r'[��һ�����������߰˾�ʮ��ǧ��]', string)) or bool(re.search(r'\d', string))


# ����С˵�½���������
def deal_novel_content(content):
    enter_count = content.count("\n")
    if enter_count < 10:
        content1 = content
        if str(content).__contains__("��"):
            content1 = content1.replace("��", "��\n\n����")
        if str(content).__contains__("��"):
            content1 = content1.replace("��", "��\n\n����")
        if str(content).__contains__("!"):
            content1 = content1.replace("!", "!\n\n����")
        if str(content).__contains__("��"):
            content1 = content1.replace("��", "��\n\n����")
        if str(content1).__contains__("��\n\n������"):
            content1 = content1.replace("��\n\n������", "����")
        return content1
    return content


# ��ȡ�ַ���������ֻ��ַ�
# str_type ��ȡ�������---->  True:��ȡ���֣�False����ȡ�ַ�����Ĭ��True
def get_str_num_or_txt(string, str_type=True):
    if str_type:
        if is_number(string):
            num = re.findall(r"\d+", string)
            if not num:
                num = re.findall(r'[��һ�����������߰˾�ʮ��ǧ��]+', string)
            return "".join(num)
        else:
            return ""
    else:
        num_txt = re.findall(r"\d+", string)
        if not num_txt:
            num_txt = re.findall(r'[��һ�����������߰˾�ʮ��ǧ��]+', string)
        for num in num_txt:
            string = string.replace(num, "")
        return string.replace("��", "").replace("��", "").replace(" ", "").replace(".", "")


# ������ʾ
# i -> ��ǰ����
# num -> ������
def sys_progress(i, num):
    num = num - 1
    out = '\r��������...  {:.2%}'.format(i / num)
    print(out, end="")


# get������ȡ��ҳ
def get_method_url(f_url):
    r = requests.get(f_url, headers=headers)
    r.encoding = charset
    html = r.text
    bf = BS(html, "lxml")
    return bf


# ��BS4������ҳ
def bs_html(html):
    return BS(html, "lxml")


# ��ȡ�½�����
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


# �ָ�����
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
    return column


# ��ȡС˵����
def get_title(href_url):
    bf = get_method_url(href_url)
    texts = bf.find_all('div', id='info')
    bs = bs_html(str(texts[0]))
    title = str(bs.find_all('h1')[0].text).replace("<h1>", "")
    return title.replace("</h1>", "\n")
