#!/usr/bin/python3

import sys
import getopt
import os
import subprocess

def main(argv):
    help = 'clutch.py [-n] [-d] [-v <output video codec>] [-a <output audio codec>] [-t <tmp directory>] [-e <edl file extension>] <input video file>'
    pathname = ""
    tmp = ""
    out = ""
    vcodec = ""
    acodec = ""
    edl_ext = "edl"
    debug = False
    noop = False
    try:
        opts, args = getopt.getopt(argv, "ndhv:a:e:t:", ["vcodec=", "acodec=", "edlext=", "tmp="])
    except getopt.GetoptError:
        print(help)
        sys.exit(2)
    print(args)
    for opt, arg in opts:
        if opt == '-h':
            print(help)
            sys.exit(2)
        elif opt == '-d':
            debug = True
            print('Debug On ...')
        elif opt == '-n':
            noop = True
            print('No-op On ...')
        elif opt in ("-v", "--vcodec"):
            vcodec = arg
        elif opt in ("-a", "--acodec"):
            acodec = arg
        elif opt in ("-e", "--edlext"):
            edl_ext = arg
        elif opt in ("-t", "--tmp"):
            if os.path.exists(arg) and os.path.isdir(arg):
                tmp = arg
            else:
                print("Directory {0} does not exist".format(arg))
                sys.exit(2)
    try:
        pathname = args[0]
        if os.path.exists(pathname):
            if debug:
                print("Input file set to {0}".format(pathname))
        else:
            print("Input file {0} does not exist".format(pathname))
            sys.exit(2)
    except:
        print("Missing input pathname")
        sys.exit(2)

    (dirname, filename) = os.path.split(pathname)
    (basename, ext) = os.path.splitext(filename)
    if debug:
        print("Pathname set to {0}".format(pathname))
        print("  with dirname set to {0}".format(dirname))
        print("  with filename set to {0}".format(filename))
        print("  with basename set to {0}".format(basename))
        print("  with extension set to {0}".format(ext))
    if tmp == "":
        tmp = dirname
    if debug:
        print("Temporary files sent to {0}".format(tmp))
    edl = "{0}/{1}.{2}".format(dirname, basename, edl_ext)
    if debug:
        print("EDL set to {0}".format(edl))
    fix = "{0}/{1}.fix{2}".format(tmp, basename, ext)
    if debug:
        print("Stream fix pathname set to {0}".format(fix))
    if tmp == dirname:
        out = "{0}/{1}.cut{2}".format(tmp, basename, ext)
    else:
        out = "{0}/{1}{2}".format(tmp, basename, ext)
    if debug:
        print("Output pathname set to {0}".format(out))

    # Block to determine "end time"
    # Example:
    # ffmpeg -i Days\ of\ Thunder\ \(1990\)\ 2020-09-19-1730.mpg 2>&1 | grep -E "Duration" | awk '{ print $2; }' | awk -F ',' '{ print $1; }'
    cmd = "ffmpeg -i \"{0}\" 2>&1 | grep -E \"Duration\" | awk '{{ print $2; }}' | awk -F ',' '{{ print $1; }}'".format(pathname)
    if debug:
        print(cmd)
    duration = subprocess.check_output(cmd, shell=True).split()[0].decode()
    if debug:
        print("Duration set to {0}".format(duration))
    (hour, min, sec) = duration.split(':')
    end = 3600.0 * float(hour) + 60.0 * float(min) + 1.0 * float(sec)
    if debug:
        print("End time in seconds set to {0}".format(end))

    # Block to determine "audio codec name" and "video codec name"
    # Example:
    # ffmpeg -i Days\ of\ Thunder\ \(1990\)\ 2020-09-19-1730.mpg 2>&1 | grep -E "Stream" | grep -E "Video" | awk '{ print $4; }'
    # ffmpeg -i Days\ of\ Thunder\ \(1990\)\ 2020-09-19-1730.mpg 2>&1 | grep -E "Stream" | grep -E "Audio" | awk '{ print $4; }'
    cmd = "ffmpeg -i \"{0}\" 2>&1 | grep -E \"Stream\" | grep -E \"Video\" | awk '{{ print $4; }}'".format(pathname)
    if debug:
        print(cmd)
    vcodec = subprocess.check_output(cmd, shell=True).split()[0].decode()
    if debug:
        print("Video codec set to {0}".format(vcodec))
    cmd = "ffmpeg -i \"{0}\" 2>&1 | grep -E \"Stream\" | grep -E \"Audio\" | awk '{{ print $4; }}'".format(pathname)
    if debug:
        print(cmd)
    acodec = subprocess.check_output(cmd, shell=True).split()[0].decode()
    if debug:
        print("Audio codec set to {0}".format(acodec))

    cmds = list()

    # Block to generate "stream fix command"
    # Example:
    # ffmpeg -i Days\ of\ Thunder\ \(1990\)\ 2020-09-19-1730.mpg -map 0:v:0 -map 0:a:1 -acodec copy -vcodec copy Days\ of\ Thunder\ \(1990\)\ 2020-09-19-1730.fix.mpg
    cmd = "ffmpeg -i \"{0}\" -map 0:v:0 -map 0:a:0 -acodec copy -vcodec copy \"{1}\" 2>&1".format(pathname, fix)
    if debug:
        print("Stream fix command...\n {0}".format(cmd))
    cmds.append(cmd)

    # Block to read the EDL file
    fd = open(edl, 'r')
    lines = fd.readlines()
    fd.close()
    n = len(lines)
    seg = list()
    i = 0
    for line in lines:
        (start, stop, action) = line.split("\t")
        if i == 0:
            seg.append([0.0, start])
            seg.append([stop, -1])
        elif i == n - 1:
            seg[i][1] = str(float(start) - float(seg[i][0]))
            seg.append([stop, str(float(end) - float(stop))])
        else:
            seg[i][1] = str(float(start) - float(seg[i][0]))
            seg.append([stop, -1])
        i += 1
    n += 1

    #
    # Block to generate the trim, clean and join commands
    #
    trim = list()
    clean = list()
    text = list()
    join = "ffmpeg -f concat -safe 0 -i \"{0}/{1}.txt\" -c copy \"{2}\" 2>&1".format(tmp, basename, out)
    for i in range(n):
        if ( float(seg[i][1]) != 0.0 ):
            trim.append("ffmpeg -ss {5} -i \"{1}\" -to {6} -async 1 -vcodec copy -acodec copy \"{2}/{3}.part{0}{4}\" 2>&1".format(i, fix, tmp, basename, ext, seg[i][0], seg[i][1]))
            text.append("echo file \"\'{1}/{2}.part{0}{3}\'\" >> \"{1}/{2}.txt\"".format(i, tmp, basename, ext))
            clean.append("rm \"{1}/{2}.part{0}{3}\"".format(i, tmp, basename, ext))
            if debug:
                print(trim[len(trim)-1])
                print(text[len(text)-1])
                print(clean[len(clean)-1])

    clean.append("rm \"{0}/{1}.txt\"".format(tmp, basename))
    clean.append("rm \"{0}\"".format(fix))

    for sub in trim:
        cmds.append(sub)
    for sub in text:
        cmds.append(sub)
    cmds.append(join)
    for sub in clean:
        cmds.append(sub)

    for cmd in cmds:
        print(cmd)
        if not noop:
            os.system(cmd)

    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
