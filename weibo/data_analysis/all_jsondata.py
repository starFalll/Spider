from weibo.data_analysis.Data_analysis import main as datamain
from weibo.data_analysis.LDA_Analysis import main as ldamain
from weibo.Connect_mysql import Connect
import json
import sys



def main():
    if (len(sys.argv) == 2):
        uid = sys.argv[1]
    else:
        conf, _ = Connect('../conf.yaml')
        uids = conf.get('uids')
        uid = list(uids.values())[0]
    result = {}
    result['first_data'] = datamain(uid)
    result['second_data'] = ldamain(uid)
    print('<%' + json.dumps(result) + '%>')
    with open('~/spider/' + str(uid), 'w') as f:
        f.write('100')
if __name__ == '__main__':
    main()
