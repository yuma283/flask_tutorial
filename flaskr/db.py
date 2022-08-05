import sqlite3

import click
#gはリクエスト毎の特有な特別オブジェクトでデータを蓄えるために使われる
#current_appはリクエストに対処するFlaskのapplicationを指している(今回は__init.py__のapp)
from flask import current_app, g 
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
      #DATABASEの構成キーによって指されているファイルへのコネクションを作成
      g.db = sqlite3.connect(
        current_app.config['DATABASE'],
        detect_types=sqlite3.PARSE_DECLTYPES
        )
      #辞書のように振る舞うRowsを返すようにコネクションに伝える
      g.db.row_factory = sqlite3.Row

    return g.db


#g.bdが設定されているかチェックし、コネクションが作られていたかどうかチェックする
def close_db(e=None):
    db = g.pop('db', None)
    #コネクションが存在したら閉じる
    if db is not None:
        db.close()
       
 
def init_db():
    db = get_db()

    #appと相対的なファイルを開く。(appはinstance file(sqlite file)と相対的であると設定している)
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

#click.command()は、init_db関数を呼び出してユーザーに成功メッセージを表示する'init-db'というコマンドラインコマンドを定義
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    
def init_app(app):
    app.teardown_appcontext(close_db) #反応を返した後にクリーンアップするときにclose_db関数を呼び出すようにFlaskに指示
    app.cli.add_command(init_db_command) #フラスクコマンドで呼び出すことができる新しいコマンドを追加