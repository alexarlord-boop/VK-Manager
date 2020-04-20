import os
import json
from flask_restful import abort, Api, Resource
from flask import jsonify
from requests import get
import datetime
from vkdata import format_vk_event_date
from data import db_session
from data.users import User
from api.parser import parser


def abort_if_users_not_found(page_id):
    res = None
    with open(f"data/pages/publics.txt") as f:
        data = f.readlines()
        for page in data:
            page = json.loads(page)
            print(page)
            if int(page_id) == int(page['id']):
                res = page
    if res is None:
        abort(404, message=f"User {page_id} not found")


class PageResource(Resource):
    def delete(self, p_id):  # doesn`t work
        with open('api/deleted.txt', 'a+') as f:
            try:
                f.write(f"{p_id}\n")
            except Exception as e:
                return jsonify({'status': 'error'})
            else:
                return jsonify({'status': 'OK!'})


class PublicResource(Resource):  # возможно не работает корректно!
    def get(self, p_id):
        print(p_id)
        res = None
        abort_if_users_not_found(p_id)
        with open(f"data/pages/publics.txt") as f:
            data = f.readlines()
            for page in data:
                page = json.loads(page)
                # print(page)
                if p_id == page['id']:
                    res = page
        return jsonify({'page': res})




class PublicsListResource(Resource):
    def get(self, activity):
        res = list()
        with open(f"data/pages/publics.txt") as f:
            data = f.readlines()
            for page in data:
                page = json.loads(page)
                page_name_list = page['name'].lower().split()
                if page in res:
                    continue
                if activity == 'all':
                    res.append(page)

                elif activity in page['activity'].lower():

                    print(page)
                    res.append(page)

        return jsonify({'pages': res})


class GroupsListResource(Resource):
    def get(self, activity):
        res = list()
        with open(f"data/pages/groups.txt") as f:
            data = f.readlines()
            for page in data:
                page = json.loads(page)
                if page in res:
                    continue
                if activity == 'all':
                    res.append(page)

                elif activity in page['name'].lower().split():
                    # print(page)
                    res.append(page)

        return jsonify({'pages': res})


class EventsListResource(Resource):
    def get(self, activity):
        res = list()
        with open(f"data/pages/events.txt") as f:
            data = f.readlines()
            for page in data:
                page = json.loads(page)

                if activity == 'all':
                    res.append(page)

                now = datetime.datetime.now().date()
                # print(now, format_vk_event_date(group['activity']))
                # print(activity)
                if now > format_vk_event_date(page['activity']) and activity == '0':
                    print('yes 0')
                    res.append(page)
                elif now < format_vk_event_date(page['activity']) and activity == '1':
                    res.append(page)

        return jsonify({'pages': res})
    # подключить ресурс в мэйн
