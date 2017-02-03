# HotelQuickly Test Assignment

### Questions
1. Please setup new Admin Server for OpenVPN server. It should route client traffic through the VPN only when client made a connection to the databases.
2. Please create ovpn file for us to test the connection.
3. Please setup the solution that clone production database to test databases every night. Put the running script in Admin Server and also github public repo.
4. Please provide us connection string for accessing databases. This connection should remain unchanged, even if the database has new clone.
5. Please make sure that the database could not be connected by world. It should be allow only access from OpenVPN and application servers.

## Solution

####1. Please set new Admin Server for OpenVPN server. It should route client traffic through the VPN only when client made a connection to the databases.

Steps:
1a) Create a new Server and attach an 'External IP' to it. This server needs a static external IP, so:

* The address does not change on reboot of the server, and
* So we can reassociate this address with a new machine, should we need to clone and replace the OpenVPN host.

This ensures the .opvn files stay correct. 

1b) Install OpenVPNas from openvpn.net (https://openvpn.net/index.php/access-server/download-openvpn-as-sw/113.html?osfamily=Debian)

On OpenVPN machine:

```
cd /tmp
wget http://swupdate.openvpn.org/as/openvpn-as-2.1.4-Debian8.amd_64.deb
(sudo) dpkg -i openvpn-as-2.1.4-Debian8.amd_64.deb
```

and follow the prompts (make sure to listen on all interfaces). When that's complete, change the passwd for the openvpn account.

```
sudo passwd openvpn
```

And then log into the OpenVPN server, at the IP address and port listed at the end of the installation process. 

Note: The IP address will probably be listed as the private IP, we change this once we log in, use the public IP of the instance. Also note that the OpenVPN server comes with a invalid certificate. For a real-world production environment, I would replace this with a valid certificate. 

If your browser mentions an invalid certificate, please select 'proceed/continue/accept' to load the OpenVPN page.


1c) Login to the OpenVPNas Server and Update settings <br />

Select the 'Login' Option on the drop down and log in.
(Username and Password to be sent via Email)
![Server_Login](https://cdn2.coconutsandpixels.com/hq/login_page.png)

Once Logged in, you can download either a pre-generated binary for your OS for OpenVPN client (with the opvn file installed, or the standalone opvn file).

Note: This was prepared already, but on a new installation you would need to update the server settings to point to the public, and not private IP addresses. I go through those steps below


![Server_Login_options](https://cdn3.coconutsandpixels.com/hq/login_page_options.png)

To set up OpenVPN to only accept incoming connections on its public IP address, click 'Admin' on the login_page (above) and login using the same username and password provided in the email.

Then click on the 'Server Network Settings' and change the *Hostname or Ip Address* setting to the public IP of the server. 

Once update the OpenVPN server will ask to reboot. Reboot it, and then you can download the Binaries or .opvn file from above.


![Server_settings](https://cdn3.coconutsandpixels.com/hq/server_network_settings.png)

Lastly, we need to ensure that only Internal (i.e Traffic going to the 



####2. Please create ovpn file for us to test the connection.<br />
Please find attached a copy of the opvn file in the email I have sent through with this submission. Alternatively the opvn can be downloaded using the intructions above in Step 1c.

####3. Please setup the solution that clone production database to test databases every night. Put the running script in Admin Server and also github public repo.

Before starting this question, I spent some thing thinking about it and checked the history of the Github commit for this assignment to ensure I had the question right.

I made the following assumptions:

* Both Databases were to be treated as independent (and not a master/slave situation)
* All databases (data) in both Databases (servers) had to be backedup and migrated to the backup Database each night
* The question changed from 'the script should continuously run every night. Applications and developers should always can access to test databases everyday, anytime.', So I am assuming that is no longer a requirement. If it is, my solution (cron + python) can be adjusted to run at a finer granularity (Say every 5mins) 

The ideal solution, I believe, would have been to use the gcloud cli/api to automate this process at a higher level. Unfortunately, the gcloud api permissions have been not configured to allow me access in this project, as per this response from the command line:

> ERROR: (gcloud.sql.instances.list) You do not have permission to access project [assignment-peter] (or it may not exist): Access Not Configured. Cloud SQL Administration API has not been used in project 561054032381 before or it is disabled.

> Enable it by visiting https://console.developers.google.com/apis/api/sqladmin/overview?project=561054032381 then retry. If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry.

I also considered the option that we use at my current job (clone the entire drive), but this was not suitable for two reasons:

1. No access to the cli/api, and
2. This assignment is using the managed SQL service from google, so there is no direct access to the 
OS of the operating system, or the drives. 

With these two options not viable, I was left with writing a script to dump the dumps both databases in their entirety and then restores them (essentially mysqldump and mysqlrestore).

This was a bit more difficult than expected due to the fact that Google's SQL offering doesn't allow 'SUPER' privileges to be created, and without 'SUPER' privileges, I am unable to lock the tables whilst taking a copy of them.

According to this article <a href'http://stackoverflow.com/questions/104612/run-mysqldump-without-locking-tables'>Run mysqldump without locking tables</a>, as long as the database engine is not running MyISAM, the --single-transaction switch can be used to avoid locking tables. 

This seemed like a good solution, so to check the DB's, I:

* Installed mysql-client on the OpenVPN machine (sudo apt-get install mysql-client)
* Logged into one of the test databases, and check the Database's

Unfortunately, the databases use a variety of different Engines for different tables. For example, the 'mysql' database, using the following

```
mysql> SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'mysql';
+---------------------------+--------+
| TABLE_NAME                | ENGINE |
+---------------------------+--------+
| columns_priv              | MyISAM |
| db                        | MyISAM |
| engine_cost               | InnoDB |
| event                     | MyISAM |
| func                      | MyISAM |
| general_log               | CSV    |
| gtid_executed             | InnoDB |
| heartbeat                 | MyISAM |
| help_category             | InnoDB |
| help_keyword              | InnoDB |
| help_relation             | InnoDB |
| help_topic                | InnoDB |
| innodb_index_stats        | InnoDB |
| innodb_table_stats        | InnoDB |
| ndb_binlog_index          | MyISAM |
| plugin                    | InnoDB |
| proc                      | MyISAM |
| procs_priv                | MyISAM |
| proxies_priv              | MyISAM |
| server_cost               | InnoDB |
| servers                   | InnoDB |
| slave_master_info         | InnoDB |
| slave_relay_log_info      | InnoDB |
| slave_worker_info         | InnoDB |
| slow_log                  | CSV    |
| system_user               | MyISAM |
| tables_priv               | MyISAM |
| time_zone                 | InnoDB |
| time_zone_leap_second     | InnoDB |
| time_zone_name            | InnoDB |
| time_zone_transition      | InnoDB |
| time_zone_transition_type | InnoDB |
| user                      | MyISAM |
+---------------------------+--------+
33 rows in set (0.00 sec)
```

Without the ability to use the gcloud api, clone drive, or use the --single-transaction switch in mysqldump, I was left with the option of writing a script to clone the DBs. This script could have been written in shell, but I find Python more flexible, so wrote it in that.

> Note: Please be aware that the schema databases won't be copied across. These are system level items so their omission should not affect anything.
> 
> This is because when I apply the --events switch to the mysqldump process it requests 'SUPER' access, which Google does not allow. Also, I can backup these files fine, but when I go to restore them, Google cannot restore due to needing 'SUPER' permissions. 
> Essentially Google are not allowing the modification of schema and system level databases (Which makes sense on a managed solution as these are vital to keeping the SQL service running).

So please note, test databases will be backed up fine, but system level ones will not be copied.


### The script

The script for dumping the databases, and restoring them to the backup server is in this repo, under 'hq_assignment.py'. Please make sure the folder it is in allows it to write files, as it dumps the mysql databases to the current directory before uploading to the backup server.

#####Usage Instructions: 
1. Ensure the mysql-client package is installed on the test machine (this script uses the mysqldump and mysql command line tools)
2. copy the config-sample.py file to config.py and enter in the required details
3. run the hq_assignment.py file:<br />
	Either as a normal python script "python hq_assignment.py" or
	As a shell script (change the file to executable 'sudo chmod +x hq_assignment.py'


#####What the script does:
1. Connects to the Databases, as per the config file, and gets a list of the databases in each (minus the core MySQL databases), and stores this in included.dbs
2. Dumps copies of those databases to the current working directory the script is in.
3. Modifies the database (and table) names to be <db_backup_name>-<original_name> so for a database on alice called test, the modified version would be alice-test. This is to ensure no conflict.

#####Running Times:
The script runs via the following cron parameters (where /opt/hq_test is the folder I saved it in):

```15 0-7 * * * python /opt/hq_test/hq_assignment.py > /opt/hq_test/hq_test_log.log```

This means it runs at 15minutes past the hour every hour from midnight to 7am, on my user account (grifforythms)

To see the cron, use this command "sudo crontab -u grifforythms -l" on the OpenVPN server.


####4. Please provide us connection string for accessing databases. This connection should remain unchanged, even if the database has new clone.

This has been sent via email. 



####5. Please make sure that the database could not be connected by world. It should be allow only access from OpenVPN and application servers.

External Access Attempt (To all DB's)

![External_to_SQL](https://cdn.coconutsandpixels.com/hq/external-to-sql.png)

No connection from an external IP was allowed.

#####From OpenVPN Server

![OpenVPN_to_SQL](https://cdn2.coconutsandpixels.com/hq/openvpn-sql.png)


####From Application-1

![appserver1_to_SQL](https://cdn3.coconutsandpixels.com/hq/app-server-1-sql.png)

###From Application-2
![appserver2_to_SQL](https://cdn4.coconutsandpixels.com/hq/app-server-2-sql.png)


**Note: I have limited access to the 'backup' database to the OpenVPN server only.**

This is because I don't want the "production" servers to be able to directly access the backup database. If it's blocked from doing so, I believe the solution is more secure. I can re-add the ability to connect from production to the backup DB by simply adding in a firewall rule to allow it. 

