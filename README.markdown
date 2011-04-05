# python-backupr


## Description

Make a backup of a MySQL database and send an (optional) success email through a GMail account.

This method will create an SQL dump of the given MySQL database, tar (compress) the file and save the file to the local file system. 

Depending on the options you pass it, it will delete the SQL dump (not the tar file) after your compress it and send you a cute email letting you know what happened and where the file was saved. The email will also have the tar file attached to it so you have a backup on your email server in addition to the local file system.

The backups are named with the name of the DB, and the timestamp it was run (e.g. `db-my_db-backup-2011-01-04-12-44.sql.tar.gz`) so you can easily grab a specific backup.


## Usage

Usage is strait forward, just put the `backupr.py` file on the `PythonPath` and then import it and run the `make_backup` method. Create a file somewhere that will call the `backupr.py` file, like your home folder (e.g. `/home/user/run_backups.py`):
    
    import os
    import sys
    
    # Add path to backupr.py file so we can import it.
    sys.path.append('/home/user/backupr/')
    
    import backupr
    
    backupr.make_backup('my_db_name', 
                'my_db_user', 
                'my_db_pass', 
                backup_path='/home/user/backups/',
                send_success_email=True,
                to_address='john@example.com', 
                gmail_user='myusername@gmail.com', 
                gmail_pw='mygmailpassword')
                

... where `'/home/user/backupr/'` is the path to the directory that contains the `backupr.py` file (your git checkout of python-backupr). Then, for safety, set the file permissions of `run_backups.py` to only allow your user full access and other users execute only access:

    chmod 711 ~/run_backups.py

You can now run:

    python ~/run_backups.py

... to make backups of your databases.

To make this script really useful, run it from a crontab. First, edit your crontab file:

    crontab -e

Then add in a crontab like this (note the first block is useful for referencing how to write a crontab job):

    # ------------- minute (0 - 59)
    # | ----------- hour (0 - 23)
    # | | --------- day of month (1 - 31)
    # | | | ------- month (1 - 12)
    # | | | | ----- day of week (0 - 6) (Sunday=0)
    # | | | | |
    # * * * * * command to be executed
    
    # Run database backup script.
    @daily /usr/local/bin/python2.6 ~/run_backups.py
    
    # Remove all backups that are 7 days old or older.
    @daily find ~/backups -mtime +6 -print | xargs rm

... where `/usr/local/bin/python2.6` is the location to your Python executable and `~/run_backups.py` is the path your `run_backups.py` file. This will run the `run_backups.py` file every night at midnight (server time). You can schedule backups however often you want using crontab.

If you enable success emails you'll get a nice email in your inbox every morning letting you know your backup was run successfully. It's nice to have peace of mind!


## Available Keywords Arguments

The available keyword options are as follows:
                
- `db_name` -- *String* -- *Required* -- The name of your database.
- `db_user` -- *String* -- *Required* -- The username of your database.
- `db_pw` -- *String* -- The password of your database. -- *Default: `''`*
- `db_host` -- *String* -- The host of your database. -- *Default: `'127.0.0.1'`*
- `backup_path` -- *String* -- The location you want to store the backup file. Can be relative (e.g. `'../foobar/'`) or absolute (e.g. `'/home/user/foobar/'`). Relative links will be relative to where the `backupr.py` file is located. -- *Default: `''`, which is the path of the `backupr.py` file*
- `send_success_email` -- *Boolean* -- Whether or not to send an email when a backup is successfully run. -- *Default: `False`*
- `to_address` -- *String* -- The address to send the success email to. Optional if no success email is desired. -- *Default: `None`*
- `gmail_user` -- *String* -- The GMail username (e.g. `'myusername@gmail.com'`) to use when sending the email. Optional if no success email is desired. -- *Default: `None`*
- `gmail_pw` -- *String* -- The GMail password for your account so we can send emails from GMail. Optional if no success email is desired. -- *Default: `None`*
- `remove_sql` -- *Boolean* -- Whether or not to keep the SQL dump after it has been compressed. This is useful if you have the need to run the SQL directly after a backup or for debugging. -- *Default: `True`*
- `attach_tar` -- *Boolean* -- Whether or not to attach the compressed tar file to the success email. -- *Default: `True`*


## Notes & Caveats

- Note that you can only call this on a machine that hosts the MySQL database, running it from a remote machine does not work.

- This method will give you some responses when running from the command line to let you know what it is doing.

- Both a plain text and HTML email are sent to be compatible with email clients that cannot handle HTML emails.

- This repo could be forked to add support for different email sending methods but since GMail is so ubiquitous and since it makes it so easy to send emails (without depending on the local machine to do it), I chose it as the method to send success emails from.


## To-Do

* Enable remote backups? (use scp or something?)


## License

Released under an MIT license.
