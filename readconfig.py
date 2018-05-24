class config():
    
    def __init__(self):
        self.config_dict = {}
        self.cfgfilename = 'config.txt'
        
    def open(self):
        with open(self.cfgfilename, 'r') as temp:
            for x in temp:
                x = x.split(' ')
                self.config_dict[x[0]] = x[1]
                
if __name__ == '__main__':
    cfg = config()
    cfg.open()
    print(cfg.config_dict)
