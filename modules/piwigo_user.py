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
- hosts: localhost
  become: true
  vars:
    my_piwigo_user:
      user1:
        password: "password1"
        email: "essai10@gmail.com"
      user2:
        password: "password2"
        email: "essai20@gmail.com"
      ratatouille:
        password: "password3"
        email: "essai40@gmail.com"
  tasks:
    - name: "Create a list of user"
      piwigo_user:
        name: "{{ item.key }}"
        password: "{{ item.value.password }}"
        email: "{{ item.value.email }}"
        send_password_by_mail: false
        url_username: "piwigo_admin"
        url_password: "xxx"
        url: "http://localhost:8080"
        state: "present"
      with_dict: "{{ my_piwigo_user }}"
    - name: "Create a user with extra attributes"
      piwigo_user:
        name: "mytest"
        password: "password"
        email: "mynewtest@gamil.com"
        group:
          - testgroup
          - testgroup2
        level: 1
        status: "admin"
        url_username: "piwigo_admin"
        url_password: "xxx"
        url: "http://localhost:8080"
        state: "present"
    - name: "Delete a user"
      piwigo_user:
        name: "user2"
        url_username: "piwigo_admin"
        url_password: "xxx"
        url: "http://localhost:8080"
        state: "absent"
    - name: "Modify a user"
      piwigo_user:
        name: "user1"
        email: "newessai10@gmail.com"
        state: "present"
        url_username: "piwigo_admin"
        url_password: "xxx"
        url: "http://piwigo.bleschet.fr:8080"
'''

RETURN = '''
results:
    description: Detailed user creation with a dictionnaty which indicates affected rows. 
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
                self.module.fail_json(msg="An error occured while deleting user {0}"
                                      .format(self.module.params["name"]))

     def set_user_info(self, user_id, group_id):
         my_url = self.module.params["url"] + self.api_endpoint
         values = {'method': 'pwg.users.setInfo',
                   'user_id': user_id,
                   'group_id[]': group_id,
                   'email': self.module.params["email"],
                   'level': self.module.params["level"],
                   'status': self.module.params["status"],
                   'pwg_token': self.token
                   }
         my_data = urllib.urlencode(values, True)

         rsp, info = fetch_url(self.module,
                               my_url,
                               data=my_data,
                               headers=self.header,
                               method="POST")

         if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to create a category", response=rsp,
                                   info=info)
         else:
             content = json.loads(rsp.read())
             if content['stat'] == "ok":
                 setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                     "User {0} succesfully created with extra attributes".format(self.module.params["name"])})
             else:
                 self.module.fail_json(
                     msg="An error occured while setting attributes to user {0}".format(self.module.params["name"]))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            password=dict(required=False, type='str', no_log=True),
            email=dict(required=False, type='str'),
            group=dict(required=False, type='list', default=[]),
            level=dict(required=False, type='int', default=0),
            send_password_by_mail=dict(required=False, default=False, type='bool'),
            status=dict(required=False, type='str', choices=['guest', 'generic', 'normal', 'admin', 'webmaster'],
                        default='normal'),
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

    # Search the user id (-1 if absent)
    my_user_id = piwigouser.get_userdict(module.params['name'])['user_id']
    # Declare tempooratry variable to retain new user id (after creation) and group id list (they must exist)
    my_new_user_id = -1
    my_group_id_list = []
    # declare temporary variables t obe able to detect change in user
    my_previous_user = {}
    my_new_user = {}
    my_diff_user = {}

    if module.params['state'] == 'present':
        if my_user_id < 0:
            piwigouser.create_user()
            if len(module.params['group']) != 0 or module.params['level'] != 0 or module.params['status'] != "normal":
                if len(module.params['group']) != 0:
                    my_group_id_list = piwigouser.get_id_list(module.params['group'], "group")
                my_new_user_id = piwigouser.get_userdict(module.params['name'])['user_id']
                piwigouser.set_user_info(my_new_user_id, my_group_id_list)
        else:
            my_previous_user = piwigouser.get_userdict(piwigouser.module.params["name"])
            piwigouser.set_user_info(my_user_id, my_group_id_list)
            my_new_user = piwigouser.get_userdict(piwigouser.module.params["name"])
            my_diff_user = piwigouser._dictdiff(my_previous_user, my_new_user)

            if len(my_diff_user.keys()) == 0:
                setattr(piwigouser, 'ansible_status',
                        {'result': 'Unchanged',
                         'message': 'No change for user {0} detected'.format(piwigouser.module.params["name"])})
            else:
                setattr(piwigouser, 'ansible_status',
                        {'result': 'Changed',
                         'message': 'Change for user {0} detected : {1}'.format(piwigouser.module.params["name"],
                                                                                   my_diff_user)})
    elif module.params['state'] == 'absent':
        if my_user_id < 0:
            setattr(piwigouser, 'ansible_status',
                    {'result': 'Unchanged',
                     'message': 'No user {0} found'.format(piwigouser.module.params["name"])})
        else:
            piwigouser.delete_user(my_user_id)

    piwigouser.finish_request()


if __name__ == '__main__':
    main()
