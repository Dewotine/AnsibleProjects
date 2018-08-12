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

class PiwigoPermissionsManagement:
    def __init__(self, module, token, header, ansible_status, api_endpoint):
        self.module = module
        self.token = token
        self.header = header
        self.ansible_status = ansible_status
        self.api_endpoint = api_endpoint

    def request_piwigo_login(self):
        server_name = self.module.params["url"]
        my_url = server_name + self.api_endpoint
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
        my_url = server_name + self.api_endpoint
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
        my_url = self.module.params["url"] + self.api_endpoint
        url_method = "&method=pwg.session.logout"

        fetch_url(self.module,
                  my_url + url_method,
                  headers=self.header,
                  method="GET")

        if self.ansible_status['result'] == 'Changed':
            self.module.exit_json(changed=True, msg=self.ansible_status['message'])
        elif self.ansible_status['result'] == 'Unchanged':
            self.module.exit_json(changed=False, msg=self.ansible_status['message'])
        else:
            self.module.fail_json(msg=self.ansible_status['message'])



    def manage_permissions(self):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.permissions.add',
                  'cat_id' : self.module.params["cat_id"],
                  'group_id': self.module.params["group_id"],
                  'user_id ': self.module.params["user_id"],
                  'recursive': self.module.params["recursive"],
                  'pwg_token': self.token
                  }
        
        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo to set album permissions", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            self.module.exit_json(changed=False, msg=content)
            if content['stat'] == "ok":
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "User {0} succesfully added".format(self.module.params["username"])})
            else:
                self.module.fail_json(msg="Failed to set permissions", response=rsp, info=info)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cat_id=dict(required=True, type='list'),
            group_id=dict(required=False, type='list'),
            user_id=dict(required=False, type='list'),
            recursive=dict(required=False, default=False, type='bool'),
            url=dict(required=True, type='str'),
            url_username=dict(required=True, type='str'),
            url_password=dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
        required_together=[
            ["url_username", "url_password"],
        ]
    )

    piwigopermission = PiwigoPermissionsManagement(module,
                                      token="",
                                      header={'Content-Type': 'application/x-www-form-urlencoded'},
                                      ansible_status={'result': 'Fail',
                                                      'message': 'Could not get status of PiwigoPermissionsManagement module'},
                                      api_endpoint="/ws.php?format=json"
                                      )

    # Get cookie
    my_header = piwigopermission.request_piwigo_login()
    setattr(piwigopermission, 'header', my_header)

    # Get token for admin user
    my_token = piwigopermission.get_admin_status()
    setattr(piwigopermission, 'token', my_token)

    #Get cat id

    #Get User id

    #Get Group Id


    piwigopermission.manage_permissions()
    piwigopermission.finish_request()

if __name__ == '__main__':
    main()
