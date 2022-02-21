# bmdump

reads data from Beurer BM 58 blood pressure monitor and output the result in csv format

Tested with the hid edition of the Beurer BM 58 blood pressure monitor connected to a Linux host.

It may work with the hid models of BM 55 and BM 65 too. (never tested)


**requirements**

requires python 3 and hid (ctypes bindings for hidapi)

read https://pypi.org/project/hid/

keep in mind that connecting to the usb device may need special permissions


**usage**

```
usage: bmdump.py [-h] [-f FILE] [-u USER] [-n] [-b DATE] [-e DATE] -d CHAR [-s CHAR]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --update FILE
                        output latest measurements to a file
  -u USER, --user USER  data for the given user only
  -n, --skip-header     skip header output, in case a file name of a non empty file is given, header output is skipped automatically
  -b DATE, --date-start DATE
                        measurements not older than the given date
  -e DATE, --date-end DATE
                        measurements not newer than the given date
  -d CHAR, --device CHAR
                        device name [bm55, bm58, bm65]
  -s CHAR, --delimiter CHAR
                        data delimiter
```
