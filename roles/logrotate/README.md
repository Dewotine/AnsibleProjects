# Role: logrotate

## Parameters

| Variable | Type | Description | Default |
| --- | --- | --- | --- |
| __logrotate\_conf\_dir__ | str | Logrotate configuration directory | /etc/logrotate.d/ |
| __logrotate\_scripts__ | dict | Logrotate rules | {} |
| __logrotate\_rotation\_days__ | int | Global rotation days | 14 |

## Examples

Setting up logrotate for additional Nginx logs, with postrotate script (assuming this role is located in `roles/logrotate`).

```
logrotate_scripts:
- name: nginx
  path: /var/log/nginx/*.log
  options:
	- weekly
	- size 25M
	- rotate 7
	- missingok
	- compress
	- delaycompress
	- copytruncate
  scripts:
	postrotate: "[ -s /run/nginx.pid ] && kill -USR1 `cat /run/nginx.pid`"
```

## License

[BSD](https://raw.githubusercontent.com/nickhammond/logrotate/master/LICENSE)

## Author Information

* [nickhammond](https://github.com/nickhammond) | [www](http://www.nickhammond.com) | [twitter](http://twitter.com/nickhammond)
* [bigjust](https://github.com/bigjust)
* [steenzout](https://github.com/steenzout)
* [jeancornic](https://github.com/jeancornic)
* [duhast](https://github.com/duhast)
* [kagux](https://github.com/kagux)
