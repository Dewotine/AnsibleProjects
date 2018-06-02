# Role: mysql

## Parameters

| Variable | Type | Description | Default |
| --- | --- | --- | --- |
| __mysql\_fork__ | str | |  |
| __mariadb\_version__ | str | | 10.1 |
| __mysql\_daemon__ | str | | mysql |
| __mysql\_user\_home__ | str | | /root |
| __mysql\_root\_username__ | str | | root |
| __mysql\_root\_password__ | str | | root |
| __mysql\_root\_password\_update__ | bool | | false |
| __mysql\_enabled\_on\_startup__ | bool | | true |
| __overwrite\_global\_mycnf__ | bool | | true |
| __mysql\_port__ | str | | 3306 |
| __mysql\_bind\_address__ | str | | 0.0.0.0 |
| __mysql\_datadir__ | str | | /var/lib/mysql |
| __mysql\_pid\_file__ | str | | /var/run/mysqld/mysqld.pid |
| __mysql\_skip\_name\_resolve__ | bool | | true |
| __mysql\_tmpdir__ | str | | /tmp |
| __mysql\_slow\_query\_log\_enabled__ | bool | | false |
| __mysql\_slow\_query\_log\_file__ | str | | {{ mysql_log_dir }}/mysql-slow.log |
| __mysql\_slow\_query\_time__ | str | | 2 |
| __mysql\_key\_buffer\_size__ | str | | 256M |
| __mysql\_key\_cache\_segments__ | str | | 0 |
| __mysql\_max\_allowed\_packet__ | str | | 64M |
| __mysql\_table\_open\_cache__ | str | | 256 |
| __mysql\_sort\_buffer\_size__ | str | | 1M |
| __mysql\_read\_buffer\_size__ | str | | 1M |
| __mysql\_read\_rnd\_buffer\_size__ | str | | 4M |
| __mysql\_myisam\_sort\_buffer\_size__ | str | | 64M |
| __mysql\_thread\_cache\_size__ | str | | 8 |
| __mysql\_query\_cache\_size__ | str | | 16M |
| __mysql\_query\_cache\_type__ | int | | 1 |
| __mysql\_query\_cache\_limit__ | str | | 1M |
| __mysql\_max\_connections__ | str | | 151 |
| __mysql\_tmp\_table\_size__ | str | | 16M |
| __mysql\_max\_heap\_table\_size__ | str | | 16M |
| __mysql\_join\_buffer\_size__ | str | | 256K |
| __mysql\_join\_buffer\_space\_limit__ | str | | 2M |
| __mysql\_lower\_case\_table\_names__ | str | | 0 |
| __mysql\_wait\_timeout__ | str | | 28800 |
| __mysql\_performance\_schema__ | bool | | true |
| __mysql\_thread\_pool\_size__ | int | | 4 |
| __mysql\_innodb\_file\_per\_table__ | str | | 1 |
| __mysql\_innodb\_buffer\_pool\_size__ | str | | 256M |
| __mysql\_innodb\_log\_file\_size__ | str | | 64M |
| __mysql\_innodb\_log\_buffer\_size__ | str | | 8M |
| __mysql\_innodb\_flush\_log\_at\_trx\_commit__ | str | | 2 |
| __mysql\_innodb\_lock\_wait\_timeout__ | str | | 50 |
| __mysql\_innodb\_thread\_concurrency__ | int | | 0 |
| __mysql\_innodb\_flush\_method__ | str | | O_DIRECT |
| __mysql\_innodb\_thread\_sleep\_delay__ | int | | 10000 |
| __mysql\_innodb\_large\_prefix__ | str | | 1 |
| __mysql\_innodb\_file\_format__ | str | | barracuda |
| __mysql\_mysqldump\_max\_allowed\_packet__ | str | | 64M |
| __mysql\_log\_dir__ | str | | /var/log/mysql |
| __mysql\_log__ | str | |  |
| __mysql\_log\_error__ | str | | {{ mysql_log_dir }}/mysql.err |
| __mysql\_syslog\_tag__ | str | | mysql |
| __mysql\_config\_include\_files__ | list | | [] |
| __mysql\_databases__ | list | | [] |
| __mysql\_users__ | list | | [] |
| __mysql\_server\_id__ | str | | 1 |
| __mysql\_max\_binlog\_size__ | str | | 100M |
| __mysql\_binlog\_format__ | str | | ROW |
| __mysql\_expire\_logs\_days__ | str | | 10 |
| __mysql\_replication\_role__ | str | | master |
| __mysql\_replication\_master__ | str | |  |
| __mysql\_replication\_user__ | list | | [] |

## Dependencies


## Examples
