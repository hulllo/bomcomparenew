import dataformat
import db
from readconfig import config
import re
import logging
logging.basicConfig( level=logging.WARN)
#logging.basicConfig(filename = 'log.txt', level=logging.WARN)


def isRLC(name):
    for a in ['电阻', '电容', '电感']:
        if a in name:
            return True
        else:
            return False

def cp(datalist0):
    result_list = []
    device = db.Device_database('test.db')
    for a in datalist0:
        match = 1
        for ref in reflist:  #只对比指定位号
            if re.match(r'\D+{0}\d\d'.format(ref),a[1]):
                match = 1
                break
            else:
                match = 0
        if a[2] in exclusive or match == 0 :
            continue
        
        elif dataformat.isRLC(a[5]):  #对RLC进行对比
            value = device.read_part('temp', 'value', 'ref', a[1])
#            print(a)
            
#            print(value, a[-1])

            if value == '' and a[-1].lower() == 'nc':
                continue
            if value == '0' and a[-1].lower() == '0r':
                continue
            elif value == '':
                value = 'nc'
            decal = device.read_part('temp', 'decal', 'ref', a[1])
            if value == a[-1].lower() and decal == a[-2]:
                 continue
            else:
                logging.warn('wrong:\n SCH is :{0}\n BOM is : {1},{2},{3}\n'.format(a[1:], a[1], value, decal))
                result_list.append('wrong:\n SCH is :{0}\n BOM is : {1},{2}\n'.format(a, decal, value))
        else:
            value = device.read_part('temp', 'value', 'ref', a[1])
            if value == '' and a[3].lower() == 'nc':
                continue
            part_num = device.read_part('temp', 'Part_Number', 'ref', a[1])
            if part_num != a[2]:
                logging.warn('wrong:\n SCH is :{0}\n BOM is : {1},{2}\n'.format(a, part_num, device.read_part('temp', 'description', 'ref', a[1])))
                result_list.append('wrong:\n SCH is :{0}\n BOM is : {1},{2}\n'.format(a, part_num, device.read_part('temp', 'description', 'ref', a[1])))
    return result_list

def main():
#    device = db.Device_database()

    global cfg, reflist, exclusive
    reflist = ['41', '42', '43', '44']
    exclusive = []
    cfg = config()
    cfg.open()
    datalist0, result_list = dataformat.main()
    result_list_cp = cp(datalist0)
    result = result_list + result_list_cp
    with open ('result.txt', 'w') as resultfile:
        for x in result:
            resultfile.write(x+'\n')



if __name__ == '__main__':
    main()
