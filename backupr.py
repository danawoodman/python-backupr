#!/usr/bin/python

import os
import datetime
import smtplib
import tarfile
import subprocess

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

# Function to print colors on the command line.
def color_print(msg, color=None):
    """
    Print colored console output.
    
    Color choices are: 
        'gray'
        'green'
        'red'
        'yellow'
        'purple'
        'magenta'
        'cyan'
    
    Example::
        color_print("Here is a message...", 'red')
    """
    if not msg:
        print "You must pass a message to the color_print function!"
        return
    
    # Declare closing.
    end = '\033[0m'
    
    # Declare print colors.
    colors = {
        'gray': '\033[90m',
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'purple': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
    }
    
    if color in colors.keys():
        print colors[color] + msg + end
    else:
        print msg

def mail(gmail_user, gmail_pw, to, subject='(No Subject)', text='', html=None, attach=None):
    """
    Send email through google.
    """
    if html:
        msg = MIMEMultipart('alternative')
    else:
        msg = MIMEMultipart()
    
    # Check to see if they entered a GMail user/password, which is required.
    if not gmail_user and not gmail_pw:
        print """You must supply a GMail username (gmail_user) and 
password (gmail_pw) to send an email!"""
        return
    
    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject
    
    if html:
        msg.attach(MIMEText(html, 'html'))
    
    msg.attach(MIMEText(text, 'text'))
    
    # Attach the file, if given.
    if attach:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attach, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
        msg.attach(part)
    
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pw)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
    
    # Log message to console.
    color_print('\nMessage sent!', 'green')
    color_print('    To: %s\n    Subject: %s' % (msg['To'], msg['Subject']), 'green')
    # print '%s' % msg.as_string()

def confirm(prompt=None, resp=False):
    """
    Prompts for yes or no response from the user. Returns True for yes and
    False for no.
    
    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.
    
    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True
    
    """
    
    if prompt is None:
        prompt = 'Confirm'
        
    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def make_backup(db_name, db_user, db_pw='', db_host='127.0.0.1', backup_path='', 
                send_success_email=False, to_address=None, gmail_user=None, 
                gmail_pw=None, remove_sql=True, attach_tar=True):
    """
    Make a backup of a MySQL database and send an email through a Gmail account.
    
    This method will create a SQL dump of the given MySQL database, tar the file 
    up and save the file.
    
    If `send_success_email` is set to `True` (default) it will send an email 
    notification of the successful backup to the `to_address`. If `to_address`, 
    `gmail_user` or `gmail_pw` are not set, then no email will be sent.
    
    If `remove_sql` is set to `True` (default), the SQL dump will be deleted 
    after the Tar file is created. If set to `False`, it will be stored to disk.
    
    Note that you can only call this on a machine that hosts the MySQL database, 
    running it from a remote machine does not work.
    
    This method will give you some responses when running from the command line 
    to let you know what it is doing.
    
    Both a plain text and HTML email are sent to be compatible with email 
    clients that cannot handle HTML emails.
    
    Example::
        make_backup('db_name', 
                    'db_user', 
                    'db_pass', 
                    backup_path='/home/user/backups/', 
                    send_success_email=True, 
                    to_address='john@example.com', 
                    gmail_user='example@gmail.com', 
                    gmail_pw='my_gmail_pass')
    
    """
    
    # Get current timestamp for the email message.
    now = datetime.datetime.now()
    now_string = now.strftime('%A, %B %d %Y at %I:%M %p') # e.g. Monday, December 31 2010 at 8:53 PM
    now_timestamp = now.strftime('%Y-%m-%d-%H-%M')
    
    # Expand the path so it is an absolute path, not relative.
    expanded_path = os.path.abspath(backup_path)
    
    # Create a timestamped backup file and set the directory we are saving things to.
    backup_string = 'db-%s-backup-%s' % (db_name, now_timestamp)
    backup_file_sql = '%s.sql' % backup_string
    backup_file_tar = '%s.tar.gz' % backup_file_sql
    backup_full_path_sql = os.path.join(expanded_path, backup_file_sql)
    backup_full_path_tar = os.path.join(expanded_path, backup_file_tar)
    
    # Make the backup folder.
    try:
        os.mkdir(expanded_path)
    except OSError, e:
        color_print("\nBackup directory already exists, skipping...", 'gray')
    
    # Construct the command.
    sub = "mysqldump \
            -u%(db_user)s%(db_pass)s \
            --add-locks \
            --flush-privileges \
            --add-drop-table \
            --complete-insert \
            --extended-insert \
            --single-transaction \
            --database %(db_name)s > %(backup_path)s" % {
                'db_user': db_user, 
                'db_pass': " -p" + db_pw if db_pw != '' else '', 
                'db_name': db_name, 
                'backup_path': backup_full_path_sql
            }
    
    # Check the subprocess call and catch exceptions. 
    subprocess.check_call(sub, shell=True)
    
    # Dump the data.
    subprocess.call(sub, shell=True)
    
    # print '\nRunning command:\n%s' % sub
    color_print('\nDumped MySQL database to: %s' % backup_full_path_sql, 'green')
    
    # Create the tar.gz archive.
    tar = tarfile.open(backup_full_path_tar, 'w:gz')
    tar.add(backup_full_path_sql, backup_file_sql, recursive=False) # Don't save the directories, just the SQL file...
    tar.close()
    
    color_print('\nCreated archive at: %s' % backup_full_path_tar, 'green')
    
    # Delete the SQL file.
    if remove_sql:
        try:
            os.remove(backup_full_path_sql)
            color_print('\nDeleted SQL file: %s' % backup_full_path_sql, 'green')
        except OSError, e:
            color_print('\nError removing SQL file: %s' % e, 'red')
    
    # Construct the email subject.
    email_subject = 'Backup of "%s" successfully run!' % (db_name)
    
    # Construct email messages.
    msg_text = """Dear Master,\n\nYour backup of the database '%(db_name)s' on %(when)s ran successfully!

The back up is stored on the server here:\n %(backup_path)s %(attachment_message)s

Love,
Your Robotic Servant""" % {
                'db_name': db_name, 
                'when': now_string, 
                'backup_path': os.path.abspath(backup_full_path_tar), 
                'attachment_message': '\n\nThe backup is also attached to this email.' if attach_tar else ''
            }
    msg_html = """
    
    <p><em>Dear Master,</em></p>
    
    <p>Your backup of the database '<em>%(db_name)s</em>' on <strong>%(when)s</strong> ran successfully!</p>
    
    <p>
        The back up is stored on the server here: <br />
        <em>%(backup_path)s</em>
    </p>
    
    %(attachment_message)s
    
    <p><em>Love,</em></p>
    
    <p><strong>Your Robotic Servant</strong></p>
    
    """ % {
                'db_name': db_name, 
                'when': now_string, 
                'backup_path': os.path.abspath(backup_full_path_tar), 
                'attachment_message': '\n\nThe backup is also attached to this email.' if attach_tar else ''
            }
    
    # Send message.
    if send_success_email and to_address and gmail_user and gmail_pw:
        mail(gmail_user, gmail_pw, to_address, email_subject, 
            msg_text, msg_html, backup_full_path_tar if attach_tar else '')
    
    color_print("\nYour backup is complete!\n", 'green')

