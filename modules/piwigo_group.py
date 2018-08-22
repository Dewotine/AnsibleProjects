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
                  'group_id': self.get_groupid(self.module.params["name"]),
                  'user_id[]': self.get_id_list(self.module.params['user_list'], "username"),
                  'pwg_token': self.token
                  }

        my_data = urllib.urlencode(values, True)

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
                # Always changed, can't get the list of users to compare before and after....
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "group {0} succesfully added with user(s) {1}".format(self.module.params["name"],
                                                                              self.module.params['user_list'])})

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
            elif (content['stat'] == "fail") and (content['message'] == "This name is already used by another group."):
                setattr(self, 'ansible_status', {'result': 'Unchanged', 'message':
                        "group {0} already existing".format(self.module.params["name"])})
            else:
                self.module.fail_json(msg="An error occured while creating group {0}".format(self.module.params["name"]))

    def delete_group(self, group_id):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.groups.delete',
                  'group_id': group_id,
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
                        "group {0} succesfully deleted".format(self.module.params["name"])})
            else:
                self.module.fail_json(msg="An error occured while deleting group {0}".format(self.module.params["name"]))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            user_list=dict(required=False, type='list', default=[]),
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

    group_id = piwigogroup.get_groupid(piwigogroup.module.params["name"])

    if module.params['state'] == 'present':
        if group_id < 0:
            piwigogroup.create_group()
        else:
            setattr(piwigogroup, 'ansible_status',
                    {'result': 'Unchanged',
                     'message': 'Group {0} already existing'.format(module.params['name'])})
        if len(module.params['user_list']) != 0:
            piwigogroup.add_user_to_group()
    else:
        if group_id > 0:
            piwigogroup.delete_group(group_id)
        else:
            setattr(piwigogroup, 'ansible_status',
                    {'result': 'Unchanged',
                     'message': 'No group {0} found'.format(module.params['name'])})

    piwigogroup.finish_request()


if __name__ == '__main__':
    main()
