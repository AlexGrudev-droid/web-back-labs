from flask import Blueprint, render_template, request, abort, jsonify

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')

films = [
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


@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return jsonify(films)


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    if 0 <= id < len(films):
        return films[id]
    else:
        abort(404)


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if 0 <= id < len(films):
        del films[id]
        return '', 204
    else:
        abort(404)


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    if 0 <= id < len(films):
        film = request.get_json()
        if film.get('title', '') == '' and film.get('title_ru', '') != '':
            film['title'] = film['title_ru']
        if film['description'] == '':
            return {'description': 'Заполните описание'}, 400
        films[id] = film
        return films[id], 200
    else:
        abort(404)


@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    if film.get('title', '') == '' and film.get('title_ru', '') != '':
        film['title'] = film['title_ru']
    if film.get('description', '') == '':
        return {'description': 'Заполните описание'}, 400
    films.append(film)
    new_index = len(films) - 1
    return {"id": new_index, "film": film}, 201
