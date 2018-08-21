#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.pywigo_management import *
import json
import urllib

DOCUMENTATION='''
module: piwigo_user
author: Cédric Bleschet
description: Module to declare users in piwigo
options:
  name:
    description: User name
    required: yes
  password:
    description:User Password
    required: false
'''

EXAMPLES='''
- name: "Insert Piwigo user"
  pywigo_user:
    name: "test"
'''

RETURN = '''
results:
    description: user status
'''

class PiwigoUserManagement(PiwigoManagement):
     def create_user(self):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.users.add',
                  'username': self.module.params["name"],
                  'password': self.module.params["password"],
                  'password_confirm': self.module.params["password"],
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
                        "User {0} succesfully added".format(self.module.params["name"])})
            elif content['stat'] == "fail" and content['err'] == 1003:
                if 'e-mail' in content['message']:
                    setattr(self, 'ansible_status', {'result': 'Failed', 'message': content})
                else:
                    setattr(self, 'ansible_status', {'result': 'Unchanged', 'message':
                        "User {0} already exists".format(self.module.params["name"])})

     def delete_user(self, user_id):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.users.delete',
                  'user_id': user_id,
                  'pwg_token': self.token
                  }
        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to delete user", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "User {0} succesfully deleted".format(self.module.params["name"])})
            else:
                self.module.fail_json(msg="An error occured while deleting user {0}".format(module.params["name"]))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=True, type='str', choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            password=dict(required=False, type='str', no_log=True),
            email=dict(required=False, type='str'),
            group_name=dict(required=False, type='list', default=[]),
            level=dict(required=False, type='int', default=0),
            send_password_by_mail=dict(required=False, default=False, type='bool'),
            status=dict(type='str', choices=['guest', 'generic', 'normal', 'admin', 'webmaster'], default='guest'),
            url=dict(required=True, type='str'),
            url_username=dict(required=True, type='str'),
            url_password=dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
        required_together=[
            ["url_username", "url_password"],
        ]
    )

    piwigouser = PiwigoUserManagement(module,
                                      token="",
                                      header={'Content-Type': 'application/x-www-form-urlencoded'},
                                      ansible_status={'result': 'Fail',
                                                      'message': 'Could not get status of PiwigoUserManagement module'},
                                      api_endpoint="/ws.php?format=json"
                                      )

    # Get cookie
    my_header = piwigouser.request_piwigo_login()
    setattr(piwigouser, 'header', my_header)

    # Get token for admin user
    my_token = piwigouser.get_admin_status()
    setattr(piwigouser, 'token', my_token)

    my_user_id = piwigouser.get_userdict(module.params['name'])['user_id']

    if module.params['state'] == 'present':
        piwigouser.create_user()
    elif module.params['state'] == 'absent':
        if my_user_id < 0:
            piwigouser.module.exit_json(changed=False, msg="No user {0} found".format(module.params['name']))
        else:
            piwigouser.delete_user(my_user_id)

    piwigouser.finish_request()

if __name__ == '__main__':
    main()
