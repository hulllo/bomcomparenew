import requests
import re
import logging

def get_desc(part_no = 'AMN0000110CX'):
    '''
    part_no = Part Number
    '''
    payload = {'globalSearchTextBox':'true', 
                'currentPage':'search', 
                'fireSearch':'true', 
                'search_keyword':part_no, 
                'keywordkeywordField_SearchTextBox':part_no, 
                'preSelectionItems':'wt.part.WTPart,wt.doc.WTDocument,WCTYPE|wt.epm.EPMDocument|com.tclcom.DefaultEPMDocument,wt.change2.WTChangeIssue,wt.change2.WTChangeRequest2,wt.change2.WTChangeOrder2,wt.fc.Persistable', 
                'searchType':'wt.part.WTPart,wt.doc.WTDocument,WCTYPE|wt.epm.EPMDocument|com.tclcom.DefaultEPMDocument,wt.change2.WTChangeIssue,wt.change2.WTChangeRequest2,wt.change2.WTChangeOrder2'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36','Authorization':'Basic eXVjaHVhbi5wYW46dGNsQDEyMzQ='}
    r = requests.post('http://plm.tclcom.com/Windchill/wtcore/jsp/com/ptc/windchill/search/Search.jsp',data=payload, headers=headers)
    if r.status_code == 200:
        l = re.findall('"comparable":"'+part_no+'"(.+?)infoPageAction', r.text)
        if l == []:
            logging.warn(part_no,'未在PLM上找到')
            return 'None'
        name = re.findall('"name":"(.+)",', l[0])
    #    print(part_no, name[0])
        return name[0]
    else:
#        print('website connect fail,error code is',r.status_code)
        logging.warn('网站连接失败')
        return '网站连接失败'
if __name__ == '__main__':
    get_desc('SIT001_96_PT')
