import logging
import os
import re

import dataformat
import db
import log_
from readconfig import config


def isRLC(name):
    '''
    判断是否RLC
    输入
    name - str - 器件的描述
    输出
    True/False - 是否RLC
    '''

    for a in ['电阻', '电容', '电感']:
        if a in name:
            return True
        else:
            return False


def cp(datalist0):
    '''
    对比导出的BOM与制作的BOM
    输入
    datalist0 - list - 导出的BOM格式化后的list
    输出
    result_list - list - 输出结果
    '''
    result_list = []
    device = db.Device_database('test.db')

    #遍历对比
    for a in datalist0:

        #判断是否指定的位号
        match = 1
        for ref in reflist:  # 只对比指定位号
            if ref == 'all':
                match = 1
                break
            elif re.match(r'\D+{0}\d\d'.format(ref), a[1]):
                match = 1
                break
            else:
                match = 0
        if a[2] in exclusive or match == 0:
            continue

        #对RLC进行对比
        elif dataformat.isRLC(a[5]):  
            value = device.read_part('temp', 'value', 'ref', a[1]) #获取制作bom某个器件的value
            #'temp'数据的格式为
            #'(Part_Number char, description char, name char, decal char, value char, ref primary key)')

            #格式化部分值
            if value == '' and a[-1].lower() == 'nc':
                continue
            if value == '0' and a[-1].lower() == '0r':
                continue
            elif value == '':
                value = 'nc'

            decal = device.read_part('temp', 'decal', 'ref', a[1]) #获取制作bom某个器件的decal

            #对比value与decal
            if value == a[-1].lower() and decal == a[-2]:
                continue
            else:
                logging.info('difference:\n SCH is :{0}\n BOM is : {1},{2},{3}\n'.format(
                    a[1:], a[1], value, decal))
                result_list.append(
                    'difference:\n SCH is :{0}\n BOM is : {1},{2}\n'.format(a, decal, value))

        #对RLC外的器件进行对比            
        else:
            value = device.read_part('temp', 'value', 'ref', a[1])  #获取制作bom某个器件的value

            #对比value与decal
            if value == '' and a[3].lower() == 'nc':
                continue
            part_num = device.read_part('temp', 'Part_Number', 'ref', a[1])
            if part_num != a[2]:
                logging.info('difference:\n SCH is :{0}\n BOM is : {1},{2}\n'.format(
                    a, part_num, device.read_part('temp', 'description', 'ref', a[1])))
                result_list.append('difference:\n SCH is :{0}\n BOM is : {1},{2}\n'.format(
                    a, part_num, device.read_part('temp', 'description', 'ref', a[1])))

    return result_list


def main():
    #    device = db.Device_database()
    print('''
    BOM 对比工具使用说明：
    输入文件：
        1. data0.csv：原理图导出的BOM
        2. data1.csv: 手工制作的BOM
        3. config.txt： 配置文件
    输出文件：
        1. log.txt： log文件
        2. result.txt： 对比结果 
    Enter继续...
    ''')
    input()
    global cfg, reflist, exclusive
    exclusive = []

    # 载入配置文件
    cfg = config()
    cfg.open()
    reflist = cfg.config_dict['reflist']

    # 按配置处理图页
    input('当前处理的图页：{0}'.format(reflist))
    if cfg.read_mark == 'error':
        return
    
    #格式化csv文件
    datalist0, result_list = dataformat.main()
    if datalist0 == 'error' or result_list == 'error':
        return
    
    #对比输出的BOM与制作的BOM
    result_list_cp = cp(datalist0)
    result = result_list + result_list_cp

    #将对比结构保存在result.txt文件
    with open('result.txt', 'w') as resultfile:
        for x in result:
            resultfile.write(x+'\n')


if __name__ == '__main__':
    main()
    os.system('notepad result.txt')
    input('程序运行完毕，结果保存在result.txt，Enter退出...')
