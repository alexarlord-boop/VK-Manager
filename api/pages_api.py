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
    def delete(self, p_id):
        print('DELETE', p_id)
        with open('api/deleted.txt', 'w+') as f:
            data = f.readlines()
            print(data)
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

                elif activity in page['activity'].lower() or activity in page['name'].lower().split():

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
                now = datetime.datetime.now().date()
                vk_d = format_vk_event_date(page['activity'])
                if now > vk_d:
                    page['was'] = 1
                else:
                    page['was'] = 0
                if activity == 'all':

                    res.append(page)

                    #print(now, format_vk_event_date(page['activity']))


                # print(activity)
                else:

                    if (now > vk_d) and (str(activity) == '0'):
                        page['was'] = 1
                        res.append(page)
                    elif (now < vk_d) and (activity == '1'):
                        page['was'] = 0
                        page['date'] = vk_d
                        res.append(page)

        if res:
            return jsonify({'pages': res})
        else:
            return jsonify({'error'})
    # не работает добавление ключей
