# useful definitions in one place

import os, hashlib, binascii as ba

# everything time related

import datetime

dtdt = datetime.datetime
dtt = datetime.time
dtd = datetime.date
dtn = dtdt.now

# default time parsing
def dtdt_from_stamp(stamp):
    return dtdt.fromisoformat(stamp)

dfs = dtdt_from_stamp

# proper time formatting
# input: string iso timestamp
# output: string formatted time

def format_time(dtdt,s):
    return dtdt.strftime(s)

# default time formatting
def format_time_iso(dtdt):
    return dtdt.isoformat(timespec='seconds')[:19]
fti = format_time_iso

format_time_datetime = lambda s: format_time(dfs(s), '%Y-%m-%d %H:%M')
format_time_dateonly = lambda s: format_time(dfs(s), '%Y-%m-%d')
format_time_timeonly = lambda s: format_time(dfs(s), '%H:%M')

def format_time_dateifnottoday(s):
    dt = dfs(s)
    now = dtn()

    if now.date() > dt.date():
        return format_time_dateonly(s)
    else:
        return format_time_timeonly(s)

def time_iso_now():
    return format_time_iso(dtn())

# pw hashing

def bytes2hexstr(b):
    return ba.b2a_hex(b).decode('ascii')

def hexstr2bytes(h):
    return ba.a2b_hex(h.encode('ascii'))

# https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
def get_salt():
    return os.urandom(32)

def hash_pw(salt, string):
    return hashlib.pbkdf2_hmac(
        'sha256',
        string.encode('ascii'),
        salt,
        100000,
    )

# input string, output hash and salt
def hash_w_salt(string):
    salt = get_salt()
    hash = hash_pw(salt, string)
    return bytes2hexstr(hash), bytes2hexstr(salt)

# input hash,salt,string, output comparison result
def check_hash_salt_pw(hashstr, saltstr, string):
    chash = hash_pw(hexstr2bytes(saltstr), string)
    return chash == hexstr2bytes(hashstr)

# username rule
username_regex=r'^[0-9a-zA-Z\u4e00-\u9fff\-\_\.]{2,16}$'
username_regex_string = str(username_regex).replace('\\\\','\\')

# markdown renderer

if 0:
    import markdown
    def convert_markdown(s):
        return markdown.markdown(s)
else:

    import re
    pattern = (
        r'((((http|https|ftp):(?:\/\/)?)'  # scheme
        r'(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+(:\[0-9]+)?'  # user@hostname:port
        r'|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)'  # www.|user@hostname
        r'((?:\/[\+~%\/\.\w\-_]*)?'  # path
        r'\??(?:[\-\+=&;%@\.\w_]*)'  # query parameters
        r'#?(?:[\.\!\/\\\w]*))?)'  # fragment
        r'(?![^<]*?(?:<\/\w+>|\/?>))'  # ignore anchor HTML tags
        r'(?![^\(]*?\))'  # ignore links in brackets (Markdown links and images)
    )
    link_patterns = [(re.compile(pattern),r'\1')]
    import markdown2 as markdown
    from markdown2 import Markdown
    md = Markdown(
        extras=[
            'link-patterns',
            'fenced-code-blocks',
            'nofollow',
            'tag-friendly',
            'strike',
        ],
        link_patterns = link_patterns,
    )

    def convert_markdown(s):
        return md.convert(s)

# database connection
from aql import AQLController
aqlc = AQLController('http://127.0.0.1:8529', 'db2047',[])
aql = aqlc.aql

# site pagination defaults

thread_list_defaults = dict(
    pagenumber=1,
    pagesize=30,
    order='desc',
    sortby='t_u',
)

user_thread_list_defaults = dict(
    pagenumber=1,
    pagesize=30,
    order='desc',
    sortby='t_c',
)

post_list_defaults = dict(
    pagenumber=1,
    pagesize=50,
    order='asc',
    sortby='t_c',
)

user_post_list_defaults = dict(
    pagenumber=1,
    pagesize=50,
    order='desc',
    sortby='t_c',
)

user_list_defaults = dict(
    pagenumber=1,
    pagesize=50,
    order='desc',
    sortby='uid',
)

common_links = [
    {'text':'花名册', 'url':'/u/all'},
    {'text':'删帖', 'url':'/c/deleted'},
    {'text':'老用户', 'url':'/t/7108'},
    {'text':'邀请码', 'url':'/t/7109'},
]

# priviledge: who can do what to whom

def can_do_to(u1, operation, u2id):
    if not u1:
        return False

    is_self = True if u1['uid'] == u2id else False
    is_admin = True if (('admin' in u1) and u1['admin']) else False

    if operation == 'delete':
        if is_self or is_admin:
            return True

    elif operation == 'edit':
        if is_self or is_admin:
            return True

    return False

# parse string of form "target_type/target_id"

def parse_target(s):
    s = s.split('/')
    if len(s)!=2:
        raise Exception('target string failed to split')

    targ = s[0]
    _id = int(s[1])

    return targ, _id

password_warning = convert_markdown('''
# 密码安全警告

2047不接收明文密码，因此无法帮助用户判断其密码是否符合安全要求。

密码太简单（少于13位纯数字、少于8位数字+字母、[最常见的一百万个密码](https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt)）将导致你的密码被人用计算机在短时间内猜解。

2047建议您使用浏览器提供的随机密码。

''')

if __name__ == '__main__':
    h, s = hash_w_salt('1989')
    assert check_hash_salt_pw(h, s, '1989')
    assert check_hash_salt_pw(h, s, '0604') == False

    import re
    print(re.fullmatch(username_regex, 'asdf你好中国'))