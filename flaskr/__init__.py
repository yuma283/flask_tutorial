import os

from flask import Flask


def create_app(test_config=None): #application factory function(って何??)
  # create and configure the app
  #appはFlaskのinstance,instance_relative_config=Trueは構成ファイルがinstance folderに対して相対的であるということ
  #from_mapping→appがよく用いるデフォルトの構成を設定
  app = Flask(__name__, instance_relative_config=True) 
  app.config.from_mapping(
      SECRET_KEY='dev',
      DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'), #app.instance_pathはFlaskが選んだinstance folder(flaskr.sqliteがinstance folder名)
  )

  if test_config is None:
      # load the instance config, if it exists, when not testing
      #instance folder内のconfig.pyが存在する場合は、そこから取得した値で既定の構成をオーバーライド(デプロイ時に、これを使用して実際のSECRET_KEYを設定できる)
      app.config.from_pyfile('config.py', silent=True) 
  else:
      # load the test config if passed in
      app.config.from_mapping(test_config)

  # ensure the instance folder exists
  try:
      os.makedirs(app.instance_path)
  except OSError:
      pass

  # a simple page that says hello
  @app.route('/hello')
  def hello():
      return 'Hello, World!'
    
  #init-dbがappに登録された
  from . import db
  db.init_app(app)
  
  #appにbpをimportし登録(auth)
  #新規ユーザ登録とlog in、log outのためのviewを持つ
  from . import auth
  app.register_blueprint(auth.bp)
  
  #appにbpをimportし登録(blog)
  from . import blog
  app.register_blueprint(blog.bp)
  app.add_url_rule('/', endpoint='index')

  return app