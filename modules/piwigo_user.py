#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION='''
module: piwigo_user
author: Cédric Bleschet
description: Module to declare users in piwigo
options:
  username:
    description: User name
    required: yes
  password:
    description:User Password
    required: false
'''

EXAMPLES='''
- name: "Insert Piwigo user"
  pywigo_user:
    username: "test"
    pwg_token: "gdgjdklfjgmfld"
'''

RETURN = '''
results:
    description: user status
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url
import json


class PiwigoUserManagement:
    def __init__(self, module):
        self.module = module

    # def request_piwigo_login(self):
    #     # rsp, info = fetch_url(module=self.module, url=self.module.params["url"], data=None)
    #     # if not rsp or info['status'] >= 400:
    #     #     self.module.fail_json(msg="failed to connect (status code %s), error was %s" % (
    #     #     info['status'], info.get('msg', 'no error given')))
    #
    #     my_data = { "method": "pwg.session.login", "username": "piwigo_admin", "password": "hfhfhfgf" }
    #     my_header = {
    #         'Content-Type': 'application/json',
    #     }
    #
    #     my_url = "http://piwigo.bleschet.fr:8080/ws.php?"
    #     rsp, info = fetch_url(module=self.module,
    #                           url=my_url,
    #                           data=self.module.jsonify(my_data),
    #                           headers=my_header,
    #                           method="POST")
    #
    #     if info["status"] != 200:
    #         self.module.fail_json(msg="Failed to  connect to piwigo", response=rsp, info=info)
    #     # else:
    #     #     self.module.fail_json(msg="Failed to  connect to piwigo", info=info)
    #
    #     # my_url2 = "http://piwigo.bleschet.fr:8080/ws.php?format=json&method=pwg.session.getStatus"
    #     # rsp2, info2 = fetch_url(module=self.module,
    #     #                       url=my_url2,
    #     #                      method="POST")
    #
    #     # if info2["status"]:
    #     #     self.module.fail_json(msg="Failed to  connect to piwigo", response=rsp, info=info)
    #
    #     # https://fossies.org/linux/ansible/lib/ansible/module_utils/urls.py
    #     # https://www.programcreek.com/python/example/99757/ansible.module_utils.urls.fetch_url
    #     # https://github.com/fraoustin/piwigo

    def request_piwigo_login(self):
        my_url = "http://piwigo.bleschet.fr:8080/ws.php?&method=pwg.session.login"
        my_data = {"username": "piwigo_admin", "password": "hfhfhfgf"}
        rsp = open_url(my_url, self.module.jsonify(my_data), method="POST")
        rsp_json = json.loads(rsp.read())
        if rsp_json["total"] == 0:
            module.fail_json(msg="Environment %s not found." % env_name)

def main():
    module = AnsibleModule (
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            username=dict(required=True, type='str'),
            password=dict(required=False, type='str'),
            password_confirm=dict(required=False, type='str'),
            email = dict(required=False, type='str'),
            send_password_by_mail=dict(required=False, default=False, type='bool'),
            url=dict(required=True, type='str'),
            admin_user=dict(required=True, type='str'),
            admin_password=dict(required=True, type='str'),
        ),
        supports_check_mode=True,
        required_together=[
            ["password", "password_confirm"],
            ["admin_user", "admin_password"],
        ]
    )

    piwigouser = PiwigoUserManagement(module)
    piwigouser.request_piwigo_login()
    # if module.params['state'] == 'present':
    #     piwigouser.create_user()
    # elif module.params['state'] == 'absent':
    #     piwigouser.delete_user()


    module.exit_json(changed=False, results="test de module")


if __name__ == '__main__':
    main()
