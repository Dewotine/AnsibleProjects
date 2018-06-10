<?php
$conf['dblayer'] = 'mysqli';
$conf['db_base'] = 'piwigo';
$conf['db_user'] = '{{ mariadb_piwigo_installation_users.name }}';
$conf['db_password'] = '{{ mariadb_piwigo_installation_users.password }}';
$conf['db_host'] = 'localhost';

$prefixeTable = 'piwigo_';

define('PHPWG_INSTALLED', true);
define('PWG_CHARSET', 'utf-8');
define('DB_CHARSET', 'utf8');
define('DB_COLLATE', '');

?>