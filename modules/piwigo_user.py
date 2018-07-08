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
from ansible.module_utils.urls import fetch_url
import json
import urllib
import urllib2
import base64


class PiwigoUserManagement:
    def __init__(self, module):
        self.module = module

    def request_piwigo_login(self):
        server_name = self.module.params["url"]
        api_endpoint = "/ws.php?format=json"
        my_url = server_name + api_endpoint
        my_header = { 'Content-Type': 'application/json',}
        session = {}
        values = { 'method': 'pwg.session.login',
                   'username': self.module.params["url_username"], 'password': self.module.params["url_password"] }
        my_data = urllib.urlencode(values)


        # Get connnexion
        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              method="POST")

        if info["status"] != 200:
            self.module.fail_json(msg="Failed to connect to piwigo", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                # self.module.exit_json(changed=True, results=info['cookies']['pwg_id'])
                self.module.exit_json(changed=True, results=info)
                data = {"response": {"status": "Login OK"}}
            else:
                # data = {"response": {"status": "fail", "err": {"msg": content}}}
                self.module.fail_json(msg=content)


        # # Get Token
        # url_method = "&method=pwg.session.getStatus"
        # rsp2, info2 = fetch_url(self.module,
        #                       my_url + url_method,
        #                       method="GET")
        #
        # if info2["status"] != 200:
        #     self.module.fail_json(msg="Failed to get session information from piwigo", response=rsp2, info=info2)
        # else:
        #     session=json.loads(rsp2.read())
        #     self.module.exit_json(changed=True, results=session)
        #
        # return info['cookies']['pwg_id']

    def create_user(self, token):
        server_name = self.module.params["url"]
        api_endpoint = "/ws.php"
        my_url = server_name + api_endpoint
        my_header = {'Content-Type': 'application/json', }
        values = {'method': 'pwg.users.add',
                  'username': 'test', ''
                  'password': 'retest',
                  'password_confirm': 'retest',
                  'email': '',
                  'send_password_by_mail': False,
                  'pwg_token': token }

        my_data = urllib.urlencode(values)

        # # Add User
        # rsp, info = fetch_url(self.module,
        #                       my_url,
        #                       data=my_data,
        #                       method="POST")
        #
        # if info["status"] != 200:
        #     self.module.fail_json(msg="Failed to connect to piwigo in order to add user", response=rsp, info=info)
        # else:
        #     content = rsp.read()
        #     if 'stat=\"ok\"' in content.lower():
        #         data = {"response": {"status": "Login OK"}}
        #     else:
        #         # data = {"response": {"status": "fail", "err": {"msg": content}}}
        #         self.module.fail_json(msg=content)

        self.module.exit_json(changed=False, results=token)

def main():
    token = ""
    module = AnsibleModule (
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            username=dict(required=True, type='str'),
            password=dict(required=False, type='str'),
            password_confirm=dict(required=False, type='str'),
            email = dict(required=False, type='str'),
            send_password_by_mail=dict(required=False, default=False, type='bool'),
            url=dict(required=True, type='str'),
            url_username=dict(required=True, type='str'),
            url_password=dict(required=True, type='str'),
        ),
        supports_check_mode=True,
        required_together=[
            ["password", "password_confirm"],
            ["url_username", "url_password"],
        ]
    )

    piwigouser = PiwigoUserManagement(module)
    token = piwigouser.request_piwigo_login()

    if module.params['state'] == 'present':
        piwigouser.create_user(token)
    # elif module.params['state'] == 'absent':
    #     piwigouser.delete_user()


if __name__ == '__main__':
    main()
