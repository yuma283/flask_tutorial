#ブループリント（設計図）は関連するビューやその他のコードのグループを編成する方法
#Flaskrには、認証機能用(authentication)とブログ投稿機能用（blog post）の2つの設計図がある
#各ブループリントのコードは個別のモジュールに配置される。ブログは認証について知る必要があるため、最初に認証を記述する。
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

#authという名前のBlueprintを作成
#appオブジェクトと同様に、bpはそれが定義されている場所を知る必要があるため、__name__が2番目の引数として渡される。
#url_prefix は、ブループリントに関連付けられたすべてのURLの先頭に追加される。
bp = Blueprint('auth', __name__, url_prefix='/auth')


#1つ目のview:Register
#/auth/registerに訪れたuserに登録フォームのHTMLを表示する
#入力を検証しフォームを再度表示してエラーメッセージを表示するか、新しいユーザーを作成してログインページに移動
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')
  
  
#Login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password): #入力されたpasswordとuserの[password]が一致するか
            error = 'Incorrect password.'

        #sessionはdictでリクエストを渡ってデータを蓄える
        #userのidはsession[user_id]に保存
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')
  
  
#@bp.before~は要求されたURLに関係なく、view関数の前に実行される関数を登録
#この関数はユーザーIDがセッションに保存されているかどうかを確認し,データベースからそのユーザーのデータを取得して要求の間持続するg.userに保存する。
#ユーザーIDがない場合、またはIDが存在しない場合、g.userはNoneになる。
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
       
       
#Logout 
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
  
  
#ページの更新をした際などにlogin状態かどうかチェックする(元々のviewをwrapする新しいview関数を返す)
#loginしてなかったらloginページにリダイレクト
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view