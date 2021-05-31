import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_pymongo_db(with_session=True):
    from hospital_management.utils.mongo_handler import MongoHandler
    if 'db' not in g:
        g.db = MongoHandler(
            with_session=with_session
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close_client()


def init_db():
    pass


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_test_db():
    from hospital_management.utils.mongo_handler import MongoHandler
    db = MongoHandler(with_session=False)
    return db
