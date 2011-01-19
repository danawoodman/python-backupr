# python-backupr

## Description

Make a backup of a MySQL database and send an (optional) success email through a GMail account.

This method will create a SQL dump of the given MySQL database, tar (compress) the file up and save the file to the local file system. 

Depending on the options you pass it, it will delete the SQL dump after your compress it and send you a (cute) email letting you know what happened and where the file was saved. The email will also have the Tar file attached to it so you have a backup on your email server in addition to the local file system.

The backups are named with the name of the DB, and the timestamp it was run so you can easily grab a specific backup.


## Usage

Usage is strait forward, just put the `backupr.py` file on the `PythonPath` and then import it and run the `make_backup` method:

    import backupr
    
    backupr.make_backup('my_db_name', 
                'my_db_user', 
                'my_db_pass', 
                to_address='john@example.com', 
                gmail_user='myusername@gmail.com', 
                gmail_pw='mygmailpassword')


## Available Keywords

The available keyword options are as follows:
                
- `db_name` -- *Required* -- The name of your database.
- `db_user` -- *Required* -- The username of your database.
- `db_pw` -- The password of your database. -- *Default: `''`*
- `db_host` -- The host of your database. -- *Default: `'127.0.0.1'`*
- `backup_path` -- The location you want to store the backup file. Can be relative (e.g. `../foobar/` or absolute `/home/user/foobar/`) -- *Default: `''`*
- `send_success_email` -- Whether or not to send an email when a backup is successfully run. -- *Default: `False`*
- `to_address` -- The address to send the success email to. Optional if no success email is desired. -- *Default: `None`*
- `gmail_user` -- The GMail username (e.g. `'myusername@gmail.com`) to use when sending the email. Optional if no success email is desired. -- *Default: `None`*
- `gmail_pw` -- The GMail password for your account so we can send emails from GMail. Optional if no success email is desired. -- *Default: `None`*
- `remove_sql` -- Whether or not to keep the SQL dump after it has been compressed. This is useful if you have the need to run the SQL directly after a backup or for debugging. -- *Default: `True`*


## Notes & Caveats

Note that you can only call this on a machine that hosts the MySQL database, running it from a remote machine does not work.

This method will give you some responses when running from the command line to let you know what it is doing.

Both a plain text and HTML email are sent to be compatible with email clients that cannot handle HTML emails.

This repo could be forked to add support for different email sending methods but since GMail is so ubiquitous and since is makes it so easy to send emails from (without depending on the local machine to do it), I chose it as the method to send success emails from.


## To-Do

* Have an option to not attach the Tar file to the email (especially useful on big DBs).
* Enable remote backups? (use scp or something?)


## License

Released under and MIT license.
