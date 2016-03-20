import os
import re
import datetime


def get_mtime_from_file_name(file_path):
    extensions = r'.(txt|pdf|jpg|mpg|doc|docx|ppt|pptx|xls|xlsx)'

    file_name = os.path.basename(file_path)
    file_dt = None

    # 2016_02_28_11_07_15.jpg
    # since this is the more restrictive, this goes first
    m = re.match(r'(.*)([0-9]{4})_([0-9]{2})_([0-9]{2})_([0-9]{2})_([0-9]{2})_([0-9]{2})' + extensions,
                 file_name, flags=re.I)
    if m:
        file_dt = datetime.datetime(int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)),
                                    int(m.group(6)), int(m.group(7)))

    # hi_there_1_2_16.txt
    if file_dt is None:
        m = re.match(r'(.*)_([0-9]{1,2})_([0-9]{1,2})_([0-9]{2,4})' + extensions,
                     file_name, flags=re.I)
        if m and m.group(4) is not None:
            month = int(m.group(2))
            day = int(m.group(3))
            year_string = m.group(4)
            year = int(year_string)
            if len(year_string) == 2:
                # a century window, and don't allow files from the future :)
                if year > datetime.datetime.now().year:
                    year += 1900
                else:
                    year += 2000
            try:
                file_dt = datetime.datetime(year, month, day)
            except ValueError:
                print('file name format error : %s (year=%i, month=%i, day=%i)' % (file_name, year, month, day))
    return file_dt

