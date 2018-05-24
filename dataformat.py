import csv
import re
import get_description
from db import Device_database
from readconfig import config
import logging

def handle(list_):
    desc_ = readfromdb(list_[2])    #根据编码从本地数据库上查询
    if desc_ != '':
        logging.info('{0} get from local database'.format(list_[2],))
        pass

    else:
#        print(cfg.config_dict['search_from_PLM'].replace('\n', ''), '1', cfg.config_dict['search_from_PLM'].replace('\n', '') == '1')
        if cfg.config_dict['search_from_PLM'].replace('\n', '') == '1':
            logging.warn('\n{0} 本地数据库上未找到，在PLM上查找\n'.format(list_[2]))
            desc_ = get_description.get_desc(list_[2])  #本地数据库上未找到，在PLM上查找
            logging.info('{0} {1}'.format(list_[2], desc_))
            logging.info('{0} PLM: {1}'.format(list_[2], desc_))
            if desc_ == 'None':
                return 'None'
            elif desc_ == '网站连接失败':
                return '网站连接失败'
            else:
                logging.info(list_[2],'get from PLM')
                  #存储PLM数据到本地
                if cfg.config_dict['save_to_db'] != '1':
                    logging.info('不存储{0}到本地数据库中'.format(list_[2]))
                else:
                    logging.info('存储{0}到本地数据库中'.format(list_[2]))
                    writetodb(list_[2], desc_)
                    part_readed = readfromdb(list_[2])
                    if part_readed == desc_:
                        logging.info('存储成功')
                    else:
                        input('存储失败\n数据库：{0}\nPLM：{1}'.format(part_readed[0][0], desc_))
        else:
            return 'None'
    name, decal = getdecal_name(desc_)
    if isRLC(name):
        value = getRLCvalue(list_[3], decal, desc_)
    else:
        value = ''
    return desc_, name, decal, value

def getRLCvalue(value, decal, description):
    if value == '':   #value1是否存在
        value = getvaluefromdesc(description) #从desc提取出值
    else:
        value, decal = formatvalue(value, description, decal)  #格式化value
    return value

def formatvalue(value, description, decal):
    if value.lower() == 'nc':            #NC?
        return ['NC', decal]          #输出[值，封装]
    else:
        pattern = re.compile(r'_\d+%')     #*_5%？
        match = pattern.search(value)
        if match:
           value = value.replace(match.group(), '')     #除去后缀
        pattern = re.compile(r'_0\d0\d')  #*_0402、*_0201、*_0603？
        match = pattern.search(value)
        if match:
            decal1 = match.group().replace('_', '')
            value = value.replace(match.group(), '')
            if decal1 != decal:              #判断封装是否符合PCB
                return([value, decal, decal1])#报错:value中的封装与PCB封装不符
        if value.lower == '0R':     #0R -> 0ohm
            value = '0ohm'
        elif value == '0':       #0 -> 0ohm
            value = '0ohm'
        else:
            value = value.replace(' ', '')     #去空格
        return(value.replace('ohm', ''), decal)     #输出[值，封装]

def getvaluefromdesc(description):
        des_list = description.split(',')
        for a in des_list:
            m = re.search(r'(pf|nf|uf|ohm|nh|uh)',a.lower())
            if m:
                value = m.string.replace(' ', '')
#                print (a, value)
                return value.replace('ohm', '')
        value = ''
        return value
def getdecal_name(description):

    desc_split = description.split(',')
    name = desc_split[0]
    for a in desc_split:
        m = re.match(r'(0\d0\d)',a)
        if m == None :
            decal = 'None'
        else:
            decal = m.group()
            break
    return(name, decal)

def writetodb(Part_Number, description):   #写入到db
    newlist = ['', '', Part_Number, '', description, '', '']
    device = Device_database('test.db')
    device.writetotable('device', newlist)


def readfromdb(Part_Number):
    device = Device_database('test.db')
    result = device.read_part('device','description','Part_Number', Part_Number)
#    print('found from db is', result)
    return result

def opendata0(name):
    with open(name, 'r') as data0:
        csv_reader = csv.reader(data0)
        datalist0 = []
        search_ok = {}
        for a in csv_reader:     # a: ['#', 'Ref Designator', 'Part Number', 'value1', 'Description']
            if a[0] == '#':
                continue
            if a[2]in search_ok:
                desc = search_ok[a[2]][0]
                name = search_ok[a[2]][1]
                decal = search_ok[a[2]][2]
            else:
                result = handle(a)
                if result == 'None':
                    desc = 'None'
                    name = 'None'
                    decal = 'None'
                elif result == '网站连接失败':
                    desc = 'None'
                    name = 'None'
                    decal = '网络连接错误，需手动核对'
                else:
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

def isRLC(name):
    for a in ['电阻', '电容', '电感']:
        if a in name:
            return True
        else:
            continue
        return False


def opendata1(name):
    device = Device_database('test.db')
    device.drop_table('temp')
    device.create_table('temp', '(Part_Number char, description char, name char, decal char, value char, ref primary key)')
    with open(name, 'r') as data1:
        csv_reader = csv.reader(data1)
        datalist1 = []
        ref_list = []
        ref_list1 = []
        result_list = []
        for a in csv_reader:

            pattern = re.compile(r'\D\d\d\d\d')    #位号个数与数量一致？
            match = pattern.findall(a[7])
            if a[6]!=str(len(match)) and a[6] != '' and a[6] != 'QTY':
                logging.warn('数量与位号个数不一致： \n{0} \n 数量是：{1}\n 位号个数是:{2}\n'.format(a, a[6], len(match)))
                result_list.append('数量与位号个数不一致： \n{0} \n 数量是：{1}\n 位号个数是:{2}\n'.format(a, a[6], len(match)))

            ref_list1=a[7].split(',')
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
            logging.info ('位号重复项：{0}\n'.format(d))

            result_list.append('位号重复项：{0}\n'.format(d))
        device.writetotable_list3D('temp', datalist1)
    return datalist1, result_list

def main():
    global cfg
    cfg = config()
    cfg.open()
    datalist0 = opendata0('data0.csv')   #data0.csv 转为列表
#    print(datalist0)
    datalist1, result_list = opendata1('data1.csv')   #data1.csv 转为列表.
#    print(datalist1)
#    print(result_list)
    return datalist0, result_list

if __name__ == '__main__':
    main()
