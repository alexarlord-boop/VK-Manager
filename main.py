import flask
import asyncio
import datetime
import os
import json
from requests import get
from flask_restful import reqparse, abort, Api, Resource
from api.pages_api import PageResource, PublicsListResource, GroupsListResource, EventsListResource
from flask import Flask, session
from flask import render_template, redirect
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from forms.login_form import LoginForm
from forms.filter import FilterForm
from forms.group_filter import GroupFilterForm
from forms.events_form import EventFilterForm
import vk_api
from vk_api import VkApiError

from data import db_session
from data.users import User

# from test_async import format_vk_event_date

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

vk = None


@login_manager.user_loader
def load_user(user_id):
    dbs = db_session.create_session()
    return dbs.query(User).get(user_id)


def get_group(group_id):
    group = vk.groups.getById(group_id=group_id,
                              fields=['activity', 'wall'])[0]
    group_id = group['id']
    group_act = group['activity']

    # print(group['activity'])

    group_name = group['name']
    group_photo = group[f'photo_100']

    group_data = {"id": group_id, "name": group_name, "activity": group_act, "photo": group_photo}

    return group_data


def preload(typ, count):
    """
    Предзагрука сообществ в данные о сессии.
    :param typ: тип сообщества
    :param count: количество предзагружаемых сообществ. Если -1, то загружает все сообщества.
    :param fields: поля фильтра сообществ
    :return:
    """
    print('preloading', typ)

    if count == 1:
        user_groups_id = vk.groups.get(filter=typ)
    else:
        user_groups_id = vk.groups.get(filter=typ, count=count)

    with open(f'data/pages/{typ}.txt', 'w') as f:
        for g_id in user_groups_id['items']:  # предзагрузка всех групп
            group = get_group(g_id)
            if group is None:
                continue

            f.write(f"{json.dumps(group)}\n")
            session[f'user_{typ}'].append(group)



def get_with_filter(typ, filter):
    print(typ)
    result = list()
    activity = filter.activity.data
    print(activity)
    pages = get(f'http://localhost:5000/api/v1/pages/{typ}/{activity}').json()['pages']

    return pages


@app.route('/login', methods=['GET', 'POST'])
def login():
    global vk

    form = LoginForm()
    if form.validate_on_submit():
        dbs = db_session.create_session()
        user = dbs.query(User).filter(User.login == form.email.data).first()
        if user:
            login_user(user)
        else:
            user = User()
            user.login = form.email.data
            user.set_password(form.password.data)

        # TOKEN = '1f0fe2dd1f0fe2dd1f0fe2dd6d1f7f630011f0f1f0fe2dd4175ea63ac4d725532953f49'

        vk_session = vk_api.VkApi(form.email.data, form.password.data, scope='groups')
        vk = vk_session.get_api()

        try:
            vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            print('vk_api:', error_msg)

        else:

            data = vk.users.get(fields=['photo_100'])[0]
            user.name = data['first_name']
            user.photo = data['photo_100']
            dbs.add(user)
            dbs.commit()
            login_user(user)

        session[f'user_publics'] = list()
        session[f'user_groups'] = list()
        session[f'user_events'] = list()

        return redirect('choice')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()

    for typ in ['publics', 'groups', 'events']:
        try:
            os.remove(f"data/pages/{typ}.txt")
        except Exception as e:
            print(e)

    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def intro():
    return render_template('main.html')


@app.route('/choice', methods=['GET', 'POST'])
def choice():
    print(session)
    main_choice = [{'title': 'Groups&Publics', 'link': '/vkg/filter/groups/1',
                    'img': 'https://avatars.mds.yandex.net/get-pdb/1848399/1348e1e6-0aab-4d3a-b7e0-3dedb221e434/s1200?webp=false'},
                   {'title': 'Events', 'link': '/vkg/filter/events/1',
                    'img': 'https://avatars.mds.yandex.net/get-pdb/1848399/1348e1e6-0aab-4d3a-b7e0-3dedb221e434/s1200?webp=false'}]
    return render_template('choice.html', cards=main_choice)


@app.route('/vkg/filter/<typ>/<int:count>', methods=['GET', 'POST'])
def filter(typ, count):
    forms = {'groups': FilterForm(), 'events': EventFilterForm()}
    form = forms[typ]

    try:
        if not os.path.exists(f"data/pages/{typ}.txt"):
            if typ == 'groups':
                preload('groups', count)
                preload('publics', count)
            else:
                preload('events', count)
        else:
            # применение фильтра
            fields = form
            filtered_groups = get_with_filter(typ, fields)
            return render_template('pages.html', title=typ, form=form, groups=filtered_groups)
    except Exception as e:
        print('FILTER ERROR:', e)

    return render_template('pages.html', title=typ, form=form, groups=session[f'user_{typ}'])


if __name__ == '__main__':
    db_path = "db/vkg.sqlite"
    db_session.global_init(db_path)
    dbs = db_session.create_session()

    api.add_resource(PublicsListResource, '/api/v1/pages/publics/<string:activity>')
    api.add_resource(PageResource, '/api/v1/pages/publics/<int:page_id>')

    api.add_resource(GroupsListResource, '/api/v1/pages/groups/<string:activity>')


    api.add_resource(EventsListResource, '/api/v1/pages/events/<string:activity>')
    app.run()
