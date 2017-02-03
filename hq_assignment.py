#!/usr/bin/env python

import os
import sys
import time
import fileinput
from config import *

def dumpDatabases():
	'''
	Name: dumpDatabases
	Description: This function reads from the DATABASES_FROM config dictionary, filters the output to non-system databases, and 
		     shells out to the mysqldump program to dump the remaining databases to a file called '<servername>.sql' where server name
		     is the game given to that item in the dictionary. For example 'alice' would output to 'alice.sql'

		     This script has to filter the core databases as, on restore, these require SUPER privileges to work, and Google Cloud disallows SUPER.
		     This is understandable as SUPER is a very powerful ability, and could kill Databases. More infromation here: 
			https://dev.mysql.com/doc/refman/5.7/en/privileges-provided.html
		     
		     Information about SUPER of Google Cloud here: http://ronaldbradford.com/blog/i-want-a-mysqldump-ignore-database-option-2012-04-18/
	'''

	for items in DATABASES_FROM:
		skipDump = False
		name, ip, port, username, password = items, DATABASES_FROM[items]['ip'], DATABASES_FROM[items]['port'], DATABASES_FROM[items]['username'], DATABASES_FROM[items]['password']

		strip_core='mysql -u %s -p%s -h %s -e "SHOW DATABASES" | grep -v Database | grep -v mysql | grep -v information_schema | grep -v performance_schema | grep -v sys | tr "\n" " " > included.dbs' % (username, password, ip)
		exclude_databases = os.system(strip_core)

		try:
			included_list = open('included.dbs', 'r')
			for line in included_list:
				included=line

			backupcmd =  "mysqldump -h %s -u %s -p%s --databases %s --skip-lock-tables > %s.sql" % (ip,username,password,included,name)
			result = os.system(backupcmd)

			if result > 0:
				print "An error has occurred, please check the error message above. Program aborted"	
				sys.exit()

		except UnboundLocalError:
			print "[Backup] No non-system databases to migrate on %s. Skipping" % items
			skipDump = True

		if not skipDump:
			print '[Backup] backing up %s' % name


def restoreDatabaseDumps():
        '''
        Name: restoreDatabaseDumps
        Description: This function runs directly after dumpDatabases. It looks for a sql file (i.e alice.sql) that has the same name as one of the configuration items
		     and if it exists. It attempts to restore the dump back to the backup server.
        '''

	for items in DATABASES_FROM:
		filename = "%s.sql" % items
		try:
			file = open(filename,'r+')
			print "[Restore] Restoring %s to backup" % items

			name, ip, port, username,password = items, DATABASES_TO['backup']['ip'], DATABASES_TO['backup']['port'], DATABASES_TO['backup']['username'],DATABASES_TO['backup']['password']
			backupcmd = "mysql -h %s -u %s -p%s < %s" % (ip,username,password,filename)
			print 'Restoring DB'	
			os.system(backupcmd)

		except IOError:	# File doesn't exist. Most likely that database does not have non-system databases and was skipped by the dumpDatabase() method
			pass

		print '[Restore] Restore for %s to backup complete' % items



if __name__ == '__main__':
	"""
	Name: Not a function, This is the main entrypoint into the script. 

	Description: This calls each method in turn to run them. This could have also been written as one big block with no methods; However, this is much cleaner.

	Methods:
		* dumpDatabases() - Connects to each Database in turn and dumps the SQL to a file with the filename:	<server_name>.sql (alice.sql, brandy.sql)
		* restoreDatabaseDumps() - Connects to the backup Database and uploads the Dumps to it. 

	"""
	print "---- BACKUP STARTED AT %s ----" % time.strftime("%c") 

	dumpDatabases()  # Dump all of the databases in each Database to file.
	restoreDatabaseDumps() 

	# Script End
	print "---- BACKUP COMPLETED AT %s ---- " % time.strftime("%c")
	

