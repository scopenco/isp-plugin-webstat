isp-plugin-webstat
==================

Documentation
--------
There is a bug in ISPmanager with scheme where nginx+apache+itk/suexec is used. Webstat is not accesible because config files passwd and .htaccess are created with wrong permissions. This plugin fixes the problem.

Installing
----------
> cp -v etc/ispmgr_mod_webstat_change_perms.xml /usr/local/ispmgr/etc/

> cp -v addon/webstat_change_perms.py /usr/local/ispmgr/addon/

> killall -9 ispmgr

Testing
----------
Tested on CentOS 6.

Questions?
----------
If you have questions or problems getting things
working, first try searching wiki.

If all else fails, you can email me and I'll try and respond as
soon as I get a chance.

        -- Andrey V. Scopenco (andrey@scopenco.net)     
