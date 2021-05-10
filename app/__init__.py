# init.py

from flask import Blueprint, Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os 
import secrets # only works with python 3.6 or above
from os.path import join, dirname, realpath



# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['UPLOAD_FOLDER'] = 'static/upload/profile/'
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 2 # LIMIT SIZE FOR UPLOADS FILES - 2 MB
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    db.init_app(app)


    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

     
    # this function below will save/rename a new list in the database.

    @app.route('/save_list', methods=['POST', 'GET'])
    def save_list():        
        
        from .models import Todo
        if request.method == 'POST':
            list_name = request.form['lists']
 
            try:
                save_list = Todo.query.filter_by(list_name='New List').update(dict(list_name=list_name))
                db.session.commit()
                db.session.flush()
                email = current_user.email
                query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') GROUP BY list_name order by date_created desc".format()
                rows = db.session.execute(query)
                output = rows.fetchall()



                share_list=current_user.email
                share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ list_name +"'"
                share_rows = db.session.execute(share_query)
                tasks = share_rows.fetchall()

                # tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=list_name).all()

                #returns to the current list
                return redirect("/list/"+ list_name +"")

            except:
                return 'There was a problem adding this task'

        else:
            return redirect('/')


    # here we will create a function to insert tasks
    
    @app.route('/insert', methods=['POST', 'GET'])
    def insert():        
        
        from .models import Todo
        email = current_user.email
        # this block below is to make a query in database in order to get all lists from the current user
        query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') GROUP BY list_name order by date_created desc".format()
        rows = db.session.execute(query)
        output = rows.fetchall()
 
        #get the name of the current list and do the logic if it is a new list
        get_list = str(request.form['list_name_input'])
        print(len(get_list))
        if len(get_list) == 0:
            list_name = 'New List'

            #getting information from the form to create a task
            if request.method == 'POST':
                task_content = request.form['content'] # this will receive the input data from the form using the input id  
                task_email = current_user.email
                task_done = '0'
                name = current_user.name

                #passing values to the system in order to add a task
                new_task = Todo(content=task_content, email=task_email, mark_task=task_done, list_name=list_name)

            
                try: 
                    db.session.add(new_task)
                    db.session.commit()
                    email = current_user.email
 
                    query2 = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '" + list_name + "' LIMIT 1".format()
                    rows2 = db.session.execute(query2)
                    output2 = rows2.fetchall()
                    output3 = output2[0] # format result from the database
                    for current_list in output3:  # format result from the database
                        print(current_list)      # format result from the database
                    # end block 

               
                    tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=current_list).all()
                    
                    # return render_template('profile.html', tasks=tasks, name=current_user.name, listas=output)
                    return redirect("/list/"+ list_name +"")


                    # return url_for('main.listas', tasks=tasks, name=current_user.name, listas=output)

                except: 
                    return 'There was a problem adding this task.'

            else: 
                return redirect('/')


        else: 

           #do the logic if it's NOT a new list


            list_name = request.form['list_name_input']
          

            if request.method == 'POST':
                task_content = request.form['content'] # this will receive the input data from the form using the id of the input  
                task_email = current_user.email
                task_done = '0'
                name = current_user.name

                # checking if this list was shared
                share_users_query = "SELECT share_list from Todo where share_list is not null and list_name = '"+ list_name +"' order by date_created asc LIMIT 1 ".format()
                share_users_rows = db.session.execute(share_users_query)
                share_users = share_users_rows.fetchall()


                # if it is a shared list then insert members email in the share_list field
                # if not just keep share list as null

                if len(share_users) > 0:
                    for current_share_user in share_users[0]:  # format result from the database
                        print(current_share_user)     # format result from the database
                        # end block 
                        new_task = Todo(content=task_content, email=task_email, share_list=current_share_user,  mark_task=task_done, list_name=list_name)
                else:
                    new_task = Todo(content=task_content, email=task_email, mark_task=task_done, list_name=list_name)
                        

                #add task

                try: 
                    db.session.add(new_task)
                    db.session.commit()
                    email = current_user.email

                    query2 = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '" + list_name + "' LIMIT 1".format()
                    rows2 = db.session.execute(query2)
                    output2 = rows2.fetchall()
                    output3 = output2[0] # format result from the database
                    for current_list in output3:  # format result from the database
                        print(current_list)      # format result from the database
                    # end block 


                    share_list=current_user.email
                    share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ current_list +"'"
                    share_rows = db.session.execute(share_query)
                    tasks = share_rows.fetchall()


                    #tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=current_list).all()
                    
                    
                    
                    return redirect("/list/"+ list_name +"")
                    
                    # return render_template('profile.html', tasks=tasks, name=current_user.name, listas=output)
                    # return redirect(request.referrer)


                    # return url_for('main.listas', tasks=tasks, name=current_user.name, listas=output)

                except: 
                    return 'There was a problem adding this task.'

            else: 
                return redirect('/')

    
    

    # do the logic to remove tasks

    @app.route('/remove/<int:id>')
    def delete(id):
        from .models import Todo    
        task_to_delete = Todo.query.get_or_404(id)
        email = current_user.email
        list_id = str(id)
        print(list_id)
        # this block below is to make a query in database in order to get all lists from the current user
        query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') GROUP BY list_name order by date_created desc".format()
        rows = db.session.execute(query)
        output = rows.fetchall()
        # database query to show what is the current list that user are deleting stuffs. this will be needed to return to the same list after deleting a task
        query2 = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and id = '"+ list_id +"' GROUP BY list_name order by date_created desc".format()
        rows2 = db.session.execute(query2)
        output2 = rows2.fetchall()
        output3 = output2[0] # format result from the database
        for current_list in output3:  # format result from the database
            print(current_list)      # format result from the database
        # end block

        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            name = current_user.name

            
            share_list=current_user.email
            share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ current_list +"'"
            share_rows = db.session.execute(share_query)
            tasks = share_rows.fetchall()

            #tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=current_list).all()


            # check if all tasks were deleted. If yes go to dashboard. If not stay on url list
            if len(tasks) == 0:
                return redirect("/dashboard")
            else:
                #return render_template('profile.html', tasks=tasks, name = current_user.name, listas=output)
                return redirect(request.referrer)

        except:
            return 'There was a problem deleting that task'


    # function to mark/check a TASK


    @app.route('/check/<int:id>')
    def check(id):
        from .models import Todo    
        task_to_delete = Todo.query.get_or_404(id)
        email = current_user.email
        list_id = str(id)
        print(list_id)
        # this block below is to make a query in database in order to get all lists from the current user
        query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') GROUP BY list_name order by date_created desc".format()
        rows = db.session.execute(query)
        output = rows.fetchall()
        # database query to show what is the current list that user are deleting stuffs. this will be needed to return to the same list after deleting a task
        query2 = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and id = '"+ list_id +"' GROUP BY list_name order by date_created desc".format()
        rows2 = db.session.execute(query2)
        output2 = rows2.fetchall()
        output3 = output2[0] # format result from the database
        for current_list in output3:  # format result from the database
            print(current_list)      # format result from the database
        # end block

        # database query showing if a task is done (1) or not done (0)
        check_query = "SELECT mark_task from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and id = '" + list_id + "'".format()
        check_rows = db.session.execute(check_query)
        check_output = check_rows.fetchall()
        check_output2 = check_output[0]
        for current_mark_task in check_output2:  # format result from the database
            print(current_mark_task)      # format result from the database
        # end block
      

        # do the logic if a task is not marked yet
        if current_mark_task == 0:
            check_mark_task = Todo.query.filter_by(id=list_id).update(dict(mark_task='1'))
            db.session.commit()
            db.session.flush()
            name = current_user.name


            share_list=current_user.email
            share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ current_list +"'"
            share_rows = db.session.execute(share_query)
            tasks = share_rows.fetchall()


            #tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=current_list).all()

            #return render_template('profile.html', tasks=tasks, name = current_user.name, listas=output)
            return redirect(request.referrer)
        
        # do the logic if a task is already marked 

        if current_mark_task == 1:
            check_mark_task = Todo.query.filter_by(id=list_id).update(dict(mark_task='0'))
            db.session.commit()
            db.session.flush()
            name = current_user.name
            
            
            share_list=current_user.email
            share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ current_list +"'"
            share_rows = db.session.execute(share_query)
            tasks = share_rows.fetchall()
            
            
            #tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=current_list).all()

            #return render_template('profile.html', tasks=tasks, name = current_user.name, listas=output)
            return redirect(request.referrer)

        else:
            return 'There was a problem checking that task'




    # FUNCTION TO SHARE LISTS between users

    @app.route('/share', methods=['POST', 'GET'])
    def share():        
        
        from .models import Todo
        if request.method == 'POST':
            email = current_user.email
            emails_share = request.form['share_input']
            list_name = request.form['task_list']
        
            #checking if the current list is shared
            query = "SELECT share_list from Todo where list_name = '"+ list_name +"'"
            rows = db.session.execute(query)
            output = rows.fetchall()
            
             #do the logic if the current list is not shared

            if len(output) == 0:
                share_insert = Todo.query.filter_by(list_name=list_name).update(dict(share_list=current_user.email+', '+emails_share))
                db.session.commit()
                db.session.flush()
                email = current_user.email

                share_list=current_user.email
                share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ list_name +"'"
                share_rows = db.session.execute(share_query)
                tasks = share_rows.fetchall()

                # tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=list_name).all()

                #returns to the current list
                return redirect("/list/"+ list_name +"")


                #do the logic if the current list was already shared
            else:
                print(output)
                print(type(output))
                share_insert = Todo.query.filter_by(list_name=list_name).update(dict(share_list=email+', '+emails_share))
                db.session.commit()
                db.session.flush()
                email = current_user.email

    
                # returns all the tasks from the current list  

                share_list=current_user.email
                share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ list_name +"'"
                share_rows = db.session.execute(share_query)
                tasks = share_rows.fetchall()

                # tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=list_name).all()

                #returns to the current list
                return redirect("/list/"+ list_name +"")

           
    # function to update tasks 


    @app.route('/update/<int:id>', methods=['GET', 'POST'])
    def update(id):             
        from .models import Todo
        task = Todo.query.get_or_404(id)
        list_name = request.form['task_list']

        if request.method == 'POST':
            task.content = request.form['taskContent']
            save_list = Todo.query.filter_by(id=id).update(dict(list_name=list_name))

            

            try:
                db.session.commit()
                return redirect(request.referrer)
            except:
                return 'There was an issue updating your task'

        else:
            return redirect(request.referrer)
 


      # FUNCTION TO UPLOAD PROFILE PICTURE


    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST':    
            email = current_user.email
            #Get file1 object as file1

            file1 = request.files['fileF']
            random_hex = secrets.token_hex(20)
            _, f_ext = os.path.splitext(file1.filename)
            picture_fn = random_hex + f_ext
            basedir = os.path.abspath(os.path.dirname(__file__))
            picture_path = os.path.join(basedir, app.config['UPLOAD_FOLDER'], picture_fn)
            file1.save(picture_path)
              
 

            #query1 = "INSERT INTO user (photo) VALUES (%s, %s, %s, %s)" 
 
            upload_photo = User.query.filter_by(email=current_user.email).update(dict(photo=picture_fn))
            db.session.commit()
            db.session.flush()
            return redirect(request.referrer)


    
     # this function below will update the name of the list

    @app.route('/UpdateList', methods=['POST', 'GET'])
    def updatelist():        
        
        from .models import Todo
        if request.method == 'POST':
            list_name_up = request.form['listname_up']
            list_name = request.form['lists']
 
            try:
                lista = Todo.query.filter_by(list_name=list_name_up).update(dict(list_name=list_name))
                db.session.commit()
                db.session.flush()
                email = current_user.email
                query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') GROUP BY list_name order by date_created desc".format()
                rows = db.session.execute(query)
                output = rows.fetchall()



                share_list=current_user.email
                share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ list_name +"'"
                share_rows = db.session.execute(share_query)
                tasks = share_rows.fetchall()

                # tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=list_name).all()

                #returns to the current list
                return redirect("/list/"+ list_name +"")

            except:
                return 'There was a problem adding this task'

        else:
            return redirect('/')

 
    
    if __name__ == "__main__": 
        app.run(debug=True)

    return app


 
 