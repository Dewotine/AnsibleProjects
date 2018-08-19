#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.pywigo_management import *
import json
import urllib

DOCUMENTATION='''
module: piwigo_group
author: Cédric Bleschet
description: Module to declare group in piwigo
options:
  name:
    description: group name
    required: yes
  password:
    description:group Password
    required: false
'''

EXAMPLES='''
- name: "Insert Piwigo group"
  pywigo_group:
    name: "test"
'''

RETURN = '''
results:
    description: group status
'''

class PiwigoGroupManagement(PiwigoManagement):
    def add_user_to_group(self):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.groups.addUser',
                  'group_id': self.get_group_id(self.module.params["name"]),
                  'user_id': self.get_userid_list(self.module.params['user_list'])
                  }

        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to add group", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            self.module.exit_json(changed=False, msg=content)
            if content['stat'] == "ok":
                self.module.exit_json(changed=False, msg=content)

    def create_group(self):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.groups.add',
                  'name': self.module.params["name"],
                  'is_default': self.module.params["is_default"],
                  'pwg_token': self.token
                  }
        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")


        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to add group", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "group {0} succesfully added".format(self.module.params["name"])})
            elif content['stat'] == "fail" and content['err'] == 1003:
                if 'e-mail' in content['message']:
                    setattr(self, 'ansible_status', {'result': 'Failed', 'message': content})
                else:
                    setattr(self, 'ansible_status', {'result': 'Unchanged', 'message':
                        "group {0} already exists".format(self.module.params["name"])})


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            user_list=dict(required=False, type='list', default=""),
            is_default=dict(required=False, default=False, type='bool'),
            url=dict(required=True, type='str'),
            url_username=dict(required=True, type='str'),
            url_password=dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
        required_together=[
            ["url_username", "url_password"],
        ]
    )

    piwigogroup = PiwigoGroupManagement(module,
                                      token="",
                                      header={'Content-Type': 'application/x-www-form-urlencoded'},
                                      ansible_status={'result': 'Fail',
                                                      'message': 'Could not get status of PiwigogroupManagement module'},
                                      api_endpoint="/ws.php?format=json"
                                      )

    # Get cookie
    my_header = piwigogroup.request_piwigo_login()
    setattr(piwigogroup, 'header', my_header)

    # Get token for admin group
    my_token = piwigogroup.get_admin_status()
    setattr(piwigogroup, 'token', my_token)

    if module.params['state'] == 'present':
        piwigogroup.create_group()
        if len(module.params['user_list']) != 0:
            piwigogroup.add_user_to_group()
    # elif module.params['state'] == 'absent':
    #     piwigogroup.delete_group()

    piwigogroup.finish_request()

if __name__ == '__main__':
    main()
