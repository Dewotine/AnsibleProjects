# Role: apache

## Parameters

| Variable | Type | Description | Default |
| --- | --- | --- | --- |
| __apache\_config\_path__ | str | | /etc/apache2 |
| __apache\_log\_path__ | str | | /var/log/apache2 |
| __apache\_package\_name__ | str | | apache2 |
| __apache\_manage\_service__ | bool | | true |
| __apache\_service\_name__ | str | | apache2 |
| __apache\_service\_enable__ | bool | | true |
| __apache\_server\_admin__ | str | | admin@example.org |
| __apache\_listening\_ip__ | str | | * |
| __apache\_listening\_port__ | int | | 80 |
| __apache\_server\_tokens__ | str | | Prod |
| __apache\_server\_signature__ | str | | Off |
| __apache\_trace\_enable__ | str | | Off |
| __apache\_protect\_vcs\_directories__ | bool | | true |
| __apache\_prevent\_clickjacking__ | bool | | false |
| __apache\_mpm\_worker__ | dict | | {'start_servers': 2, 'min_spare_threads': 25, 'max_spare_threads': 75, 'thread_limit': 64, 'threads_per_child': 25, 'max_connections_per_child': 0} |
| __apache\_mpm__ | dict | | {'server_limit': 16, 'max_request_workers': 150, 'listen_backlog': 511} |
| __apache\_modules__ | list | | [] |
| __apache\_jk\_method__ | str | | Busyness |
| __apache\_jk\_workers__ | dict | | {} |
| __apache\_mod\_svn\_enable__ | bool | | false |
| __apache\_vhosts__ | list | | [] |
| __apache\_log\_formats__ | dict | | {} |
| __apache\_log\_formats\_default__ | str | | combined |
| __apache\_catchall\_virtualhost__ | bool | | false |
| __apache\_catchall\_virtualhost\_httpcode__ | int | | 404 |
| __apache\_catchall\_virtualhost\_logformat__ | str | | combined |
| __apache\_enable\_localhost\_virtualhost__ | bool | | false |


## Dependencies

  * logrotate

## Examples


## Managing Apache modules

You can use apache_modules variables to enable modules and apache.modules_blacklist for disable modules.

Warning: On Debian, default installed modules are not modified by this playbook.

```
apache_modules:
  - {name: cgid,        state: absent}
  - {name: mpm_event,   state: absent}
  - {name: status,      state: absent}

  - {name: deflate,     state: present}
  - {name: jk,          state: present}
  - {name: mime,        state: present}
  - {name: mpm_worker,  state: present}
  - {name: negotiation, state: present}
  - {name: reqtimeout,  state: present}
  - {name: rewrite,     state: present}
```

The following modules will trigger a package installation:

* mod_jk
* mod_auth_pgsql

Other modules installation aren't supported at this moment, don't hesistate to do a PR

## Managing Apache virtualhosts

You can manage your virtualhosts using the apache_vhosts variable.

Here is the exhaustive list of config variables:

* ip (optionnal, default apache_listening_ip): apache listening IP
* port (optionnal, default apache_listening_port): apache listening port
* server_name: virtualhost domain name
* server_aliases (optionnal, default None): list of virtualhost domain name aliases
* log_path (optional, default apache_log_path): log folder where store apache logs for this vhost
* document_root (optionnal, default /var/www/<vhost_name>)
* custom_log_format (optionnal, default combined): log output format for CustomLog
* indexes (optionnal, default -indexes): Document root indexes
* allowed_hosts (optionnal, default undefined): List of allowed IP who can use this DocumentRoot, if specified, else everybody
* allow_override (optionnal, default None): Allow overriding Apache configuration for DocumentRoot Directory
* document_root_fragment (optionnal, default ''): A custom raw apache configuration for DocumentRoot Directory
* rewrite_rules (optionnal, default undefined): List of Rewrite Rules to apply on this vhost with the following item attributes. Applied only if mod_rewrite is enabled

  * condition (optionnal): Rewrite rule condition
  * pattern: Pattern to match
  * dest: Rule to apply

* disallowed_path_regex (optionnal, default undefined): List of forbidden paths to protect. This uses a rewrite rule and a regex matching. Applied only if mod_rewrite is enabled
* disallowed_files (optionnal, default undefined): List of forbidden files to protect.
* deflate_compression_level (optionnal, default 9): mod_deflate compression level. Applied only if mod_deflate is enabled
* deflate_by_type (optionnal, default undefined): List of mime types to compress with deflate. Applied only if mod_deflate is enabled.
* expire_by_type (optionnal, default undefined): List of file types with a rule expire rule. Applied only if mod_expires is enabled
* proxy_preserve_host (optionnal, default Off): Preserve requested host when calling the backend server
* proxy_pass (optionnal, default undefined): List of reverse proxy objects with the following parameters. Applied only if mod_proxy is enabled

  * path: local path to map
  * url: backend URL to call

* jk_mounts (optionnal, default undefined): List of JkMount/JkUnMount directives to apply. Applied only if mod_jk is enabled.

  * path: path to send/ignore
  * mount (optionnal, default true): set to false to do a JkUnMount
  * worker: jk worker group to use
```
apache_vhosts:
  - name: "wordpress_front"
    server_admin: "no-reply@crazy-app.example"
    server_name: "wordpress_front.crazy-app.example"
    deflate_by_type:
      - image/*
      - text/css
    expire_by_type:
      'image/png':
        rule: "access plus 1 day"
    jk_mounts:
      - { path: "/*", worker: "cluster01" }
      - { path: "/static", mount: false, worker: "cluster01" }
      - { path: "/ext", mount: true, worker: "cluster02" }
```

## Managing JK workers

You can manage your mod_jk workers using the apache_jk_workers variable. 
This variable needs a list of workers and each worker awaits a list of nodes

If you want to change the load balancing method, you can change globally the apache_jk_method (default is Busyness) 
or per worker using the method attribute in your worker
```
apache_jk_workers:
  group_amazing_app:
	nodes:
	  io_tomcat_01: { ip: 10.0.0.1 }
	  io_tomcat_02: { ip: 10.0.0.2 }
```

## Managing apache security

By default this module configure some apache security. You can configure apache.security keys to set some global security values

* server_tokens (default: Prod): OS type & compiled modules
* server_signature (default: Off): Server version & virtualhost name
* trace_enable (default: Off)
* prevent_clickjacking (default: false): add X-Frame-Options: "sameorigin" header to prevent content embedded on other sites
* protect_vcs_directories (default: true): forbid access to .svn and .git directories
```
apache_server_tokens: 'Prod'
apache_server_signature: 'Off'
apache_trace_enable: 'Off'
apache_prevent_clickjacking: false
apache_protect_vcs_directories: true
```
