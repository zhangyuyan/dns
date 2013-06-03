#!/usr/bin/env python
#-*- coding:utf-8 -*-

__verson__=2.0
__LastModifiedTime__ = '2013-05-30 09:10:00'

import os
import re
import time
import logging

from twisted.names.client import AXFRController
from twisted.names.dns import DNSDatagramProtocol
from twisted.names.dns import  Query
from twisted.names.dns import Name
from twisted.names.dns import TXT
from twisted.names.dns import CH
from twisted.names.dns import Message
from twisted.python.failure import Failure
from twisted.python import log
from twisted.python import failure
from twisted.names.error import DNSQueryTimeoutError

from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.internet import task
from twisted.internet import reactor
reactor.suggestThreadPoolSize(20000)


class DnsDatagramProtocol(DNSDatagramProtocol):
    def datagramReceived(self, data, addr):
        m = Message()
        try:
            m.fromStr(data)
        except EOFError:
            log.msg("Truncated packet (%d bytes) from %s" % (len(data), addr))
            return
        except:
            log.err(failure.Failure(), "Unexpected decoding error")
            return
        if m.id in self.liveMessages:
            d, canceller = self.liveMessages[m.id]
            del self.liveMessages[m.id]
            canceller.cancel()
            try:
                d.callback(m)
            except:
                log.err()
        else:
            if m.id not in self.resends:
                self.controller.messageReceived(m, self)

def get_result(result,ip,i):
    msg = '\t%d\t%s\trA=%d\trCode=%d\t'%(i,ip,result.recAv,result.rCode)

    if len(result.queries)== 0:
        logger_error.error(msg + 'Set Null Query:not implemented')
    elif result.answer == 0:
        logger_error.error(msg + 'Set Q Flag,not A: secured?')
    elif len(result.answers) == 0:
        logger_error.error(msg + 'Set Null Answer:refused')
    else:
        version = ''
        try:
            version = result.answers[0].payload.data[0]
            version = version.replace('\n','')
        except Exception, e:
            pass
        logger_success.critical(msg+version)

def get_error(reason,ip,i):
    msg = '\t%d\t%s\tN/A\tN/A\t'%(i,ip)
    if reason.check(DNSQueryTimeoutError):
        logger_error.error(msg + 'Timed out')
    else:
        rea = reason.getErrorMessage()
        logger_error.error(msg + 'OtherError'+rea)

def release_port(arg,dns):
    try:
        dns.transport.stopListening()
    except Exception,e:
        pass

def check_ip(ip):
   pass

def doWork():
    i = 1
    for ip in file(cwd+"list12.txt"):
        msg = '\t%s\t%d\t%s'
        ip = ip.strip()
        test_ip = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}').findall(ip)
        if test_ip:
            ip = test_ip[0]
            if ip=='192.168.1.0' or ip=='192.168.1.255':
                logger_debug.warn(msg%("illegal",i,ip))
                continue
        else:
            logger_debug.warn(msg%("illegal",i,ip))
            continue

        logger_debug.info(msg%("query",i,ip))
        df = Deferred()
        name = Name('version.bind')
        axf = AXFRController(name,df)
        dns = DnsDatagramProtocol(axf)
        d = dns.query((ip,53),[Query('version.bind',TXT,CH)])
        d.addCallback(get_result,ip,i)
        d.addErrback(get_error,ip,i)
        d.addBoth(release_port,dns)
        i += 1
        yield d

def finish(igo):
    reactor.callLater(5, reactor.stop)
    logging.shutdown()

def taskRun():
    deferreds = []
    coop = task.Cooperator()
    work = doWork()
    maxRun = 5000
    for i in xrange(maxRun):
        d = coop.coiterate(work)
        deferreds.append(d)
    dl = defer.DeferredList(deferreds, consumeErrors=True)
    dl.addCallback(finish)

def main():
    taskRun()
    reactor.run()

if __name__ == '__main__':
    cwd = '/home/zhangyuyan/work/dns/'
    if not os.path.isdir(cwd+'log'):
        os.mkdir(cwd+'log') 

    formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(filename)s-%(lineno)s\t%(levelname)s:%(message)s', '%Y-%m-%d %H:%M:%S')

    logger_debug = logging.getLogger('debug')
    logger_debug.setLevel(logging.DEBUG)
    fh = logging.FileHandler(cwd+'log/debug-'+time.strftime('%Y%m%d%H%M',time.localtime(time.time())))
    ch = logging.StreamHandler()
    fh.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger_debug.addHandler(fh)
   # logger_debug.addHandler(ch)

    logger_error = logging.getLogger('error')
    logger_error.setLevel(logging.DEBUG)
    fh = logging.FileHandler(cwd+'log/error-'+time.strftime('%Y%m%d%H%M',time.localtime(time.time())))
    fh.setLevel(logging.ERROR)
    fh.setFormatter(formatter)
    logger_error.addHandler(fh)

    logger_success = logging.getLogger('result')
    logger_success.setLevel(logging.CRITICAL)
    fh = logging.FileHandler(cwd+'log/success-'+time.strftime('%Y%m%d%H%M',time.localtime(time.time())))
    fh.setLevel(logging.CRITICAL)
    fh.setFormatter(formatter)
    logger_success.addHandler(fh)
 
    main()
