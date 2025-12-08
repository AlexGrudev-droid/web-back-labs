from lab5 import db_connect, db_close

from flask import Blueprint, render_template, request, abort, jsonify
from datetime import datetime

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')

# начальные данные – только для первичного заполнения БД
initial_films = [
    {
        'title': 'Snatch',
        'title_ru': 'Большой куш',
        'year': 2000,
        'description': 'Четырехпалый Френки должен был переправить \
        краденый алмаз из Англии в США своему боссу Эви. \
        Но вместо этого герой попадает в эпицентр больших \
        неприятностей. Сделав ставку на подпольном \
        боксерском поединке, Френки попадает в круговорот \
        весьма нежелательных событий.'
    },
    {
        'title': 'Tropic thunder',
        'title_ru': 'Солдаты неудачи',
        'year': 2008,
        'description': 'пародийная комедия, рассказывающая о группе \
        самовлюбленных актеров, снимающих дорогой фильм о войне \
        во Вьетнаме, которые случайно оказываются в настоящих джунглях и \
        вынуждены сражаться с реальными бандитами, думая, что это часть съемок. \
        Это сатира на голливудскую киноиндустрию, военные фильмы и звездную культуру, \
        с обилием черного юмора, абсурдных ситуаций и звездными камео.'
    },
    {
        'title': 'Interstellar',
        'title_ru': 'Интерстеллар',
        'year': 2014,
        'description': 'Когда засуха, пыльные бури и вымирание \
        растений приводят человечество к продовольственному \
        кризису, коллектив исследователей и учёных отправляется \
        сквозь червоточину (которая предположительно соединяет \
        области пространства-времени через большое расстояние) в \
        путешествие, чтобы превзойти прежние ограничения для \
        космических путешествий человека и найти планету с \
        подходящими для человечества условиями.'
    },
    {
        'title': 'Whiplash',
        'title_ru': 'Одержимость',
        'year': 2014,
        'description': 'Эндрю Ниман, амбициозный молодой джазовый \
        барабанщик, поступает в консерваторию, где попадает под \
        влияние Теренса Флетчера — жесткого и бескомпромиссного \
        преподавателя, чьи пугающие методы заставляют учеников \
        выходить за пределы своих возможностей. Их отношения \
        превращаются в психологическую битву, где стремление \
        к совершенству граничит с одержимостью.'
    },
    {
        'title': 'Parasite',
        'title_ru': 'Паразиты',
        'year': 2019,
        'description': 'Бедная корейская семья, живущая в полуподвале, \
        хитростью устраивается на работу в богатый дом клана Пак. \
        Они втираются в доверие к состоятельным хозяевам, но их \
        безоблачная жизнь неожиданно осложняется, когда обнаруживается \
        жуткая тайна в глубинах особняка.'
    }, 
]

def init_films_table():
    """Создаём таблицу films и заполняем её начальными данными, если она пустая."""
    conn, cur = db_connect()
    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS films (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                title_ru TEXT NOT NULL,
                year INTEGER NOT NULL,
                description TEXT NOT NULL
            )
        ''')
        # если таблица пустая – заполним начальными фильмами
        cur.execute('SELECT COUNT(*) FROM films')
        count = cur.fetchone()[0]
        if count == 0:
            for f in initial_films:
                cur.execute(
                    'INSERT INTO films (title, title_ru, year, description) '
                    'VALUES (?, ?, ?, ?)',
                    (f['title'], f['title_ru'], f['year'], f['description'])
                )
        conn.commit()
    finally:
        db_close(conn, cur)


@lab7.record_once
def init(state):
    with state.app.app_context():
        init_films_table()


def row_to_film(row):
    """Преобразование строки БД в словарь фильма."""
    return {
        'id': row[0],
        'title': row[1],
        'title_ru': row[2],
        'year': row[3],
        'description': row[4],
    }



@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    conn, cur = db_connect()
    try:
        cur.execute('SELECT id, title, title_ru, year, description FROM films ORDER BY id')
        rows = cur.fetchall()
    finally:
        db_close(conn, cur)
    return jsonify([row_to_film(r) for r in rows])


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    conn, cur = db_connect()
    try:
        cur.execute(
            'SELECT id, title, title_ru, year, description FROM films WHERE id = ?',
            (id,)
        )
        row = cur.fetchone()
    finally:
        db_close(conn, cur)

    if row is None:
        abort(404)

    return row_to_film(row)


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    conn, cur = db_connect()
    try:
        cur.execute('DELETE FROM films WHERE id = ?', (id,))
        deleted = cur.rowcount
        conn.commit()
    finally:
        db_close(conn, cur)

    if deleted == 0:
        abort(404)

    return '', 204


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    film = request.get_json()

    # русское название обязательно
    if film.get('title_ru', '').strip() == '':
        return {'title_ru': 'Заполните русское название'}, 400

    # автозаполнение оригинального названия
    if film.get('title', '').strip() == '':
        film['title'] = film['title_ru']

    # проверка года
    year = int(film.get('year', ''))
    current_year = datetime.now().year
    if year < 1895 or year > current_year:
        return {'year': f'Год должен быть от 1895 до {current_year}'}, 400

    # проверка описания
    description = film.get('description', '').strip()
    if description == '':
        return {'description': 'Заполните описание'}, 400
    if len(description) > 2000:
        return {'description': 'Описание не должно превышать 2000 символов'}, 400

    conn, cur = db_connect()
    try:
        cur.execute(
            'UPDATE films SET title = ?, title_ru = ?, year = ?, description = ? '
            'WHERE id = ?',
            (film['title'], film['title_ru'], year, description, id)
        )
        updated = cur.rowcount
        conn.commit()
    finally:
        db_close(conn, cur)

    if updated == 0:
        abort(404)

    film['id'] = id
    film['year'] = year
    film['description'] = description
    return film, 200


@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()

    # русское название обязательно
    if film.get('title_ru', '').strip() == '':
        return {'title_ru': 'Заполните русское название'}, 400

    # автозаполнение оригинального названия
    if film.get('title', '').strip() == '':
        film['title'] = film['title_ru']

    # проверка года
    year = int(film.get('year', ''))
    current_year = datetime.now().year
    if year < 1895 or year > current_year:
        return {'year': f'Год должен быть от 1895 до {current_year}'}, 400

    # проверка описания
    description = film.get('description', '').strip()
    if description == '':
        return {'description': 'Заполните описание'}, 400
    if len(description) > 2000:
        return {'description': 'Описание не должно превышать 2000 символов'}, 400

    conn, cur = db_connect()
    try:
        cur.execute(
            'INSERT INTO films (title, title_ru, year, description) '
            'VALUES (?, ?, ?, ?)',
            (film['title'], film['title_ru'], year, description)
        )
        new_id = cur.lastrowid
        conn.commit()
    finally:
        db_close(conn, cur)

    film['id'] = new_id
    film['year'] = year
    film['description'] = description

    return {"id": new_id, "film": film}, 201
