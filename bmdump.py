#!/usr/bin/env python3

import hid
import sys
import csv
import os.path
from argparse import ArgumentParser

vid = 0x0C45
pid = 0x7406

init_cmd  = bytes([ 0xAA, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4 ])
cnt_cmd   = bytes([ 0xA2, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4 ])
fetch_cmd = bytearray([ 0xA3, 0x00, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4 ])
exit_cmd  = bytes([ 0xF7, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4, 0xF4 ])

parser = ArgumentParser()
parser.add_argument("-f", "--update", dest="filename", help="stores latest measurements to a file, default limiter ';' otherwise '\\t' for stdout", metavar="FILE")
parser.add_argument("-u", "--user", dest="user", help="measurements for the given user only", metavar="USER")
parser.add_argument("-n", "--skip-header", dest="header", help="skip header output - in case a file name of a non empty file is given, header output is skipped automatically", action='store_true')
parser.add_argument("-b", "--date-start", dest="datestart", help="measurements not older than the given date", metavar="DATE")
parser.add_argument("-e", "--date-end", dest="dateend", help="measurements not newer than the given date", metavar="DATE")
parser.add_argument("-d", "--device", dest="device", help="device name [bm55, bm58, bm65]", metavar="CHAR", choices=['bm55', 'bm58', 'bm65'], required=True)
parser.add_argument("-s", "--delimiter", dest="delimiter", help="data delimiter", metavar="CHAR")
args = parser.parse_args()

result = []
last_date = ""
delimiter = ";" if not args.delimiter else args.delimiter
if not args.delimiter and not args.filename:
    delimiter = "\t"
file_empty = True

# device lookup
if len(hid.enumerate(vid, pid)) == 0:
    print("error: no device found", file=sys.stderr)
    sys.exit(1)

# reading csv data file
if args.filename and os.path.isfile(args.filename):
    with open(args.filename, newline='') as csvfile:
        myreader = csv.reader(csvfile, delimiter=delimiter)
        for row in myreader:
            file_empty = False
            if row[0] == 'dev':
                continue
            if args.user and args.user != row[1]:
                continue
            if row[2] > last_date:
                last_date = row[2]
        csvfile.close()

# opening hid device
with hid.Device(vid, pid) as h:

    #initialize
    h.write(init_cmd);
    res = h.read(8, 2000)
    if not res:
        print("error: device not in pc mode, please reconnect the device", file=sys.stderr)
        sys.exit(1)        

    h.write(cnt_cmd)
    res = h.read(8, 5000)

    for i in range(res[0]):
        fetch_cmd[1] = i + 1;
        h.write(bytes(fetch_cmd));
        d = h.read(8);
        u = 1 + int(d[4] > 128)
        dt = "-".join([str(2000 + (d[7] & 0x7F)), str(d[3] & 0x0F).zfill(2), str(d[4]& 0x1F).zfill(2)])+' '+str(d[5]).zfill(2)+':'+str(d[6]).zfill(2)

        if args.datestart and dt < args.datestart:
            continue
        elif dt <= last_date:
            continue
        if args.dateend and dt > args.dateend:
            continue
        if args.user and args.user != str(u):
            continue

        arr = ''
        mov = ''

        if args.device in ['bm55', 'bm58'] :
           arr = str(int(d[7] & 0x80 == 128))
        if args.device in ['bm55'] :
           mov = str(d[3] >> 7)

        out = [ args.device, str(u), dt, str(d[0] + 25), str(d[1] + 25), str(d[2]), arr, mov ]
        result.append(out)

    h.write(exit_cmd)
    h.close()

    header = ["dev", "usr", "date_time_measurement", "sys", "dia", "pul", "arr", "mov"]

    if args.filename:
        with open(args.filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter, lineterminator="\n")
            if file_empty:
                writer.writerow(header)
            for data in result:
                writer.writerow(data)
    else:
        print(delimiter.join(header))
        for data in result:
            print(delimiter.join(data))

