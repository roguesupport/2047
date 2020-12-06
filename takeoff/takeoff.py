import sys, time
sys.path.append('../')

# import monkeypatch
# from commons import *

import sqlite3

class Weibo:
    def get_root(self):
        from root_path import root_path, dest_path, dest_path_universal
        return root_path, dest_path_universal
        # return root_path, dest_path

    def init_sqlite(self):
        print('fullpath is', self.fullpath)
        print('trying to connect to', self.dbpath)
        self.conn = sqlite3.connect(self.dbpath, check_same_thread=False)
        self.q('PRAGMA synchronous = OFF')
        self.q('PRAGMA journal_mode = MEMORY')
        self.q('PRAGMA cache_size = 1000000')

    def __init__(self):
        root, dest = self.get_root()

        self.path = '微博五亿2019.txt'
        self.fullpath = root + self.path

        self.name = 'weibo_500m'
        self.dbpath = dest + self.name + '.db'

        self.init_sqlite()

    def q(self, *a, **k):
        c = self.conn.cursor()
        c.execute(*a, **k)
        return c.fetchall()

    def qmany(self, *a, **k):
        c = self.conn.cursor()
        c.executemany(*a, **k)
        return c.fetchall()

    def commit(self):
        return self.conn.commit()

    def test(self):
        all = self.q(f'select * from {self.name} limit 10')
        print(all)
        return all

    def init_table(self):
        self.q(f'create table {self.name} (mobile integer, uid integer)')

    def create_index(self):
        self.q(f'''create index if not exists mobile_index on {self.name} (mobile)''')
        self.q(f'''create index if not exists uid_index on {self.name} (uid)''')


    def parse(self):
        flushevery = 100000

        dl = []
        def flush():
            nonlocal dl
            print('got', len(dl))
            self.qmany(f'insert into {self.name} values (?,?)', dl)
            self.commit()

            dl = []

        with open(self.fullpath, 'r', encoding='utf-8') as f:

            count = 0
            while 1:
                k = f.readline()
                if k=='':
                    break

                k = k.split('\t')

                if len(k)!=2:
                    print(k)
                    continue

                mobile = k[0].strip()
                uid = k[1].strip()

                if len(mobile)<11:
                    print(mobile, uid)
                    continue

                # print(mobile, uid)

                try:
                    tpl = (int(mobile), int(uid))
                except Exception as e:
                    print(e)
                    print(k)
                else:
                    dl.append(tpl)

                # count+=1

                if len(dl)>=flushevery:
                    count+=len(dl)
                    flush()
                    print('count:', count)

            flush()

    def get_variants(self,s):
        if not isinstance(s, str):
            return [s]
        if len(s)<7: return [s]
        vs = [s]
        if s[0]=='0': vs.append(s[1:])
        if s[0:2]=='00': vs.append(s[2:])
        vs.append('0'+s)
        return vs

    def auto_bracketing(self, num, propnames):
        res = []

        variants = self.get_variants(num)

        for v in variants:
            for n in propnames:
                res += self.q(f'''select * from {self.name}
                where {n}=?1 limit 10''', (v,))

        if not len(res): # if no hit in previous searches
            for n in propnames:
                res += self.q(
                    f'select * from {self.name} where {n}>=?1 order by {n} asc limit 1', (num,))
                res += self.q(
                    f'select * from {self.name} where {n}<=?1 order by {n} desc limit 1', (num,))
        return res

    def resultgen(self, q, l, name_map):
        d = {}
        for n, v in zip(name_map, l):
            d[n] = v
            if v in self.get_variants(q):
                d['hit'] = n
        d['source'] = self.path
        return d

    def find(self, num):
        try:
            num = int(num)
        except:
            return []

        res = self.auto_bracketing(num, ['mobile', 'uid'])
        name_map = 'weibo_mobile,weibo_uid'.split(',')
        return [self.resultgen(num, item, name_map) for item in res]

class QQ(Weibo):
    def __init__(self):
        root, dest = self.get_root()

        # self.path = 'q绑.rar'
        self.path = '6.9更新总库(qq).txt'
        self.fullpath = root + self.path

        self.name = 'qqleak'
        self.dbpath = dest + self.name + '.db'

        self.init_sqlite()

    def parse(self):
        flushevery = 100000

        dl = []
        def flush():
            nonlocal dl
            print('got', len(dl))
            self.qmany(f'insert into {self.name} values (?,?)', dl)
            self.commit()

            dl = []

        with open(self.fullpath, 'r', encoding='utf-8') as f:
            count = 0

            def eat(k):
                nonlocal count
                if len(k[0])>20 or len(k[1])> 20:
                    print('toolong')
                    return

                try:
                    tpl = (int(k[1].strip()), int(k[0].strip()))
                except Exception as e:
                    print(e)
                    print(k)
                    return

                # tpl = (tpl[1], tpl[0])
                dl.append(tpl)

                if len(dl)>=flushevery:
                    count+=len(dl)
                    flush()
                    print(tpl)
                    print('count:', count)

            while 1:
                k = f.readline()
                if k=='':
                    break

                # k = k.decode('ascii')
                k = k.split('----')

                if len(k)!=2:
                    if len(k)==3:
                        if k[0]==k[1]:
                            j = (k[1], k[2])
                            eat(j)
                        else:
                            j = (k[1], k[2])
                            eat(j)
                            j = (k[0], k[2])
                            eat(j)
                    else:
                        s = repr(k)
                        if len(s)<100:
                            print(s)
                        else:
                            print(len(s))
                        # print(k)
                        continue
                else:
                    eat(k)

            flush()

    def find(self, num):
        try:
            num = int(num)
        except:
            return []
        res = self.auto_bracketing(num, ['mobile', 'uid'])
        name_map = 'qq_mobile,qq_number'.split(',')
        return [self.resultgen(num, item, name_map) for item in res]

class SF(Weibo):
    def __init__(self):
        root, dest = self.get_root()

        self.path = '1/shunfeng_script.sql'
        self.fullpath = root + self.path

        self.name = 'sfleak'
        self.dbpath = dest + self.name + '.db'

        self.init_sqlite()

        # self.conn.text_factory = lambda b:b.decode('utf-16')

    def init_table(self):
        self.q(f'create table {self.name} (mobile text, name text, addr text)')

    def create_index(self):
        self.q(f'''create index if not exists mobile_index on {self.name} (mobile)''')
        self.q(f'''create index if not exists name_index on {self.name} (name)''')

    def parse(self):
        flushevery = 100000

        dl = []
        def flush():
            nonlocal dl
            print('got', len(dl))
            self.qmany(f'insert into {self.name} values (?,?,?)', dl)
            self.commit()

            dl = []

        with open(self.fullpath, 'r', encoding='utf-16') as f:
            import re
            count = 0
            countlines = 0
            while 1:
                k = f.readline()
                if len(k)<1:
                    break

                k = k.strip()

                countlines+=1

                # print(k)

                g = re.search(r'\(N\'(.*?)\', N\'(.*?)\', N\'(.*?)\', N\'(.*?)\', N\'(.*?)\', N\'(.*?)\'\)', k)
                # print(g)
                if not g: continue
                # print(g[1], g[2], g[6])
                if not len(g[2]): continue

                try:
                    phone = g[2].strip()
                except Exception as e:
                    print(e)
                    # continue
                    # phone = -1
                    phone = ''

                addr = g[6].strip().replace(r"\'","'")
                # if '，暂不显示' in addr:

                # addr = addr.encode('utf-16')

                name = g[1].strip()

                if not(
                    (name and addr) or (name and phone) or (phone and addr)
                ): continue


                tpl = (name, phone, addr)
                # print(tpl)

                dl.append(tpl)

                # if count==3560: break

                if len(dl)>=flushevery:
                    count+=len(dl)
                    flush()
                    print(tpl)
                    print('count:', count, 'lines:', countlines)

            flush()

    def find(self, num):
        res = self.auto_bracketing(num, ['mobile', 'name'])
        name_map = 'sf_name,sf_mobile,sf_addr'.split(',')
        return [self.resultgen(num, item, name_map) for item in res]

class JD(Weibo):
    def find(self, num):
        res = self.auto_bracketing(num, ['mobile', 'name','username','email','mobile2'])
        name_map = 'jd_name,jd_username,jd_email,jd_sfz,jd_mobile,jd_mobile2'.split(',')
        return [self.resultgen(num, item, name_map) for item in res]

    def __init__(self):
        root, dest = self.get_root()

        self.path = '1/www_jd_com_12g.txt'
        self.fullpath = root + self.path

        self.name = 'jdleak'
        self.dbpath = dest + self.name + '.db'

        self.init_sqlite()

        # self.conn.text_factory = lambda b:b.decode('utf-16')

    def init_table(self):
        self.q(f'create table {self.name} (name text, username text, email text, sfz text, mobile text, mobile2 text)')

    def create_index(self):
        def ci(name):
            self.q(f'''create index if not exists {name}_index on {self.name} ({name})''')

        [ci(k) for k in 'name,username,email,mobile,mobile2'.split(',')]

    def parse(self):
        flushevery = 100000

        dl = []
        def flush():
            nonlocal dl
            print('got', len(dl))
            self.qmany(f'insert into {self.name} values (?,?,?,?,?,?)', dl)
            self.commit()

            dl = []

        with open(self.fullpath, 'r', encoding='utf-8') as f:
            import re
            count = 0
            countlines = 0
            while 1:
                k = f.readline()
                if len(k)<1:
                    break

                k = k.strip()

                countlines+=1

                # print(k)

                g = re.search(r'(.*?)---(.*?)---(.*?)---(.*?)---(.*?)---(.*?)---(.*?)$', k)
                # print(g)
                if not g: continue
                # print(g[1], g[2], g[6])

                name, username, email, sfz, mobile, mobile2 =\
                    g[1], g[2], g[4].lower(), g[5], g[6], g[7]


                tpl = (name, username, email, sfz, mobile, mobile2)
                tpl = tuple(( k.strip().replace('\\N', '') for k in tpl))
                # print(tpl)

                dl.append(tpl)

                # if count==3560: break

                if len(dl)>=flushevery:
                    count+=len(dl)
                    flush()
                    print(tpl)
                    print('count:', count, 'lines:', countlines)

            flush()

class Pingan(Weibo):

    def find(self, num):
        res = self.auto_bracketing(num, ['mobile', 'name', 'email'])
        name_map = 'pingan_name,pingan_sfz,pingan_mobile,pingan_email'.split(',')
        return [self.resultgen(num, item, name_map) for item in res]

    def __init__(self):
        root, dest = self.get_root()

        self.path = '1/平安保险2020年-10w.csv'
        self.fullpath = root + self.path

        self.name = 'pinganleak'
        self.dbpath = dest + self.name + '.db'

        self.init_sqlite()

    def init_table(self):
        self.q(f'create table {self.name} \
        (name text, sfz text, mobile text, email text)')

    def create_index(self):
        def ci(name):
            self.q(f'''create index if not exists {name}_index on {self.name} ({name})''')

        [ci(k) for k in 'name,email,mobile'.split(',')]

    def parse(self):
        flushevery = 100000

        dl = []
        def flush():
            nonlocal dl
            print('got', len(dl))
            self.qmany(f'insert into {self.name} values (?,?,?,?)', dl)
            self.commit()

            dl = []

        # with open(self.fullpath, 'r', encoding='utf-8') as f:
        with open(self.fullpath, 'rb') as f:
            import re
            count = 0
            countlines = 0
            while 1:
                k = f.readline()

                if len(k)<1:
                    break

                k = k.decode('gb2312', errors='ignore')
                k = k.strip()

                countlines+=1

                cols = k.split(',')
                assert len(cols)==16

                c = cols

                name, sfz, mobile, email = c[3], c[4], c[6], c[7]
                # print(cols[3])

                tpl = (name.strip(), sfz.strip(), mobile.strip(), email.lower().strip())
                # print(tpl)

                dl.append(tpl)

                # if count==3560: break

                if len(dl)>=flushevery:
                    count+=len(dl)
                    flush()
                    print(tpl)
                    print('count:', count, 'lines:', countlines)

            flush()

if __name__ == '__main__':
    weibo = Weibo()

    # weibo.init_table()
    # weibo.parse()
    # weibo.test()
    # weibo.create_index()
    # weibo.test()

    print(weibo.find('15890981333'))
    print(weibo.find('3798002017'))

    qq = QQ()

    # qq.init_table()
    # qq.parse()
    # qq.test()
    # qq.create_index()
    # qq.test()

    print(qq.find('13550121037'))

    sf = SF()

    # sf.init_table()
    # sf.parse()
    # sf.test()
    # sf.create_index()
    # sf.test()

    print(sf.find('黄小姐'))
    print(sf.find('13662168290'))

    jd = JD()

    # jd.init_table()
    # jd.parse()
    # jd.test()
    # jd.create_index()
    # jd.test()

    print(jd.find('刘庆宁'))
    print(jd.find('OGVTK28'))
    print(jd.find('13165993135'))

    pingan = Pingan()

    # pingan.init_table()
    # pingan.parse()
    # pingan.test()
    # pingan.create_index()
    # pingan.test()

    print(pingan.find('陈希'))
    print(pingan.find('13079804169'))