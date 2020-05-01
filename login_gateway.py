#! usr/bin/python3

'''
python script to login to router automatically
@authors = zznnixt, sunieltmg
for educational purpose only
Do not use for unethical purposes
'''

import requests, bs4, re, time, sys, subprocess

def connectToWifi():
    comSpec = subprocess.Popen('netsh wlan connect name=STW_CU', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(15)
    return comSpec.stdout.read() if comSpec.stdout.read() else comSpec.stderr.read()

def login():
    with requests.Session() as s:
        global loginTime
        global getUrl
        # firstCookies = {'username': '1@local'}
        r = s.get('http://www.msftconnecttest.com/redirect')
        print(r.url)

        returnUrl = re.findall(r'ReturnUrl=(.*)', r.url)[0]
        # print(returnUrl)
        payload0 = {'ReturnUrl': returnUrl}
        r = s.get('http://gateway.example.com/no_cookie_loginpages/dns_post.shtml',
                        # cookies=firstCookies,
                        params=payload0)
        r.raise_for_status()

        secondCookies = {'password': 'MQ==', 'username': '1@local'}
        r = s.get('http://gateway.example.com/loginpages/login.shtml',
                    cookies=secondCookies,
                    params=payload0)
        r.raise_for_status()

        creds = {'username': '@user',
                    'password': '****',
                    'accesscode': '',
                    'vlan_id': '106'}

        r = s.post('http://gateway.example.com/loginpages/userlogin.shtml',
                    # headers={'Referer': 'http://gateway.example.com/loginpages/login.shtml?ReturnUrl=' + returnUrl},
                    # cookies=finalCookies,
                    data=creds)
        r.raise_for_status()
        print(s.cookies)

        getUrl = r.url
        print(f'long Post url is : {getUrl}')
        customUrl = re.findall(r'/?next=(.+)&uid.*&se_enc=(.+)&ip=(.+)&umac=(.+?)&.*&loginvalue=(.+?)&', getUrl)[0]

        nextUrl, seEnc, loginValue = customUrl[0], customUrl[1], customUrl[4]

        localIp, macAddr = customUrl[2], customUrl[3]

        # paramsTuple = re.findall(regexGen(17), getUrl)[0]
        # deviceInfo = dict(zip([k for k in paramsTuple if paramsTuple.index(k) % 2 == 0], [v for v in paramsTuple if paramsTuple.index(v) % 2 != 0]))

        deviceInfo = {
                    'next': nextUrl,
                    'uid': '1%40local',
                    'original_uid': '1',
                    'utype': 'LOCAL',
                    'se_enc': seEnc,
                    'ip': localIp,
                    'umac': macAddr,
                    'sessionlength': '0',
                    'byteamount': '0',
                    'chargetype': 'TIME',
                    'idletimeout': '7200',
                    'interim': '0',
                    'custom': '',
                    'roomState': '',
                    'loginvalue': loginValue,
                    'initplm': '',
                    'key': 'L',
                    'split_tunnel': '0'
                     }
        r = s.get('http://gateway.example.com/loginpages/popup1.shtml',
                    params=deviceInfo)
        r.raise_for_status()
        # print(r.content)

        soup = bs4.BeautifulSoup(r.content, 'lxml')
        selectScript = str(soup.find('script'))
        onlineUsers = re.findall(r'online_users.*;', selectScript)[0]
        loginTime = re.findall(r'loginvalue = "(.*)"', selectScript)[0]

        print(onlineUsers)
        print(loginTime)

        return sessionId

def logout(sessionId):
    with requests.Session() as s:
        # uncomment below line if using with login
        loginTime = time.time() + 50

        finalCookies = {'password': 'MQ==',
                        'Session': sessionId,
                        'username': '1@local'}

        r = s.get('http://gateway.example.com/loginpages/logoff.shtml',
                    params={'uid': '1@local'},
                    cookies=finalCookies,
                    # headers={'Referer': getUrl},
                    allow_redirects=False)

        redirectUrl = r.headers.get('Location')
        print(r.headers.get('Location'))
        try:
            localIp = re.findall(r'gwip=(.+?)&', redirectUrl)[0]
            print(localIp)
        except Exception as e:
            print(f'error was {e}')

        logoutParams = {'uid': '1@local',
                        'original_uid': '1',
                        'vidx': '6',
                        'vlanid': '106',
                        'gwip': localIp,
                        'used_time' : time.time() - int(loginTime)
                        }
        r = s.get('http://gateway.example.com/loginpages/logout_redirect.shtml',
                    params=logoutParams,
                    cookies=finalCookies)

        print(r.status_code)
        print(r.content)

    return 'Logged out'

sessId = login()

input()
