import os
import logging
# logging.basicConfig(level=logging.INFO)
class config():
    
    def __init__(self):
        self.config_dict = {}
        self.read_mark = 'ok'
        self.cfgfilename = 'config.txt'
        self.reflist = []

    def open(self):
        self.read_mark = 'ok'
        try:
            with open(self.cfgfilename, 'r') as temp:
                for x in temp:  #遍历所有配置
                    x = x.split(' ')

                    #配置项为reflist，配置组成一个list
                    if x[0] == 'reflist': 
                        for v in x[1:]:
                            self.reflist.append(v.replace('\n', ''))
                        self.config_dict[x[0]] = self.reflist
                    
                    #配置项为非reflist    
                    else:                         
                        self.config_dict[x[0]] = x[1].replace('\n', '')
            logging.info('读取配置文件成功')
            logging.debug('读取的配置为：{0}'.format(self.config_dict))        
        
        #读取配置文件出错
        except Exception  as e:
            self.read_mark = 'error'
            logging.error('读取配置文件错误 {0}'.format(e))        

if __name__ == '__main__':
    cfg = config()
    cfg.open()
