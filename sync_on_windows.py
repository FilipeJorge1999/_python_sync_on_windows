import os
import hashlib
import time
import shutil

# in case of FileNotFoundError: [WinError 3]
if os.path.exists('log.txt'):
  os.remove('log.txt')

if os.path.exists('config.txt'):
  os.remove('config.txt')

LOG = 'log.txt'


# functions -------------------------------------------------------------


def compare2file(file1, file2):
    # compare 2 files with hash
    with open(file1, 'rb') as f1:
        with open(file2, 'rb') as f2:
            if hashlib.md5(f1.read()).hexdigest() == hashlib.md5(f2.read()).hexdigest():
                return True
            else:
                return False
# log function
def log(message):
    # write log
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG, 'a') as f:
        f.write('['+now+']'+message+'\n')

def compareHashFolder(folder, backup):
    # compare hash folder
    # return True if all file is same
    # return False if any file is different
     # get all file in folder
    files = os.listdir(folder)
    # get all file in backup
    files_backup = os.listdir(backup)
    # compare 2 list
    if len(files) != len(files_backup):
        return False

    for file in files:
        if file in files_backup:
            if not compare2file(folder+'/'+file, backup+'/'+file):
                return False
        else:
            return False
    return True

#------------------------------------------------------------------
log('Start')

if os.path.isfile('config.txt'):
    print("config file: OK")
    log ('config file: OK')
    # get variable from config
    with open('config.txt', 'r') as f:
        lines = f.readlines()
        folder = lines[0].split(':')[1].strip()
        backup = lines[1].split(':')[1].strip()

else:
    log('config file: NOT FOUND')
    print("config file: NOT FOUND")
    # register folder
    folder = input('enter the source directory:')
    backup = input('enter your replica path:')
    # check if folder is exist
    if not os.path.isdir(folder):
        log('folder: NOT FOUND')
        print('source does not exist')
        exit()
    # check if backup is exist
    if not os.path.isdir(backup):
        log('backup: NOT FOUND')
        print('replica does not exist')
        exit()
    # write config
    with open('config.txt', 'w') as f:
        f.write('folder:'+folder)
        f.write('\n')
        f.write('backup:'+backup)
    print('config file: CREATED')
    log('config file: CREATED')

# run loop every 30 seconds

while True:
    # check if folder is same with backup
    if compareHashFolder(folder, backup):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'[{now}] file is up to date')
        log('file is up to date')
        # sleep for 30 seconds
        time.sleep(30)
        continue

    # check folder
    if os.path.isdir(folder):
        print('folder: ONLINE')
        log('folder: ONLINE')
    else:
        print('folder does not exist')
        log('folder does not exist')
        print('please check your config file')
        break

    # check backup
    if os.path.isdir(backup):
        print('backup: ONLINE')
        log('backup: ONLINE')
    else:
        print('backup does not exist')
        log('backup does not exist')
        print('please check your config file')
        break

    # check file hash in folder and compare with backup
    countSync = 0
    updateFile = 0
    deleteFile = 0

    # get all file in folder
    files = os.listdir(folder)
    # get all file in backup
    files_backup = os.listdir(backup)
    # compare 2 list
    for file in files_backup:
        if file in files:
            if compare2file(folder+'/'+file, backup+'/'+file):
                log(f'{file} is up to date')
                countSync += 1
            else:
                # copy file from folder to backup
                updateFile += 1
                os.remove(backup+'/'+file)
                shutil.copy2(folder+'/'+file, backup)
                log(f'{file} is updated')
        if file not in files:
            # delete file in backup
            log(f'{file} is deleted')
            deleteFile += 1
            os.remove(backup+'/'+file)

    for file in files:
        if file not in files_backup:
            # copy file from folder to backup
            updateFile += 1
            log(f'{file} is copied')
            shutil.copy2(folder+'/'+file, backup)



    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f'[{now}] sync: {countSync}; update: {updateFile}; delete: {deleteFile};')

    # sleep for 30 seconds
    time.sleep(30)