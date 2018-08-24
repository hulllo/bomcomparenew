import csv
import re
import get_description
from db import Device_database
from readconfig import config
import logging
import os


def handle(list_):
    '''
    从本地或者PLM上获得导出bom的器件的描述
    输入：
    list_ - list - 单个器件格式化后的list
    输出：
    desc_ - str - 获得的描述
    name - str - 器件名字（类型）
    decal - str - 器件的封装
    value - str - 器件的值，RLC为实际值，非RLC为''
    '''
    # 在本地数据库查询
    desc_ = readfromdb(list_[2])  # 根据编码从本地数据库上查询
    if desc_ != '':
        logging.info('{0} 本地数据库获取成功'.format(list_[2],))
        pass

    # 在PLM上查询
    else:

        # 根据配置在PLM上查询
        if cfg.config_dict['search_from_PLM'] == '1':
            logging.info('{0} 本地数据库上未找到，在PLM上查找'.format(list_[2]))
            desc_ = get_description.get_desc(list_[2])  # 本在PLM上获得器件的描述
            logging.debug('{0} {1}'.format(list_[2], desc_))
            logging.debug('{0} PLM: {1}'.format(list_[2], desc_))

            # 处理查询异常
            if desc_ == 'None':
                desc_ = name = decal = value = '未在PLM上找到'
                return desc_, name, decal, value
            elif desc_ == '网站连接失败':
                desc_ = name = decal = value = '网站连接失败'
                return desc_, name, decal, value
            # 处理查询正常
            else:
                logging.debug('{0} get from PLM'.format(list_[2]))

                # 根据配置不存储PLM数据到本地
                if cfg.config_dict['save_to_db'] != '1':
                    logging.info('不存储{0}到本地数据库中'.format(list_[2]))

                # 根据配置存储PLM数据到本地
                else:
                    logging.info('存储{0}到本地数据库中'.format(list_[2]))
                    writetodb(list_[2], desc_)
                    part_readed = readfromdb(list_[2])

                    # 处理数据库是否储存成功
                    if part_readed == desc_:
                        logging.info('***存储成功***\n')
                    else:
                        input('存储失败\n数据库：{0}\nPLM：{1}'.format(
                            part_readed[0][0], desc_))

        # 根据配置不在PLM上查询
        else:
            desc_ = name = decal = value = 'None'
            return desc_, name, decal, value

    # 格式化获取的数据
    name, decal = getdecal_name(desc_)  # 获取器件的名字（类型）、封装
    if isRLC(name):
        value = getRLCvalue(list_[3], decal, desc_)  # 获得RLC的Value
    else:
        value = ''

    return desc_, name, decal, value


def getRLCvalue(value, decal, description):
    '''
    获取RLC的值，如果导出的BOM存在value，以该value为准，否则以获取的为准
    输入:
    value - str - 导出BOM的器件的Value
    decal - str - 获取的器件封装
    description - str - 获取的器件描述

    输出：
    value - str - 器件的最终value
    '''
    # 如果导出的BOM存在value，以该value为准，否则以获取的为准
    if value == '':  # value1是否存在
        value = getvaluefromdesc(description)  # 从desc提取出值
    else:
        value = formatvalue(value, decal)  # 格式化value

    return value


def formatvalue(value, decal):
    '''
    格式化value，判断获取的封装是否与导出Value中的封装相同，以导出封装为准
    输入：
    value - str - 原理图导出的值
    decal - str - PLM上获取的器件封装
    输出：
    value - str - 格式化后的值
    decal - str - 修正后的器件封装    
    '''

    if value.lower() == 'nc':  # NC?
        return 'NC'  # 输出[值]
    else:
        pattern = re.compile(r'_\d+%')  # *_5%？
        match = pattern.search(value)
        if match:
            value = value.replace(match.group(), '')  # 除去后缀
        pattern = re.compile(r'_0\d0\d')  # *_0402、*_0201、*_0603？
        match = pattern.search(value)
        if match:
            decal1 = match.group().replace('_', '')
            value = value.replace(match.group(), '')
            if decal1 != decal:  # 判断获取的封装是否与导出的封装相同
                logging.error('value中的封装与PCB封装不符{0}'.format(
                    [value, decal, decal1]))  # 报错:value中的封装与PCB封装不符
                raise
        if value.lower == '0R':  # 0R -> 0ohm
            value = '0ohm'
        elif value == '0':  # 0 -> 0ohm
            value = '0ohm'
        else:
            value = value.replace(' ', '')  # 去空格
        return(value.replace('ohm', ''))  # 输出[值]


def getvaluefromdesc(description):
    '''
    获取RLC的值
    输入：
    description - str - RLC器件的描述 
    输出：
    value - str - RLC器件的值
    '''
    des_list = description.split(',')
    for a in des_list:
        m = re.search(r'(pf|nf|uf|ohm|nh|uh)', a.lower())
        if m:
            value = m.string.replace(' ', '')
#                print (a, value)
            return value.replace('ohm', '')
    value = ''
    return value


def getdecal_name(description):
    '''
    获取封装与名字
    输入：
    description - str - 器件的描述
    输出：
    name - str - 获取的名字
    decal - str - 获取的封装
    '''
    desc_split = description.split(',')
    name = desc_split[0]
    for a in desc_split:
        m = re.match(r'(0\d0\d)', a)
        if m == None:
            decal = 'None'
        else:
            decal = m.group()
            break
    return(name, decal)


def writetodb(Part_Number, description):  # 写入到db
    '''
    写入到test.db\device
    输入：
    Part_Number - str - 器件编码
    description -str - 器件描述
    '''
    newlist = ['', '', Part_Number, '', description, '', '']
    device = Device_database('test.db')
    device.writetotable('device', newlist)


def readfromdb(Part_Number):
    '''
    读取自test.db\device
    输入：
    Part_Number - str - 器件编码
    输出：
    result - str - 器件的description
    '''

    device = Device_database('test.db')
    result = device.read_part('device', 'description',
                              'Part_Number', Part_Number)
#    print('found from db is', result)
    return result


def opendata0(name):
    '''
    格式化从原理图直接导出的BOM

    输入：
    name - str - 原理图直接导出的BOM文件名

    输出：
    datalist0 - list - 格式化后的BOM，['#', 'Ref Designator', 'Part Number', 'value1', 'Description']
    '''
    try:
        with open(name, 'r') as data0:
            csv_reader = csv.reader(data0)
            datalist0 = []
            search_ok = {}

            # a: ['#', 'Ref Designator', 'Part Number', 'value1', 'Description']
            for a in csv_reader:
                if a[0] == '#':
                    continue
                if a[2]in search_ok:
                    desc = search_ok[a[2]][0]
                    name = search_ok[a[2]][1]
                    decal = search_ok[a[2]][2]
                else:
                    result = handle(a)
                    desc = result[0]
                    name = result[1]
                    decal = result[2]
                    search_ok[a[2]] = [desc, name, decal]
                if isRLC(name):
                    value = getRLCvalue(a[3], decal, desc)
                else:
                    value = ''
                a[4] = desc
                a.append(name)
                a.append(decal)
                a.append(value)
    #            print(a)
                datalist0.append(a)
        return datalist0
    except FileNotFoundError as e:
        logging.error(e)
        return 'error'


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
            continue
        return False


def opendata1(name):
    '''
    格式化手工制作的BOM，并将格式化后的数据保存在数据库test.db/temp

    输入
    name - str - 格式化手工制作的BOM的文件名

    输出
    datalist1 - list - 格式化为列表的BOM  
    result_list - list - 手工制作的BOM存在的位号数量不一致及重复位号数量的汇总
    '''

    device = Device_database('test.db')
    device.drop_table('temp')
    device.create_table(
        'temp', '(Part_Number char, description char, name char, decal char, value char, ref primary key)')
    try:
        with open(name, 'r') as data1:
            csv_reader = csv.reader(data1)
            datalist1 = []
            ref_list = []
            ref_list1 = []
            result_list = []
            for a in csv_reader:

                pattern = re.compile(r'\D\d\d\d\d')  # 位号个数与数量一致？
                match = pattern.findall(a[7])
                if a[6] != str(len(match)) and a[6] != '' and a[6] != 'QTY':
                    logging.info('数量与位号个数不一致： \n{0} \n 数量是：{1}\n 位号个数是:{2}\n'.format(
                        a, a[6], len(match)))
                    result_list.append(
                        '数量与位号个数不一致： \n{0} \n 数量是：{1}\n 位号个数是:{2}\n'.format(a, a[6], len(match)))

                ref_list1 = a[7].split(',')
                ref_list = ref_list + ref_list1

                name, decal = getdecal_name(a[5])
                if isRLC(name):
                    value = getRLCvalue('', decal, a[5])
                else:
                    value = ''
                a.append(name)
                a.append(decal)
                a.append(value)
                if a[7] == '':
                    continue
                b = a[7].split(',')

                for x in b:

                    c = (a[1], a[5], a[-3], a[-2], a[-1], x)
                    datalist1.append(c)
    #        print(ref_list)
            d = {}
            for x in set(ref_list):
                if x == '':
                    continue
                count = ref_list.count(x)
                if count == 1:
                    continue
                d[x] = ref_list.count(x)
            if d == {}:
                logging.info('位号无重复\n')
                result_list.append('位号无重复\n'.format(d))
            else:
                for key in d:
                    logging.info('位号重复项：{0}，重复数量：{1}\n'.format(key, d[key]))
                    result_list.append(
                        '位号重复项：{0}，重复数量：{1}\n'.format(key, d[key]))
            device.writetotable_list3D('temp', datalist1)
        return datalist1, result_list
    except FileNotFoundError as e:
        logging.error(e)
        return 'error', 'error'


def main():
    global cfg
    cfg = config()
    cfg.open()
    # data0.csv 转为列表, data0 为原理图导出的BOM
    datalist0 = opendata0('data0.csv')

    # data1.csv 转为列表. data1 为制作的BOM
    datalist1, result_list = opendata1('data1.csv')
    return datalist0, result_list


if __name__ == '__main__':
    main()
