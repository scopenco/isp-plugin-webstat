#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This plugin fix problem described in http://forum.ispsystem.com/ru/showthread.php?t=23471
There is a bug in ISPmanager with scheme where nginx and apache+itk is used. 
Webstats are not accesible because config files passwd and .htaccess are created with wrong permissions. This plugin fixes the problem.

Author: Andrey Scopenco <andrey@scopenco.net>
'''

PLUGIN_NAME = 'webstat_change_perms'
LOG_FILE = '/usr/local/ispmgr/var/ispmgr.log'

from xml.dom import minidom
from pwd import getpwuid,getpwnam
from os import chdir,getpid,environ,access,R_OK,chown,listdir
from sys import exit,stderr
from cgi import FieldStorage
from traceback import format_exc

class ExitOk(Exception):
    pass

class Log(object):
    '''Class used for add debug to ispmgr.log'''
    def __init__(self, plugin=None, output=LOG_FILE):
        import time
        timenow = time.localtime(time.time())
        self.timef = time.strftime("%b %d %H:%M:%S", timenow)
        self.log = output;
        self.plugin_name = plugin;
        self.fsock = open(self.log, 'a+')
        self.pid = getpid()
        self.script_name = __file__

    def write(self,desc):
        if not (desc == "\n"):
            if (desc[-1:] == "\n"):
                self.fsock.write('%s [%s] ./%s \033[36;40mPLUGIN %s :: %s\033[0m' % \
                    (self.timef, self.pid, self.script_name, self.plugin_name, desc))
            else:
                self.fsock.write('%s [%s] ./%s \033[36;40mPLUGIN %s :: %s\033[0m\n' % \
                    (self.timef, self.pid, self.script_name, self.plugin_name, desc))

    def close(self):
        self.fsock.close()

def xml_doc(elem = None, text = None):
    xmldoc = minidom.Document()
    doc = xmldoc.createElement('doc')
    xmldoc.appendChild(doc)
    if elem:
        emp = xmldoc.createElement(elem)
        doc.appendChild(emp)
        if text:
            msg_text = xmldoc.createTextNode(text)
            emp.appendChild(msg_text)
    return xmldoc.toxml('UTF-8')

def xml_error(text,code_num=None):
    xmldoc = minidom.Document()
    doc = xmldoc.createElement('doc')
    xmldoc.appendChild(doc)
    error = xmldoc.createElement('error')
    doc.appendChild(error)
    if code_num:
        code = xmldoc.createAttribute('code')
        error.setAttributeNode(code)
        error.setAttribute('code',str(code_num))
        if code_num in [2,3,6]:
            obj = xmldoc.createAttribute('obj')
            error.setAttributeNode(obj)
            error.setAttribute('obj',str(text))
            return xmldoc.toxml('UTF-8')
        elif code_num in [4,5]:
            val = xmldoc.createAttribute('val')
            error.setAttributeNode(val)
            error.setAttribute('val',str(text))
            return xmldoc.toxml('UTF-8')
    error_text = xmldoc.createTextNode(text.decode('utf-8'))
    error.appendChild(error_text)
    return xmldoc.toxml('UTF-8')

def domain_to_idna(dom):                                                                                                                                                                       
    ''' convert domain to idna format'''
    dom_u = unicode(dom, 'utf-8')
    return dom_u.encode("idna")

if __name__ == "__main__":
    chdir('/usr/local/ispmgr/')

    # activate logging
    # stderr ==> ispmgr.log
    log = Log(plugin=PLUGIN_NAME)
    stderr = log

    try:
        # get cgi vars
        req = FieldStorage(keep_blank_values=True)
        func = req.getvalue('func')
        elid = req.getvalue('elid')
        sok = req.getvalue('sok')

        log.write('func %s, elid %s, sok %s' % (func, elid, sok))

        if func != 'wwwdomain.edit' or not sok:
            print xml_doc()
            raise ExitOk('no action')

        user = req.getvalue('owner')
        if not user:
            user = environ.get('REMOTE_USER')

        if not user:
            raise Exception('cant set user')

        try:
            pw_user = getpwnam(user)
        except KeyError:
            print xml_doc()                                                                                                                                                           
            raise ExitOk('user not found')

        pw_apache = getpwnam('apache')
        log.write('user %s has uid %s' % (user, pw_user.pw_uid))

        chgrp = []
        domain = domain_to_idna(req.getvalue('domain'))
        passwd_dir = '%s/etc' % pw_user.pw_dir
        for passwd in listdir(passwd_dir):
            if 'passwd' in passwd:
                chgrp.append('%s/%s' % (passwd_dir, passwd))
        chgrp.append('%s/www/%s/webstat/.htaccess' % (pw_user.pw_dir, domain))
        for conf in chgrp:
            if access(conf, R_OK):
                log.write('chown %s:%s %s' % (pw_user.pw_uid, pw_apache.pw_gid,  conf))
                chown(conf, pw_user.pw_uid, pw_apache.pw_gid)

        print xml_doc('ok')
        raise ExitOk('done')

    except ExitOk, e:
        log.write(e)
    except:
        print xml_error('please contact support team', code_num='1')
        log.write(format_exc())
        exit(0)
