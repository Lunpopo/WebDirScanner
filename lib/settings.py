import os

ROOT_PATH = os.getcwd()
DICT_PATH = os.path.join(ROOT_PATH, 'dict')
IMAGES_PATH = os.path.join(ROOT_PATH, 'images')
DATA_PATH = os.path.join(ROOT_PATH, 'data')
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'close',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}
DICT_LIST_TEXT = """
The following lists are included with WebDirScanner:

simple-dir-dict.txt  (1153 words)
Including simple files/dirs dict

file-dict.txt  (79080 words)
Including lots of web files/dirs/path dict

from-wwwscan-cgi.txt  (252509 words)
Heavyweight and fullest dict which contained lots of files/dirs/path/config

directory-list-2.3-small.txt  (87650 words)
Directories/files that where found on at least 3 different hosts

directory-list-2.3-medium.txt  (220546 words)
Directories/files that where found on at least 2 different hosts

directory-list-2.3-big.txt  (1273819 words)
All directories/files that where found

directory-list-lowercase-2.3-small.txt  (81629 words)
Case insensitive version of directory-list-2.3-small.txt

directory-list-lowercase-2.3-medium.txt  (207629 words)
Case insensitive version of directory-list-2.3-medium.txt

directory-list-lowercase-2.3-big.txt  (1185240 words)
Case insensitive version of directory-list-2.3-big.txt

directory-list-1.0.txt  (141694 words)
Original unordered list

apache-user-enum-1.0.txt  (8916 usernames)
Used for guessing system users on apache with the userdir module enabled, based on a
username list I had lying around (unordered)

apache-user-enum-2.0.txt  (10341 usernames)
Used for guessing system users on apache with the userdir module enabled, based
on ~XXXXX found during list generation (Ordered)
"""