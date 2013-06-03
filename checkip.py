import re

def check_ip(ip):
    ip = ip.strip()
    if '/' in ip:
        divsion = ip.split('/')
        prefixlen = int(divsion[1])  
        if prefixlen==32:
            return divsion[0]
        else:
            ip = ip_to_int(divsion[0]) 
            netmask = ((2<<prefixlen-1)-1) << (32 - prefixlen)
            max_num = 2**(32-prefixlen)-2
            print 'max_num',max_num
            print 'ip',ip
            print 'netmask',netmask
            first = (ip&netmask)+1
            target = []
            for x in xrange(max_num):
                ipstr = int_to_ip(first)
                target.append(ipstr)
                first+=1
            return target
    else:
        ip = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}').findall(ip)
        if ip:
            return ip
        else:
            return False

def int_to_ip(ip):
    ip = int(ip)
    ret = ''
    for x in xrange(4):
        ret = str(ip & 0xff) + '.' + ret
        ip = ip >> 8
    ret = ret[:-1]
    return ret

def ip_to_int(ipstr):
    bytes = ipstr.split('.')
    bytes = [int(x) for x in bytes]
    return (bytes[0] << 24) + (bytes[1] << 16) + (bytes[2] << 8) + bytes[3]

# test = check_ip('211.137.96.205/26')
# print test
# print len(test)

# test = check_ip('117.135.192.2/30')
# print test
# print len(test)

filelist = ['list1.txt','list2.txt','list3.txt','list8.txt',
    'list9.txt','list10.txt','list11.txt','list12']
fw = open('list','a')
for f in filelist:
    fr = open(f,'r')
    for line in fr.readlines():
        iplist = check_ip(line)
        if iplist:
            for ip in iplist:
                fw.write(ip+'\n')
        else:
            pass
    fr.close()
fw.close()

# i = 1
# fp = open('cidr','r')
# fw = open('target','a')
# for x in fp.readlines():
#     x = x.strip()
#     ip = check_ip(x)
#     fw.write(str(i)+'\t'+str(ip)+'\n')
#     i += 1
# fp.close()
# fw.close()









