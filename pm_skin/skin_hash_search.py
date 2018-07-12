from tkinter import filedialog
import sqlite3
from PIL import Image


# 通过文件选择器选择文件
def select_file():
    file = filedialog.askopenfilename(filetypes=[("PNG图片", "*.png")])
    return file


def grayscale_Image(image,resize_width=9,resize_heith=8):   #image为图片的路径，resize_width为缩放图片的宽度，resize_heith为缩放图片的高度
    im = Image.open(image)   #使用Image的open方法打开图片
    smaller_image = im.resize((resize_width,resize_heith))  #将图片进行缩放
    grayscale_image = smaller_image.convert('L')   #将图片灰度化
    return grayscale_image


def get_dhash(image,resize_width=9,resize_heith=8):
    hash_string = ""    #定义空字符串的变量，用于后续构造比较后的字符串
    pixels = list(grayscale_Image(image,resize_width,resize_heith).getdata())
    # 上一个函数grayscale_Image()缩放图片并返回灰度化图片，.getdata()方法可以获得每个像素的灰度值，使用内置函数list()将获得的灰度值序列化
    for row in range(1,len(pixels)+1): #获取pixels元素个数，从1开始遍历
        if row % resize_width :  #因不同行之间的灰度值不进行比较，当与宽度的余数为0时，即表示当前位置为行首位，我们不进行比较
            if pixels[row-1] > pixels[row]: #当前位置非行首位时，我们拿前一位数值与当前位进行比较
                hash_string += '1'   #当为真时，构造字符串为1
            else:
                hash_string += '0'   #否则，构造字符串为0
          #最后可得出由0、1组64位数字字符串，可视为图像的指纹
    print('原始hash: %s\n二进制转十进制: %s\n' % (hash_string, int(hash_string, 2)))
    return hash_string


def search_db(dhash):
    db_file = 'scrapy.db'
    conn = sqlite3.connect(db_file)
    sql = "SELECT title,author,date,raw_url FROM skins WHERE dhash='%s'" % dhash
    print('[执行SQL指令] ',sql)
    cursor = conn.execute(sql)

    result_num = 0
    result_list = []
    for row in cursor:
        result_list.append(row)
        result_num += 1
    conn.close()
    print('搜索完毕，共找到%s条记录。\n'%result_num)
    if len(result_list)>0:
        for i in result_list:
            print(i)


def main():
    skin_file = select_file()
    dhash = get_dhash(skin_file)
    search_db(dhash)


if __name__ == '__main__':
    main()