import flask
import asyncio
import datetime
import os
import json
from requests import get, delete
from flask_restful import reqparse, abort, Api, Resource
from api.pages_api import PublicResource, PageResource, PublicsListResource, GroupsListResource, EventsListResource
from flask import Flask, session, jsonify
from flask import render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from forms.login_form import LoginForm
from forms.filter import FilterForm
from forms.page_form import PageForm
from forms.events_form import EventFilterForm
import vk_api
from vk_api import VkApiError

from data import db_session
from data.users import User

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


def get_group(group_ids):
    group_ids = ','.join(list(map(str, group_ids)))
    # print(group_ids)
    groups = vk.groups.getById(group_ids=group_ids,
                               fields=['activity', 'description', 'status'])
    # print(groups)
    return groups


def preload(typ, count):
    """
    Предзагрука сообществ в данные о сессии.
    :param typ: тип сообщества
    :param count: количество предзагружаемых сообществ.
    :param fields: поля фильтра сообществ
    :return:
    """
    print('preloading', typ)

    if count == 'all':
        user_groups_id = vk.groups.get(filter=typ)['items']
    else:
        user_groups_id = vk.groups.get(filter=typ, count=int(count))['items']

    groups = get_group(user_groups_id)
    # print(user_groups_id)
    with open(f'data/pages/{typ}.txt', 'w') as f:
        for group in groups:
            f.write(f"{json.dumps(group)}\n")
            # session[f'user_{typ}'].append(group)
            # f.write(group)


def get_gnp_with_filter(activ):
    print('getting gnp with filter')
    activity = activ
    # print(activity)
    groups = get(f'http://localhost:5000/api/v1/pages/groups/{activity}').json()['pages']
    publics = get(f'http://localhost:5000/api/v1/pages/publics/{activity}').json()['pages']
    # print('GROUPS:', groups)
    groups.extend(publics)
    pages = groups
    # print('PAGES:', pages)
    return pages


def get_events_with_filter(activ):
    print('getting events with filter')
    activity = activ
    # print('activity:', activity)

    pages = get(f'http://localhost:5000/api/v1/pages/events/{activity}').json()['pages']
    print(pages)

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

        vk_session = vk_api.VkApi(form.email.data, form.password.data, scope='groups')
        # vk_session = vk_api.VkApi(form.email.data, scope='groups')
        vk = vk_session.get_api()

        try:
            print('vk response ', vk_session.auth(token_only=True))
        except vk_api.AuthError as error_msg:
            print('vk_api:', error_msg)
            return render_template('login.html', form=form)

        else:

            data = vk.users.get(fields=['photo_100'])[0]
            user.name = data['first_name']
            user.photo = data['photo_100']
            dbs.add(user)
            dbs.commit()
            login_user(user)

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

    try:
        os.remove('api/deleted.txt')
    except Exception as e:
        print(e)

    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def intro():
    return render_template('main.html')


@app.route('/choice', methods=['GET', 'POST'])
def choice():
    # print(session)

    for title in list(filter(lambda x: not os.path.exists(f"data/pages/{x}.txt"), ['groups', 'publics', 'events'])):
        preload(title, 'all')

    # move links into static
    main_choice = [{'title': 'Группы', 'link': '/vkg/filter/groups/all',
                    'img': 'https://avatars.mds.yandex.net/get-pdb/1848399/1348e1e6-0aab-4d3a-b7e0-3dedb221e434/s1200?webp=false'},
                   {'title': 'События', 'link': '/vkg/filter/events/all',
                    'img': 'https://avatars.mds.yandex.net/get-pdb/1848399/1348e1e6-0aab-4d3a-b7e0-3dedb221e434/s1200?webp=false'}]

    return render_template('choice.html', cards=main_choice)


@app.route('/vkg/filter/<typ>/<count>', methods=['GET', 'POST'])
def filt(typ, count):
    forms = {'groups': FilterForm(), 'events': EventFilterForm()}
    filt = forms[typ]
    titles = {'groups': 'Группы', 'events': 'События'}

    print(filt.activity.data)
    activ = filt.activity.data
    print(typ)

    if request.method == 'POST':
        return redirect(f"/filtered_pages/{typ}/{activ}/{count}")

    return render_template('gnp.html', typ=titles[typ], form=filt)


@app.route('/filtered_pages/<typ>/<activ>/<count>', methods=['GET', 'POST'])
def filtered_pages(typ, activ, count):
    page_form = PageForm()
    keys = {'all': 'Все', 'кино': 'Кино', 'прогр': 'Программирование',
            'юмор': 'Юмор', 'образ': 'Образование',
            'курс': 'Курсы', 'игр': 'Игры', 'спорт': 'Спорт',
            'медицин': 'Медицина', 'дизайн': 'Дизайн',
            '0': 'Прошедшие', '1': 'Скоро будут'}

    if page_form.validate_on_submit():  # DELETING PAGE
        p_id = int(page_form.p_id.data)
        print(p_id)
        print(delete(f'http://localhost:5000/api/v1/pages/{page_form.p_id.data}').json())

        print('delete', vk.groups.leave(group_id=p_id))

    preload(typ, 'all')
    if typ == 'groups':
        filtered_groups = get_gnp_with_filter(activ)
    else:
        filtered_groups = get_events_with_filter(activ)

    count = len(filtered_groups)
    title = keys[activ]
    return render_template('pages.html', count=count, typ=typ, title=title,
                           page=page_form, groups=filtered_groups)


if __name__ == '__main__':
    db_path = "db/vkg.sqlite"
    db_session.global_init(db_path)
    dbs = db_session.create_session()

    api.add_resource(PublicsListResource, '/api/v1/pages/publics/<string:activity>')
    api.add_resource(PageResource, '/api/v1/pages/<int:p_id>')

    api.add_resource(GroupsListResource, '/api/v1/pages/groups/<string:activity>')

    api.add_resource(EventsListResource, '/api/v1/pages/events/<string:activity>')
    app.run()
