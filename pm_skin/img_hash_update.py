import os
import time
import sqlite3
import threading
from PIL import Image
import requests


# 将多线程的局部变量储存在local_img中
local_img = threading.local()
# 设定同时执行的最大线程数
maxs = 8
threadLimiter=threading.BoundedSemaphore(maxs)


# 空数据异常定义
class EmptyDataError(Exception):
    pass


# 从数据库提取信息
def get_data_from_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM skins WHERE dhash IS NULL LIMIT 32")
    values = cursor.fetchall()
    data_list = []
    for row in values:
        data = {
            'name': row[0],
            'img_url': row[5],
        }
        data_list.append(data)
    # 如果提取的数据字典为空，抛出异常
    if len(data_list) == 0:
        raise EmptyDataError('从数据库提取信息为空！')
    cursor.close()
    conn.close()
    return data_list


# 获取网页内容
def get_content(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.content
    except:
        print('[ERROR][get_html]获取网页内容时发生错误，错误代码%s！' % r.status_code)
        return 403


# 通过URL下载图片并存在本地
def process_img():
    local_img.content = get_content(local_img.url)
    with open('%s.png' % local_img.name, 'wb') as f:
        if not isinstance(local_img.content, int):
            f.write(local_img.content)
        elif local_img.content == 403:
            pass


# 传入URL和name，启动图片下载
def process_thread(url, name):
    local_img.url = url
    local_img.name = name
    process_img()


# 使用多线程下载图片，因此步骤容易造成阻塞，影响脚本效率
def img_download(data_list):
    threads = []
    for data in data_list:
        # 添加新线程，通过target指定调用的函数，args传入参数，name指定线程名称，随后将线程对象添入threads列表
        t = threading.Thread(target=process_thread, args=(data['img_url'], data['name']), name=data['name'])
        threads.append(t)
    # 逐个启动线程
    for t in threads:
        t.start()
    # 等待各个线程终止
    for t in threads:
        t.join()


# 转为灰度图
def get_grayscale(image, resize_width=9, resize_heith=8):   #image为图片的路径，resize_width为缩放图片的宽度，resize_heith为缩放图片的高度
    im = Image.open(image)   #使用Image的open方法打开图片
    smaller_image = im.resize((resize_width,resize_heith))  #将图片进行缩放
    grayscale_image = smaller_image.convert('L')   #将图片灰度化
    return grayscale_image


# 计算dhash
def hash_calc(image,resize_width=9,resize_heith=8):
    hash_string = ""    #定义空字符串的变量，用于后续构造比较后的字符串
    pixels = list(get_grayscale(image,resize_width,resize_heith).getdata())
    # 上一个函数get_grayscale()缩放图片并返回灰度化图片，.getdata()方法可以获得每个像素的灰度值，使用内置函数list()将获得的灰度值序列化
    for row in range(1,len(pixels)+1): #获取pixels元素个数，从1开始遍历
        if row % resize_width :  #因不同行之间的灰度值不进行比较，当与宽度的余数为0时，即表示当前位置为行首位，我们不进行比较
            if pixels[row-1] > pixels[row]: #当前位置非行首位时，我们拿前一位数值与当前位进行比较
                hash_string += '1'   #当为真时，构造字符串为1
            else:
                hash_string += '0'   #否则，构造字符串为0
          #最后可得出由0、1组64位数字字符串，可视为图像的指纹
    print('原始hash: %s\n二进制转十进制: %s\n' % (hash_string, int(hash_string, 2)))
    return hash_string


# 更新数据库，写入dhash信息
def update_db(db_file, data_list):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    for i in data_list:
        sql = 'UPDATE skins SET dhash="%s" WHERE title="%s"' % (i['dhash'], i['name'])
        cursor.execute(sql)
        conn.commit()
    conn.commit()
    conn.close()


# 主函数
def main():
    time0 = time.time()
    db_file = 'scrapy.db'
    data_list = get_data_from_db(db_file)
    time1 = time.time()
    img_download(data_list)
    time2 = time.time()
    new_list = []
    for i in data_list:
        try:
            dhash = hash_calc('%s.png' % (i['name']))
        except OSError:
            dhash = 'Not Found'

        hash_data = {
            'name': i['name'],
            'dhash': dhash,
        }
        new_list.append(hash_data)
    update_db(db_file, new_list)
    time3 = time.time()
    for i in data_list:
        try:
            os.remove('%s.png' % (i['name']))
        except FileNotFoundError:
            pass
    time4 = time.time()
    time_msg = '[时间统计]\n总用时%ss\n读取DB数据%ss，下载图片%ss，计算更新%ss，清理文件%ss' % (time4-time0, time1-time0, time2-time1, time3-time2, time4-time3)
    print(time_msg)


# 循环执行
if __name__ == '__main__':
    while True:
        main()
