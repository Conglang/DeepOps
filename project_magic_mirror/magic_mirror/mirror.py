# import gevent.monkey
# gevent.monkey.patch_all()

from app import app
from app import db
import database

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': database.models.User}


if __name__ == '__main__':
    app.run(debug=False, gevent=100)
    # app.run(debug=False, host='localhost', port=5000, master=True, processes=1)
    # uwsgi --master --http :5000 --http-websockets --wsgi mirror:app
    # https://github.com/keras-team/keras/issues/2397
    # https://github.com/zeekay/flask-uwsgi-websocket