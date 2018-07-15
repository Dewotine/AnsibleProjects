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
    def __init__(self, module, token, header, ansible_status):
        self.module = module
        self.token = token
        self.header = header
        self.ansible_status = ansible_status

    def request_piwigo_login(self):
        server_name = self.module.params["url"]
        api_endpoint = "/ws.php?format=json"
        my_url = server_name + api_endpoint
        my_header = {}
        values = {'method': 'pwg.session.login',
                  'username': self.module.params["url_username"],
                  'password': self.module.params["url_password"]}

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
            if content['stat'] != "ok":
                self.module.fail_json(msg=content)
            else:
                my_header = {
                    'Cookie': info['set-cookie']
                }

        return my_header

    def get_admin_status(self):
        my_token = ""
        server_name = self.module.params["url"]
        api_endpoint = "/ws.php?format=json"
        my_url = server_name + api_endpoint
        url_method = "&method=pwg.session.getStatus"

        rsp, info = fetch_url(self.module,
                              my_url + url_method,
                              headers=self.header,
                              method="GET")
        if info["status"] != 200:
            self.module.fail_json(msg="Failed to get session information from Piwigo", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            my_token = content['result']['pwg_token']

        return my_token

    def finish_request(self):
        api_endpoint = "/ws.php?format=json&method=pwg.session.logout"
        my_url = self.module.params["url"] + api_endpoint

        fetch_url(self.module, my_url, headers=self.header, method="GET")

        if self.ansible_status['result'] == 'Changed':
            self.module.exit_json(changed=True, msg=self.ansible_status['message'])
        elif self.ansible_status['result'] == 'Unchanged':
            self.module.exit_json(changed=False, msg=self.ansible_status['message'])
        else:
            self.module.fail_json(msg=self.ansible_status['message'])



    def create_user(self):
        api_endpoint = "/ws.php?format=json&method=pwg.users.add"
        my_url = self.module.params["url"] + api_endpoint
        values = {'username': self.module.params["username"],
                  'password': self.module.params["password"],
                  'password_confirm': self.module.params["password_confirm"],
                  'email': self.module.params["email"],
                  'send_password_by_mail':  self.module.params["send_password_by_mail"],
                  'pwg_token': self.token
                  }
        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to add user", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "User {0} succesfully added".format(self.module.params["username"])})
            elif content['stat'] == "fail" and content['err'] == 1003:
                if 'e-mail' in content['message']:
                    setattr(self, 'ansible_status', {'result': 'Failed', 'message': content})
                else:
                    setattr(self, 'ansible_status', {'result': 'Unchanged', 'message':
                        "User {0} already exists".format(self.module.params["username"])})



def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            username=dict(required=True, type='str'),
            password=dict(required=False, type='str', no_log=True),
            password_confirm=dict(required=False, type='str', no_log=True),
            email=dict(default='', type='str'),
            send_password_by_mail=dict(required=False, default=False, type='bool'),
            url=dict(required=True, type='str'),
            url_username=dict(required=True, type='str'),
            url_password=dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
        required_together=[
            ["password", "password_confirm"],
            ["url_username", "url_password"],
        ]
    )

    piwigouser = PiwigoUserManagement(module,
                                      token="",
                                      header={'Content-Type': 'application/x-www-form-urlencoded'},
                                      ansible_status={'result': 'Fail',
                                                      'message': 'Could not get status of PiwigoUserManagement module'}
                                      )

    # Get cookie
    my_header = piwigouser.request_piwigo_login()
    setattr(piwigouser, 'header', my_header)

    # Get token for admin user
    my_token = piwigouser.get_admin_status()
    setattr(piwigouser, 'token', my_token)

    if module.params['state'] == 'present':
        piwigouser.create_user()
    # elif module.params['state'] == 'absent':
    #     piwigouser.delete_user()

    piwigouser.finish_request()

if __name__ == '__main__':
    main()
