import os
import sqlite3
from tkinter import filedialog
from PIL import Image
import requests

# 选择数据库（暂时弃用）
def select_file():
    file = filedialog.askopenfilename(filetype=[("数据库文件", "*.db")])
    return file

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

# 通过URL下载图片到本地
def img_download(data_list):
    for data in data_list:
        img_content = get_content(data['img_url'])
        with open('%s.png' % data['name'], 'wb') as f:
            if not isinstance(img_content, int):
                f.write(img_content)
            elif img_content == 403:
                pass

# 转为灰度图
def get_grayscale(image,resize_width=9,resize_heith=8):   #image为图片的路径，resize_width为缩放图片的宽度，resize_heith为缩放图片的高度
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
    db_file = 'scrapy.db'
    data_list = get_data_from_db(db_file)
    img_download(data_list)
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
    for i in data_list:
        try:
            os.remove('%s.png' % (i['name']))
        except FileNotFoundError:
            pass

# 循环执行
if __name__ == '__main__':
    while True:
        main()