import requests, bs4, re, time, sys, subprocess

def regexGen(nDictItems):
    # GET requests have params seperated by &
    return '\?' + '&'.join(['(.*?)=(.*?)' for i in range(nDictItems)]) + '&(.*?)=(.*)'
    # if the last key has value then .*? will ignore the value cuz it is not greedy and has found zero value
    # below can solve the above problem but the regex engine takes more time to process it
    # return '\?' + '&'.join(['(.*?)=(.*)' for i in range(nDictItems + 1)])

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
        # print(r.content) # tickbox privacy accept html

        # print(s.cookies)
        # print(r.cookies)
        # print(r.status_code)
        '''
        <SCRIPT type="text/javascript">
        var disclaimer_login_url = "http://gateway.example.com/loginpages/login.shtml?ReturnUrl=IS/JsU7gnDvVvVqxlUuRsQu1mTeNbV/JdUvImQu1lDvBdR-dqROFs053";
        </SCRIPT>
        ''' # has this? YEAHHHH

        # varCookies = s.cookies
        # varCookies.set('password', 'MQ==') # MQ%3D??? , domain,path=??
        # varCookies.set('username', '1@local')
        secondCookies = {'password': 'MQ==', 'username': '1@local'}
        r = s.get('http://gateway.example.com/loginpages/login.shtml',
                    # headers={'Referer': 'http://gateway.example.com/no_cookie_loginpages/dns.shtml?ReturnUrl=' + returnUrl},
                    cookies=secondCookies,
                    params=payload0)
        r.raise_for_status()
        # print(s.cookies) # same as below
        print(r.cookies)
        # <RequestsCookieJar[<Cookie Session=7671bd8f0c26fbc3649d4d084cc550f6 for gateway.example.com/>,
        # <Cookie ReturnUrl=LP8GpR4dkAsSsSnuiRrOpNryjQbKYS8GaRsFjNryiAs-aO7anOLCp053 for gateway.example.com/loginpages>]>
        # print(r.status_code)

        # print(r.content)
        # ......var vlan_id = '106';
        # var sz_id = 6;
        # var pop_win = 'None';
        # var freeAuth = '0';...........

        sessionId = r.cookies.get_dict().get('Session')
        # not needed these cookies
        # varCookies = s.cookies
        # varCookies.set('password', 'MQ==')
        # varCookies.set('username', '1@local')
        # varCookies.set('Session', sessionId)
        # finalCookies = {'password': 'MQ==',
        #                 'username': '1@local',
        #                 'Session': sessionId}

        creds = {'username': '@user',
                    'password': '****',
                    'accesscode': '',
                    'vlan_id': '106'}
        # sys.exit(0)
        r = s.post('http://gateway.example.com/loginpages/userlogin.shtml',
                    # headers={'Referer': 'http://gateway.example.com/loginpages/login.shtml?ReturnUrl=' + returnUrl},
                    # cookies=finalCookies,
                    data=creds)
        r.raise_for_status()
        print(s.cookies)
        # print(r.cookies)

        getUrl = r.url
        print(f'long Post url is : {getUrl}')
        customUrl = re.findall(r'/?next=(.+)&uid.*&se_enc=(.+)&ip=(.+)&umac=(.+?)&.*&loginvalue=(.+?)&', getUrl)[0]

        nextUrl, seEnc, loginValue = customUrl[0], customUrl[1], customUrl[4]

        localIp, macAddr = customUrl[2], customUrl[3]
        # localIp = '172.26.6.181'
        # macAddr = 'C0:17:4D:4A:DB:AA'

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
                    # cookies=finalCookies,
                    # headers={'Referer': 'http://gateway.example.com/loginpages/login.shtml?ReturnUrl=' + returnUrl},
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

'''
what is this?
if (preOpenURL == true && pop_win !="None" && !skip_popup ) {
    var ReturnUrl_c = getCookie("ReturnUrl");
    var url = 'http://'+hostname+'/no_cookie_loginpages/'+'entry_portal.shtml?uname='+uname+'&ReturnUrl='+ReturnUrl_c;
    if ( user_agent.search( "iPhone" ) != -1 || user_agent.search( "iPad" ) != -1 ) ........
'''

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
            # uncomment if with login # 172.26.1.86
            # localIp = '172.16.17.2'
        logoutParams = {'uid': '1@local',
                        'original_uid': '1',
                        'vidx': '6',
                        'vlanid': '106',
                        'gwip': localIp,
                        # 'gwip': # lr4-----172.16.17.2  /////// lr14-------172.16.17.2
                        'used_time' : time.time() - int(loginTime)
                        }
        r = s.get('http://gateway.example.com/loginpages/logout_redirect.shtml',
                    params=logoutParams,
                    cookies=finalCookies)

        print(r.status_code)
        print(r.content)

    return 'Logged out'

# print(connectToWifi())
sessId = login()
# print(logout(sessId))

# print(logout('BZGQzbGL5Kx8ya1Yzc1ExZVMgKlUjcR4tbB7036'))
# print(logout('a9e1fab9d4d74935f124ed757900db38'))

# 2 quereies
# 1. can use other mac address to login corresponding devices? deviceInfo = {}
# 2. can use others ip address to logout corresponding devices. alas it doesnt depend on ip address but the sessionId
# sent params=ip=172.26.10.37 this is the cmd ipconfig ipv4 address
# but sent params=gwip=172.16.17.2 seems always same
# also username = @user, password=*****
input()
