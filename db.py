import sqlite3
import logging
#import get_description

class Device_database():
    def __init__(self, dbname):
        self.dbname = dbname
        self.tbname = 'device'
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
        sql="SELECT count(*) FROM sqlite_master WHERE type='table' AND name='"+self.tbname+"'"
        cursor.execute(sql)
        b=cursor.fetchall()
        if b[0][0] == 1: 
            pass
#            print('table <{0}> exists'.format(self.tbname))
#            cursor.execute('drop table {0}'.format(self.tbname))
#            cursor.execute('create table {0} (ref_designer primary key)'.format(self.tbname)) 
        else:
            logging.info('{0} do not exists, create new one'.format(self.tbname))
            cursor.execute('create table {0} (Part_Number primary key, value1 char, description char, class char, decal char)'.format(self.tbname)) 
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()  
    def print_header(self, tbname):        
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info ({0})".format(tbname)) 
        b=cursor.fetchall()
#        cursor.close()
#        # 提交事务:
#        conn.commit()
#        # 关闭Connection:
#        conn.close()  
        logging.info('the table \'{0}\' header is:{1}'.format(tbname, b))
    def print_tables(self):
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
        cursor.execute('select name from sqlite_master where type = "table" order by name')
        b=cursor.fetchall()
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()  
        logging.info('The table is:{0}'.format(b))
    def print_all(self, tbname):
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
        cursor.execute('select * from {0}'.format(tbname))
        b=cursor.fetchall()
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()  
        logging.info('{0}'.format(b))    
    def drop_table(self, tbname):
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
        sql="SELECT count(*) FROM sqlite_master WHERE type='table' AND name='"+tbname+"'"
        cursor.execute(sql)
        b=cursor.fetchall()
        if b[0][0] == 1: 
            logging.info('table \'{0}\' exists,drop...'.format(tbname))
            cursor.execute('drop table {0}'.format(tbname))
            logging.info('drop table \'{0}\' succeful'.format(tbname))
        else:
            logging.info('table {0} do not exists'.format(tbname))
    def writetotable(self, tbname, list_all):   
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
        try:
            newlist = (tuple(list_all[2:]))
            cursor.execute("insert into {0} values {1}".format(tbname, newlist))
        except sqlite3.IntegrityError as e:
            logging.error(e)
        cursor.close()
        conn.commit()
        conn.close()  

    def read_part(self, tbname, target_, col, data_):
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
#        logging.info(target_, tbname, col, data_)
        cursor.execute("select {0} from {1} where {2} is '{3}'".format(target_, tbname, col, data_))
        b=cursor.fetchall()
#        cursor.close()
#        # 提交事务:
#        conn.commit()
#        # 关闭Connection:
#        conn.close() 
        if b == []:
            pass
#           logging.info('{0} 未在本地找到'.format(data_))
            return ''
        else:
            pass
#            logging.info('{0}'.format(b)) 
        return b[0][0]
    def del_part(self, col, data_):
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
        cursor.execute("delete from {0} where {1} is '{2}'".format(self.tbname, col, data_))
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()  
    def create_table(self, table_name, tuple_):    
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
        cursor.execute('create table {0} {1}'.format(table_name, tuple_))
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close() 
    def writetotable_list3D(self, tbname, list3D):    
        conn = sqlite3.connect(self.dbname)
        cursor = conn.cursor()
        for a in list3D:
            try:
                cursor.execute("insert into {0} values {1}".format(tbname, a))
            except sqlite3.IntegrityError as e:
                logging.error('\n{0}\n{1}\n'.format(e, a))
        cursor.close()
        conn.commit()
        conn.close() 
if __name__ == '__main__':
    
    device = Device_database('test.db')
    device.print_tables()
    device.print_header('temp')
#    device.print_all('temp')
    # datalist0 = main.opendata0('data0.csv')
    
    print(device.read_part('device','description','Part_Number', 'AEA0000370CX'))
#    device.del_part('Part_Number', 'ACA27HBAC0CX')
#    device.drop_table('temp')
#    device.create_table('temp', ('Part_Number primary key', 'desc char', 'name char', 'decal char', 'value char', 'ref char'))
#    device.writetotable('temp', ('','','ACA56HHA02CX','电感,Inductor,5.6 nH,±3 %,DCR=0.88 ohm,250 mA,0201,Film,0.63×0.33×0.33 mm,LQP03TG5N6H02D,MURATA', '电感', '0201', '5.6nh', 'L4261,L4442'))
