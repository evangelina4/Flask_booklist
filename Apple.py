from flask import Flask,render_template,flash,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import  DataRequired
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:9436369@127.0.0.1/flask_books'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'nine'

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(16),unique=True)
    books = db.relationship('Book',backref = 'author')
    def __repr__(self):
        return '<Author: %s>' % self.name

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(16),unique=True)
    author_id = db.Column(db.Integer,db.ForeignKey('authors.id'))
    def __repr__(self):
        return '<Book: %s>' % self.name

#自定义表单类
class AuthorForm(FlaskForm):
    author = StringField('作者:',validators=[DataRequired()])
    book = StringField('书籍:',validators=[DataRequired()])
    submit = SubmitField('提交')

#删除作者
@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    #查询数据库，是否有该id的作者，有则删除（先删书再删作者），无则报错
    #1.查询数据库
    author = Author.query.get(author_id)

    #2.有则删除
    if author:
        try:
            #查询到直接删除
            Book.query.filter_by(author_id=author.id).delete()
            #删除作者
            db.session.delete(author)
            db.session.commit()

        except Exception as e:
            print(e)
            flash('删除作者出错')
            db.session.rollback()
    #3.无则报错
    else:
        flash('作者找不到')

    return redirect(url_for('index'))




#删除书籍----网页中删除----点击需要发送书籍的id给删除书籍的路由----路由需要接收参数
@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    #查询数据库，是否有该id的书，有就删除，没有就提示错误
    book = Book.query.get(book_id)
    #如果有就删除
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍出错')
            db.session.rollback()
    else:
        #没有书籍，就提示错误
        flash('找不到书籍')

    #如何返回当前网址----重定向
    return redirect(url_for('index'))


@app.route('/',methods=['GET','POST'])
def index():
    #创建自定义表单类
    author_form = AuthorForm()
    '''
    验证逻辑
    1.调用WTF的函数实现验证
    2.验证通过获取数据
    3.判断作者是否存在
    4.如果作者存在，判断书籍是否存在，没有重复书籍就添加数据，如果重复就提示错误
    5.如果作者不存在，添加作者和书籍
    6.验证若不通过，则提示错误
    '''
    #1.调用WTF的函数实现验证
    if author_form.validate_on_submit():
        #2.验证通过获取数据
        author_name = author_form.author.data
        book_name = author_form.book.data

        #3.判断作者是否存在
        author = Author.query.filter_by(name=author_name).first()

        #4.如果作者存在
        if author:
            #判断书籍是否存在
            book = Book.query.filter_by(name=book_name).first()
            #如果重复就提示错误
            if book:
                flash('已存在同名书籍')
            #没有重复书籍就添加数据
            else:
                try:
                    new_book = Book(name=book_name,author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('添加书籍失败')
                    db.session.rollback()

        else:
            #5.如果作者不存在，添加作者和书籍
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name,author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash('添加作者和书籍失败')
                db.session.rollback()


    else:
        #6.验证若不通过，则提示错误
        if request.method == 'POST':
            flash('参数不全')


    #查询作者信息，传递给模板
    authors = Author.query.all()
    return render_template('books.html',authors=authors,form=author_form)


if __name__ == '__main__':
    db.drop_all()
    db.create_all()

    au1 = Author(name='吴承恩')
    au2 = Author(name='曹雪芹')
    au3 = Author(name='刘慈欣')
    db.session.add_all([au1,au2,au3])
    db.session.commit()

    bk1 = Book(name='西游记',author_id=au1.id)
    bk2 = Book(name='红楼梦', author_id=au2.id)
    bk3 = Book(name='地球往事', author_id=au3.id)
    bk4 = Book(name='二零一八', author_id=au3.id)
    bk5 = Book(name='朝闻道', author_id=au3.id)
    db.session.add_all([bk1,bk2,bk3,bk4,bk5])
    db.session.commit()

    app.run(debug = True)
