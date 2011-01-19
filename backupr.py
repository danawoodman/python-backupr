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
    print '\nMessage sent!'
    print '    To: %s\n    Subject: %s' % (msg['To'], msg['Subject'])
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
    """
    try:
        
        # Get current timestamp for the email message.
        now = datetime.datetime.now()
        now_string = now.strftime('%A, %B %d %Y at %I:%M %p') # e.g. Monday, December 31 2010 at 8:53 PM
        
        # Create a timestamped backup file and set the directory we are saving things to.
        backup_string = 'db-%s_backup_%s' % (db_name, now.strftime('%Y-%m-%d-%H-%M'))
        backup_file_sql = '%s.sql' % backup_string
        backup_file_tar = '%s.tar.gz' % backup_file_sql
        backup_full_path_sql = '%s%s' % (backup_path, backup_file_sql)
        backup_full_path_tar = '%s%s' % (backup_path, backup_file_tar)
        
        # Make the backup folder.
        try:
            os.mkdir(backup_path)
        except:
            pass
        
        # Construct the command.
        sub = 'mysqldump -u%s -p%s --add-locks --flush-privileges --add-drop-table \
--complete-insert --extended-insert --single-transaction --database %s > %s' % (db_user, db_pw, db_name, backup_full_path_sql)
        
        # Dump the data.
        subprocess.call(sub, shell=True)
    
        print '\nDumping MySQL database to: %s' % backup_full_path_sql
        
        print '\nRunning command:\n%s' % sub
        
        # Create the tar.gz archive.
        tar = tarfile.open(backup_full_path_tar, 'w:gz')
        tar.add(backup_full_path_sql, backup_file_sql, recursive=False) # Don't save the directories, just the SQL file...
        tar.close()
        
        print '\nCreated archive at: %s' % backup_full_path_tar
        
        # Delete the SQL file.
        if remove_sql:
            try:
                os.remove(backup_full_path_sql)
                print '\nDeleted SQL file: %s' % backup_full_path_sql
            except e:
                print '\nError removing SQL file: %s' % e
        
        # Construct email messages.
        msg_text = """Dear Master,\n\nYour backup of the database '%s' on %s ran successfully!

The back up is stored here:\n %s %s

Love,
Your Robotic Servant""" % (db_name, now_string, 
                                os.path.abspath(backup_full_path_tar), 
                                '\n\nThe backup is also attached to this email.' if attach_tar else '')
        msg_html = """
        
        <p><em>Dear Master,</em></p>
        
        <p>Your backup of the database '<em>%s</em>' on <strong>%s</strong> ran successfully!</p>
        
        <p>
            The back up is stored here: <br />
            <em>%s</em>
        </p>
        
        %s
        
        <p><em>Love,</em></p>
        
        <p><strong>Your Robotic Servant</strong></p>
        
        """ % (db_name, now_string, os.path.abspath(backup_full_path_tar), 
                '<p>The backup is also attached to this email.</p>' if attach_tar else '')
        
        # Send message.
        if send_success_email and to_address and gmail_user and gmail_pw:
            mail(gmail_user, gmail_pw, to_address, 'Backup successfully run!', 
                msg_text, msg_html, backup_full_path_tar if attach_tar else '')
        
        print "\nYour backup is complete!\n"
        
    except:
         print 'Shit done broke...'

