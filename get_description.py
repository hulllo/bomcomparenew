import requests
import re
import logging
# logging.basicConfig(level=logging.INFO)


def get_desc(part_no):
    '''
    从PLM获取器件description
    输入：
    part_no - str - 器件编码
    输出：
    str - 器件Description、None、网站连接失败
    '''
    payload = {'globalSearchTextBox': 'true',
               'currentPage': 'search',
               'fireSearch': 'true',
               'search_keyword': part_no,
               'keywordkeywordField_SearchTextBox': part_no,
               'preSelectionItems': 'wt.part.WTPart,wt.doc.WTDocument,WCTYPE|wt.epm.EPMDocument|com.tclcom.DefaultEPMDocument,wt.change2.WTChangeIssue,wt.change2.WTChangeRequest2,wt.change2.WTChangeOrder2,wt.fc.Persistable',
               'searchType': 'wt.part.WTPart,wt.doc.WTDocument,WCTYPE|wt.epm.EPMDocument|com.tclcom.DefaultEPMDocument,wt.change2.WTChangeIssue,wt.change2.WTChangeRequest2,wt.change2.WTChangeOrder2'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
               'Authorization': 'Basic eXVjaHVhbi5wYW46dGNsQDEyMzQ='}
    try:
        r = requests.post(
            'http://plm.tclcom.com/Windchill/wtcore/jsp/com/ptc/windchill/search/Search.jsp', data=payload, headers=headers)
    except Exception as e:
        logging.error('连接网站失败{0}'.format(e))
        return '网站连接失败'
    if r.status_code == 200:
        l = re.findall('"comparable":"'+part_no+'"(.+?)infoPageAction', r.text)
        if l == []:
            logging.warning('{0} 未在PLM上找到'.format(part_no))
            input('按Enter继续...')
            return 'None'
        name = re.findall('"name":"(.+)",', l[0])
        logging.info('在线查找成功: {0} ->\n {1}'.format(part_no, name[0]))
        return name[0]
    else:
        #        print('website connect fail,error code is',r.status_code)
        logging.error('网站连接失败')
        return '网站连接失败'


if __name__ == '__main__':
    get_desc('AMN0000110CX')
