import requests 
import json
import time
import datetime
import sys 
import csv

test_ID = ''
# some comment 
def checkStatus(testID, test_type):
    print('Check status...')
    status = ''
    i = 0
    while status != 'Test Complete':
        response = requests.request('GET', 'https://www.webpagetest.org/testStatus.php?f=json&test=' + str(testID)).json()
        status = response['statusText']
        time.sleep(30)
        i += 1
        # create time stamp
        ts = int(time.time())
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(time_stamp + ' ' + test_type + ' current status = ' + status)
        # if i>30:
        #     print('ERROR: Time over')
        #     break

def get_data_json(url):
    response = requests.request('GET', url).json()
    return response

def make_request(test_type, runs):
    # read config file
    with open('config.json') as f:
        conf = json.load(f)

    wpt_url = conf['wpt_url'] # 'https://www.webpagetest.org/runtest.php'
    test_url = conf['test_url'] # 'https://inhabitat.com/'
    api_key = conf['api_key'] # 'A.6a8cbf35982bf7e08b81a8e3257f0938'
    location = conf['location'] # 'Dulles.Native'
    priority = conf['priority'] # 0
    block = conf['block'] # '%2Fjs%2Fad.min.js%20hb-lite.min.js%20%2Fht%2Fhtw-ib-inhabitat.js%20apstag.js%20integrator.js%20s.mnet-ad.net%20securepubads%20googlesyndication'
    script_unity = conf['script_unity'] # 'setDns%20inhabitat.com%2052.6.144.109%0AsetCookie%20https%3A%2F%2Finhabitat.com%20apsid%3D1542414095244547%0AsetCookie%20https%3A%2F%2Finhabitat.com%20apsct%3De947314d0fed7e3cd2634a1469861142%0AsetCookie%20https%3A%2F%2Finhabitat.com%20apss%3Dd%0AsetCookie%20https%3A%2F%2Finhabitat.com%20apadb%3D4%0Anavigate%20https%3A%2F%2Finhabitat.com'
    script_unity_blocked = conf['script_unity_blocked']

    base = '&k='+api_key+'&location='+location+'&f=json&runs='+str(runs)+'&priority='+str(priority)+'&test=1'

    if test_type == 'original':
        payload = wpt_url + '?url=' + test_url + base

    if test_type == 'original_block':
        payload = wpt_url + '?url=' + test_url + base + '&block=' + block
        
    if test_type == 'unity':
        payload = wpt_url + '?script=' + script_unity + base + '&ignoreSSL=1'

    if test_type == 'unity_block':
        payload = wpt_url + '?script=' + script_unity_blocked + base + '&ignoreSSL=1' + '&block=' + block

    # make request - run tests
    r = requests.request('GET', payload).json()
    # wait status - Complete
    test_ID = r['data']['testId']
    checkStatus(test_ID, test_type)
    # return url for download json file with test data 
    return r['data']['jsonUrl']

def input_test_type():
    return input('''
====================================================================
| Provide num of Test type                                         |
| 1 - original, 2 - original_block, 3 - unity, 4 - unity_block     |
| ex. '1,2,3' = original, original_block, unity                    |
| or use 'all' to select '1,2,3,4'                                 |
====================================================================
>>> test type: ''')

def input_run_num():
    return input('''
====================================================================
| Provide num of Runs  min = 1, max = 9                            |
====================================================================
>>> test runs: ''')

def input_num_of_tests():
    return input('''
====================================================================
| Provide num of tests for run  min = 1, max = 11                  |
====================================================================
>>> test runs: ''')


def main():
    # === input
    test_index = str(input_test_type())
    if test_index != '1' and test_index != '2' and test_index != '3' and test_index != '4':
        if test_index == 'all':
            test_index = '1,2,3,4'
        test_index = test_index.split(',')
    else:
        temp_in = []
        temp_in.append(test_index)
        test_index = temp_in

    runs_num = int(input_run_num())
    test_run_number = int(input_num_of_tests())

    # === var
    json_file_list = []
    test_list = ['', 'original', 'original_block', 'unity', 'unity_block'] 

    # === loop number of tests ran
    for test_run_num in range(test_run_number): 
        # timestamp
        ts = int(time.time()) 
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(str(time_stamp) + ' ' + str(test_run_num + 1) + ' out of ' +  str(test_run_number) + ' test Run starts')

        # === loop for number of test types
        for num in test_index:
            # get data url
            data_url = make_request(test_list[int(num)], runs_num) # sdata_url = tring - url json result
            # get data json
            data = get_data_json(data_url)
            # create/rewrite json file with test type name
            file_name = test_list[int(num)]+'_data.json'
            # write data into json file
            with open(file_name, 'w') as outfile:  
                json.dump(data, outfile)
            json_file_list.append(file_name)

        # === create csv file and write data (from existing json files)
        if test_run_num == 0:
            csv_file_name = str(ts) +'_total.csv'
            with open(csv_file_name, 'w') as csv_file:
                 # write first line (header) in csv
                line = 'TestName,Time,ID,URL,Location,Connectivity,Runs,View,LoadTime,SpeedIndex,TTFB,FirstMeaningfulPaint,FirstTextPaint\n'
                csv_file.writelines(line) 
                csv_file.close # close file
        # parce json files and write data into csv line by line
        for f_name in json_file_list:
            # copy json file into var f
            with open(f_name) as json_file:  
                f = json.load(json_file)
            # create csv file
            with open(csv_file_name, 'a') as csv_file:
                
                View = ['firstView', 'repeatView']
                runs = list(range(1,runs_num+1))

                id = f['data']['id']
                url = f['data']['url']
                location = f['data']['location']
                connectivity = f['data']['connectivity']
                testName = f_name.replace('_data.json', '')
                
                for v in View:
                    for i in runs:
                        try:
                            loadTime = f['data']['runs'][str(i)][v]['loadTime']
                        except:
                            loadTime = 'n/a'
                            print('ERROR: loadTime = n/a')
                        try:
                            SpeedIndex = f['data']['runs'][str(i)][v]['SpeedIndex']
                        except:
                            SpeedIndex = 'n/a'
                            print('ERROR: SpeedIndex = n/a')
                        try:
                            TTFB = f['data']['runs'][str(i)][v]['TTFB']
                        except:
                            TTFB = 'n/a'
                            print('ERROR: TTFB = n/a')
                        try:
                            firstMeaningfulPaint = f['data']['runs'][str(i)][v]['firstMeaningfulPaint']
                        except:
                            firstMeaningfulPaint = 'n/a'
                            print('ERROR: firstMeaningfulPaint = n/a')
                        try:
                            firstTextPaint = f['data']['runs'][str(i)][v]['firstTextPaint']     
                        except:
                            firstTextPaint = 'n/a'
                            print('ERROR: firstTextPaint = n/a')

                        line = '{},{},{},{},{},{},{},{},{},{},{},{},{} \n'\
                            .format(testName, time_stamp, id, url, location, connectivity, i, v, loadTime, SpeedIndex, TTFB, firstMeaningfulPaint, firstTextPaint)
                        csv_file.writelines(line) 

    print('Done, enjoy!!!')





if __name__ == '__main__':
    main()
