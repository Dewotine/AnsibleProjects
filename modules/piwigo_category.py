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
'''

RETURN = '''
results:
    description: user status
'''

class PiwigoCategoryManagement(PiwigoManagement):
    def create_category(self):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.categories.add',
                  'name': self.module.params["name"],
                  'parent': self.module.params["parent"],
                  'comment': self.module.params["comment"],
                  'visible': self.module.params["visible"],
                  'status':  self.module.params["status"],
                  'commentable': self.module.params["commentable"],
                  }
        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to create a category", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "Category {0} succesfully added".format(self.module.params["name"])})
            else:
                self.module.fail_json(msg="Failed to create Category", response=rsp, info=info)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            parent=dict(required=False, type='int', default=0),
            comment=dict(required=False, default='', type='str'),
            visible=dict(required=False, default=True, type='bool'),
            status=dict(type='str', choices=['public', 'private'], default='private'),
            commentable=dict(required=False, default=True, type='bool'),
            url = dict(required=True, type='str'),
            url_username = dict(required=True, type='str'),
            url_password = dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
        required_together=[
            ["url_username", "url_password"],
        ]
    )

    piwigocategory = PiwigoCategoryManagement(module,
                                      token="",
                                      header={'Content-Type': 'application/x-www-form-urlencoded'},
                                      ansible_status={'result': 'Fail',
                                                      'message': 'Could not get status of PiwigoCategoryManagement module'},
                                      api_endpoint="/ws.php?format=json"
                                      )

    # Get cookie
    my_header = piwigocategory.request_piwigo_login()
    setattr(piwigocategory, 'header', my_header)

    # Get token for admin user
    my_token = piwigocategory.get_admin_status()
    setattr(piwigocategory, 'token', my_token)

    if module.params['state'] == 'present':
        piwigocategory.create_category()
    # elif module.params['state'] == 'absent':
    #     piwigocategory.delete_user()

    piwigocategory.finish_request()

if __name__ == '__main__':
    main()
