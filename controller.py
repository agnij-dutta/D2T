from flask import Flask, render_template, request, redirect,  url_for
import sqlite3
from os import path

from application.models import *

app = Flask(__name__)
cd=path.abspath(path.dirname('application'))
print(cd)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finaldb.db'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+path.join(cd,"finaldb.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']="21f1002786"
db.init_app(app)
app.app_context().push()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/logout')
def logout():
     return redirect(url_for('home'))

#-----------------------ADMIN FUNCTIONS----------------------------

@app.route('/search_a', methods=['GET','POST'])
def search_admin():
     if request.method=='POST':
          S = Show.query.all()
          V = Venue.query.all()
          sch=request.form.get("anything")
          #print(sch)
          shows=[]
          venues=[]
          loc=[]
          for s in S:
               loc=[]
               if s.name==sch or s.tag==sch or s.price ==sch or s.rating==sch or s.time==sch:
                    loc.append(s)
                    ven = Venue.query.filter_by(vid=s.vid).all()
                    loc.append(ven)
               if loc!=[]:
                    shows.append(loc)

          for v in V:
               if v.vname==sch or v.capacity==sch or v.place==sch:
                    venues.append(v)

          return render_template('adminsearchresults.html',shows=shows,venues=venues)

@app.route('/search_u/<int:usr>',methods=['GET','POST'])
def search_user(usr):
     if request.method=='POST':
          S = Show.query.all()
          V = Venue.query.all()
          sch=request.form.get("anything")
          #print(sch)
          shows=[]
          venues=[]
          loc=[]
          for s in S:
               loc=[]
               if s.name==sch or s.tag==sch or s.price ==sch or s.rating==sch or s.time==sch:
                    loc.append(s)
                    ven = Venue.query.filter_by(vid=s.vid).all()
                    loc.append(ven)
               if loc!=[]:
                    shows.append(loc)

          for v in V:
               if v.vname==sch or v.capacity==sch or v.place==sch:
                    venues.append(v)

          return render_template('usersearchresults.html',shows=shows,venues=venues,usr=usr)



@app.route('/admin',methods=['GET','POST'])
def login_admin():
    if request.method=='GET':
         return render_template('adm.html')
    elif request.method=='POST':
            usr = request.form["username"]       
            pswrd = request.form["password"]
            #validate credentials 
            admn_ob = Admin.query.filter_by(aname = usr).first()
            if admn_ob is None or admn_ob.password!=pswrd:
                 return render_template('login_error.html') #done
            ven_ob = Venue.query.filter_by().all()
            #ev_ob = Show.query.filter_by().all()
            return render_template('events_admin.html',admn_ob=admn_ob,ven_ob=ven_ob) # can send full object to jinja
    
@app.route('/register_admin',methods=['GET','POST'])
def register_admin():
     if request.method=='GET':
          return render_template('register_admin.html')
     elif request.method=='POST':
          uname=request.form.get("username")
          pswrd=request.form.get("password")
          admn_ob = Admin.query.filter_by(aname = uname).first()
          if admn_ob is not None:
               return render_template('taken_error.html')
          a = Admin(aname = uname,password=pswrd)
          db.session.add(a)
          db.session.commit()
          return render_template('adm.html')

@app.route('/create_venue/',methods=['GET','POST'])
def create_venue():
     if request.method=='GET':
          return render_template('create_venue.html')
     elif request.method=='POST':
          vname=request.form.get('vname')
          place=request.form.get('place')
          capacity=request.form.get('capacity')
          
          v_ob=Venue.query.filter_by(vname=vname).first()
          if v_ob is not None:
               return render_template('venue_exists_error.html')
          #add these to admin database
          v = Venue(vname = vname,capacity=capacity,place=place)
          db.session.add(v)
          db.session.commit()
          ven_ob = Venue.query.all()
          for v in ven_ob:
               print(v.vname)
          return redirect(url_for('view_venues'))
          #return render_template('events_admin.html',ven_ob=ven_ob)

@app.route('/edit_venue/<vid>',methods=['GET','POST'])
def edit_venue(vid):
     vn = Venue.query.filter_by(vid=vid).first()

     if request.method=='GET':
          return render_template('edit_venue.html',vn=vn)
     elif request.method=='POST':
          vn = Venue.query.filter_by(vid=vid).first()
          vn.vname=request.form.get("vname")
          vn.capacity=request.form.get("capacity")
          vn.place=request.form.get("place")
          print(vn.vname,vn.place,vn.capacity)

          db.session.commit()
          
          ven_ob = Venue.query.all()
          return redirect(url_for('view_venues'))
     
     
@app.route('/delete_venue/<int:vid>',methods=['GET','POST'])
def delete_venue(vid):
     vnu = Venue.query.filter_by(vid=vid).first()
     if vnu !=None:
          shows = Show.query.filter_by(vid=vnu.vid)
          print("shows are:",shows)
          for sh in shows:
               book = Bookings.query.filter_by(sid=sh.sid).all()
               print(book)
               if book !=[]:
                    for b in book:
                         db.session.delete(b)
                         db.session.commit()
               db.session.delete(sh)
               db.session.commit()
          #new code: 11:40pm - 8/4/23
          db.session.delete(vnu)
          db.session.commit()
     return redirect(url_for('view_venues'))

@app.route('/view_venues',methods=['GET'])
def view_venues():
     ven_ob = Venue.query.all()
     return render_template('events_admin.html',ven_ob=ven_ob)

@app.route('/view_shows/<int:s>',methods=['GET'])
def view_shows(s):
     show_ob = Show.query.filter_by(vid=s).all()
     ven_ob = Venue.query.filter_by(vid=s).first()
     print(ven_ob)
     return render_template('shows.html',show_ob=show_ob,s=s,ven_ob=ven_ob)

@app.route('/create_show/<int:vn>',methods=['GET','POST'])
def create_show(vn):
     if request.method=='GET':
          return render_template('create_show.html',vn=vn)
     elif request.method=='POST':
          name = request.form.get('name')
          price = request.form.get('price')
          tag = request.form.get('tag')
          rating = request.form.get('rating')
          time = request.form.get('time')
          sh_ob = Show.query.filter_by(name=name).all()
          #print(sh_ob)
          vnm = Venue.query.filter_by(vid=vn).first()
          #if sh_ob is None:
               #return render_template('show_exists_error.html',vnm=curr_ven)
          s = Show(name=name,price=price,tag=tag,rating=rating,time=time,vid=vnm.vid)
          db.session.add(s)
          db.session.commit()
          s_ob = Show.query.filter_by(vid=vn).all()
          for sh in s_ob:
               print(s.name)
          #vnm = Venue.query.filter_by(vid=vn).all()
          return redirect(url_for('view_venues'))

@app.route('/edit_show/<int:sid>',methods=['GET','POST'])
def edit_show(sid):
     sh = Show.query.filter_by(sid=sid).first()

     if request.method=='GET':
          return render_template('edit_show.html',sh=sh)
     
     elif request.method=='POST':
          sh = Show.query.filter_by(sid=sid).first()
          sh.name = request.form.get("name")
          sh.price = request.form.get("price")
          sh.tag = request.form.get("tag")
          sh.rating = request.form.get("rating")
          sh.time = request.form.get("time")

          db.session.commit()
          sh_ob = Show.query.filter_by(sid=sid).all()
          ven_ob = Venue.query.filter_by(vid=sh.vid).first()
          #print(sh)
          #print(ven_ob)
          return redirect(url_for('view_venues'))

          #return render_template('shows.html',ven_ob=ven_ob,show_ob=sh_ob)
          

@app.route('/delete_show/<int:sh>',methods=['GET','POST'])
def delete_show(sh):
     s = Show.query.filter_by(sid=sh).first()
     v = Venue.query.filter_by(vid=s.vid).first()
     print(s)
     if s !=None:
          book = Bookings.query.filter_by(sid=sh).all()
          print(book)
          if book !=[]:
               for b in book:
                    v.capacity+=b.tickets
                    db.session.delete(b)
                    db.session.commit()
          db.session.delete(s)
          db.session.commit()

          return redirect(url_for('view_venues'))
     else:
          return render_template('error.html')


#----------------------------------USER FUNCTIONS:----------------------------

@app.route('/register_user',methods=['GET','POST'])
def register_user():
     if request.method=='GET':
          return render_template('register_user.html')
     elif request.method=='POST':
          uname=request.form.get("username")
          pswrd=request.form.get("password")
          #8 to 10 password length | atleast 1 special character

          if (len(pswrd)<8 or len(pswrd)>10) or pswrd.isalnum():
               return render_template('cred.html')
               

          usr_ob = User.query.filter_by(username = uname).first()
          if usr_ob is not None:
               return render_template('taken_error.html')
          u = User(username = uname,password = pswrd)
          db.session.add(u)
          db.session.commit()
          return render_template('usr.html')

@app.route('/user',methods=['GET','POST'])
def login_user():
    if request.method=='GET':
         return render_template('usr.html')
    elif request.method=='POST':
            usr = request.form.get("username")       
            pswrd = request.form.get("password")
            #validate credentials:
            usr_ob=User.query.filter_by(username=usr).first()
            print(usr_ob)
            if usr_ob is None or usr_ob.password!=pswrd:
                 return render_template('login_error.html') #done
            ven_ob = Venue.query.all()
            ev_ob = Show.query.all()
            uid=usr_ob.uid
            print("USER ID: ",uid)
            return render_template('events_user.html',ven_ob=ven_ob,usr_ob=usr_ob,uid=uid)

@app.route('/user_venues/<int:uid>',methods=['GET'])
def user_venues(uid):
     ven_ob = Venue.query.all()
     print(ven_ob)
     usr_ob = User.query.filter_by(uid=uid).first()
     return render_template('events_user.html',ven_ob=ven_ob,usr_ob=usr_ob)

@app.route('/user_shows/<int:vid>/<int:uid>',methods=['GET'])
def user_shows(vid,uid):
     #print(uid) -not entering here
     #rint(vid)
     show_ob = Show.query.filter_by(vid=vid).all()
     ven_ob = Venue.query.filter_by(vid=vid).first()
     usr_ob= User.query.filter_by(uid=uid).first()
     print(ven_ob)
     return render_template('user_shows.html',show_ob=show_ob,ven_ob=ven_ob,usr_ob=usr_ob)

@app.route('/mybookings/<int:uid>',methods=['GET'])
def mybookings(uid):
     if request.method=='GET':
          print(uid)
          temp=[]
          lst=[]
          bob = Bookings.query.filter_by(uid=uid).all()
          for b in bob:
               temp=[]
               sob = Show.query.filter_by(sid=b.sid).all()
               for s in sob:
                    temp.append(s)
               temp.append(b.tickets)
               lst.append(temp)

          print(lst)
          usr = User.query.filter_by(uid=uid).first()
          return render_template('mybookings.html',lst=lst,usr=usr)

@app.route('/book_show/<int:sid>/<int:uid>',methods=['GET','POST'])
def book_show(sid,uid):
     if request.method=='GET':
          show_ob = Show.query.filter_by(sid=sid).first()
          ven_ob = Venue.query.filter_by(vid=show_ob.vid).first()
          return render_template('bookshow.html',show_ob=show_ob,ven_ob=ven_ob,uid=uid)
     elif request.method=='POST':
          tickets=request.form.get('tickets')
          show_ob = Show.query.filter_by(sid=sid).first()
          ven_ob = Venue.query.filter_by(vid=show_ob.vid).first()
          print(ven_ob.capacity,type(ven_ob.capacity))
          if int(tickets)<=int(ven_ob.capacity):
               newcap=int(ven_ob.capacity)-int(tickets)
               ven_ob.capacity=newcap
               print(ven_ob.capacity)

               #new code : 
               b = Bookings(uid=uid,sid=sid,tickets=tickets)
               db.session.add(b)
               db.session.commit()
          else:
               usr_ob = User.query.filter_by(uid=uid).first()
               return render_template("noseats.html",usr_ob=usr_ob)
          return redirect(f'/user_venues/{uid}')

@app.route('/event/<event_id>',methods=['GET','POST'])
def event():
     if request.method=='GET':
          #fetch shows of that event
          return render_template('event.html')

if __name__ == '__main__':
     #db.create_all()
     app.run(debug=True,port=8000)