# coding: utf-8
from datetime import datetime
import subprocess, os, shutil, time
from threading import Thread, RLock


class CommandTime:
    def execute(self):
        print ('Time is now: {}:{}:{}'.format(datetime.now().hour, datetime.now().minute, datetime.now().second))


class CommandDiskFS:
    def execute(self):
        output = subprocess.check_output('df -h', shell=True)
        print ("free disk space: ", output.decode())


class CommandListFS:
    def create_archive(self, src):
        if os.path.isdir(src):
            dest = src + '.tar.gz'
        else:
            filename, file_extension = os.path.splitext(src)
            dest = filename + '.tar.gz'

        p = subprocess.Popen(['tar', '-Pczf', dest, src], shell=False)
        p.wait()

        if p.poll() == 0:
            print('\narchive {} created success'.format(dest))
        else:
            print('\narchive {} created with error'.format(dest))

    def execute(self):
        while True:
            cmd = input('Enter subcommand (list|create|delete|archive|exit|help [path]): ')
            cmd_lst = cmd.split()

            if len(cmd_lst):
                action = cmd_lst[0]
            else:
                action = None

            if not action in ['list', 'create', 'delete', 'archive', 'exit', 'help']:
                print('incorrect subcommand. try again ...')
                continue

            if action == 'help':
                print("\tlist [path] - show files and directories from path (default is current path)")
                print("\tcreate path - create file from path")
                print("\tdelete path - delete file or directory from path")
                print("\tarchive path - create archive file or directory from path in async mode")
                print("\texit - exit from subcommand shell")
                print("\thelp - show subcommand help")
                continue

            if action == 'exit':
                break

            if len(cmd_lst) < 2 and action in ['create', 'delete', 'archive']:
                print ("empty path argument. try again ...")
                continue

            if len(cmd_lst) < 2:
                cmd_lst.append('.')

            src = os.path.abspath(cmd_lst[1])

            if action == 'list':
                if os.path.isdir(src):
                    print('list dir {}:'.format(src))
                    files = os.listdir(src)
                    for f in files:
                        print(f)
                else:
                    print(src)

            if action == 'create':
                if os.path.exists(src) and os.path.isfile(src):
                    print('file {} already exists. try any other path ...'.format(src))
                    continue
                file = open(src, 'w')
                file.close()
                print('file {} created'.format(src))

            if action == 'delete':
                if not os.path.exists(src):
                    print ("{} not exists. try delete any other path ...".format(src))
                    continue
                if os.path.isdir(src):
                    shutil.rmtree(src)
                else:
                    os.remove(src)
                print('{} deleted'.format(src))

            if action == 'archive':
                if not os.path.exists(src):
                    print("{} not exists. try archive any other path ...".format(src))
                    continue
                thread = Thread(target=self.create_archive, args=(src,))
                thread.start()


class CommandHelp:
    def execute(self):
        print ("\ttime - show current time")
        print ("\tdf - show free space on disk")
        print ("\tfs - subcommand shell")
        print ("\texit - exit from shell")
        print ("\thelp - show command help")

class Command:
    __commands = {
        'time': CommandTime,
        'df': CommandDiskFS,
        'fs': CommandListFS,
        'help': CommandHelp
    }

    @staticmethod
    def create(name):
        return Command.__commands[name]()


if __name__ == '__main__':
    try:
        while True:
            command = input('Your command (time|df|fs|exit|help): ')
            if command in ['time', 'df', 'fs', 'help']:
                cmd = Command.create(command)
                cmd.execute()
            elif command == 'exit':
                break
            else:
                print ('incorrect command. try again ...')
    except KeyboardInterrupt:
        print ('\nshell terminated')