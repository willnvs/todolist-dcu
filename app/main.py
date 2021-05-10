# main.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import login_required, current_user
import re
import secrets

main = Blueprint('main', __name__)

db = SQLAlchemy()

  
# return user profile/dashboard with all lists created/shared

@main.route('/dashboard')
@login_required
def profile():
    email = current_user.email
    list_name = 'New List'
    
    password = current_user.password
    from .models import Todo
    email = current_user.email
    # return all lists for the current user except shared lists 
    query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is null GROUP BY list_name order by date_created desc".format() 
    rows = db.session.execute(query)
    output = rows.fetchall()
    tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name='New List').all()


    # count tasks to complete
    count_tasks = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 0".format() 
    count_rows = db.session.execute(count_tasks)
    count_output = count_rows.fetchall()
    for counting in count_output:  # format result from the database
        print(counting)  

    # count completed tasks
    count_tasks2 = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 1".format() 
    count_rows2 = db.session.execute(count_tasks2)
    count_output2 = count_rows2.fetchall()
    for counting2 in count_output2:  # format result from the database
        print(counting2)  
 
    #returns only shared lists for the current user. This will be important to show the shared lists on the left menu
    check_shared_list = "SELECT distinct(list_name) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is not null order by date_created desc".format()
    check_shared_list_rows = db.session.execute(check_shared_list)
    check_shared_list_output = check_shared_list_rows.fetchall()

    # check if a new list needs to be saved -- if yes show the list if not redirect to dashboard
    if len(tasks) == 0:
        return render_template('profile.html', name=current_user.name, photo=current_user.photo, tasks=tasks, email=email, password=password, get_list=output, share_list=check_shared_list_output, tasks_to_complete=counting, completed_tasks=counting2)
    else:
        return redirect("/list/"+ list_name +"")
        #return redirect("/dashboard")
        #return redirect(request.referrer)


# return list for each list selected by the user

@main.route('/list/<list_name>')
@login_required
def get_list(list_name):
    password = current_user.password
    from .models import Todo
    email = current_user.email

    # return all lists for the current user except shared lists 

    query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is null GROUP BY list_name order by date_created desc".format()
    rows = db.session.execute(query)
    output = rows.fetchall()

    # database query showing if a task is done (1) or not done (0)
    check_query = "SELECT mark_task from Todo where email = '"+ email +"' and list_name = '"+ list_name +"' ".format()
    check_rows = db.session.execute(check_query)
    check_output = check_rows.fetchall()
    for current_mark_task in check_output:  # format result from the database
        print(current_mark_task)      # format result from the database
        # end block
    
    # query to show all tasks (private and shared lists)
    share_list=current_user.email
    share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ list_name +"' order by date_created asc"
    share_rows = db.session.execute(share_query)
    tasks = share_rows.fetchall()

    # count tasks to complete
    count_tasks = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 0".format() 
    count_rows = db.session.execute(count_tasks)
    count_output = count_rows.fetchall()
    for counting in count_output:  # format result from the database
        print(counting)  

    # count completed tasks
    count_tasks2 = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 1".format() 
    count_rows2 = db.session.execute(count_tasks2)
    count_output2 = count_rows2.fetchall()
    for counting2 in count_output2:  # format result from the database
        print(counting2)  


    #returns only shared lists for the current user. This will be important to show the shared lists on the left menu
    check_shared_list = "SELECT distinct(list_name) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is not null order by date_created desc".format()
    check_shared_list_rows = db.session.execute(check_shared_list)
    check_shared_list_output = check_shared_list_rows.fetchall()
   


    # tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=list_name).all()
    
    return render_template('profile.html', tasks=tasks, name=current_user.name, photo=current_user.photo, list_name=list_name, get_list=output, share_list=check_shared_list_output, tasks_to_complete=counting, completed_tasks=counting2)

 
 # for the moment we are not using the function below

@main.route('/<user>')
def exibir_perfil(user):
    email = current_user.email
    password = current_user.password
    if user == current_user.name:
        user=current_user.name
        return render_template('profile.html', name=current_user.name, photo=current_user.photo, email=email, password=password)
    else:
        return 'Page not found'


 #  Do the logic for all New Lists

@main.route('/list/New List')
@login_required
def new_list():
    password = current_user.password
    from .models import Todo
    email = current_user.email
    list_name = 'New List'


    # return all lists for the current user except shared lists 

    query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is null GROUP BY list_name order by date_created desc".format()
    rows = db.session.execute(query)
    output = rows.fetchall()

    # database query showing if a task is done (1) or not done (0)
    check_query = "SELECT mark_task from Todo where email = '"+ email +"' and list_name = '"+ list_name +"' ".format()
    check_rows = db.session.execute(check_query)
    check_output = check_rows.fetchall()
    for current_mark_task in check_output:  # format result from the database
        print(current_mark_task)      # format result from the database
        # end block
    
    # query to show all tasks (private and shared lists)
    share_list=current_user.email
    share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and list_name = '"+ list_name +"' order by date_created asc"
    share_rows = db.session.execute(share_query)
    tasks = share_rows.fetchall()


    #returns only shared lists for the current user. This will be important to show the shared lists on the left menu
    check_shared_list = "SELECT distinct(list_name) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is not null order by date_created desc".format()
    check_shared_list_rows = db.session.execute(check_shared_list)
    check_shared_list_output = check_shared_list_rows.fetchall()

     # count tasks to complete
    count_tasks = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 0".format() 
    count_rows = db.session.execute(count_tasks)
    count_output = count_rows.fetchall()
    for counting in count_output:  # format result from the database
        print(counting)  

    # count completed tasks
    count_tasks2 = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 1".format() 
    count_rows2 = db.session.execute(count_tasks2)
    count_output2 = count_rows2.fetchall()
    for counting2 in count_output2:  # format result from the database
        print(counting2)  
   


    # tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=list_name).all()
    
    return render_template('profile.html', tasks=tasks, name=current_user.name, photo=current_user.photo, list_name=list_name, get_list=output, share_list=check_shared_list_output, tasks_to_complete=counting, completed_tasks=counting2)


 # Do the logic to show tasks TO COMPLETE

@main.route('/to_complete')
@login_required
def to_complete():
    password = current_user.password
    from .models import Todo
    email = current_user.email
    list_name='Tasks To Complete'
 

    # return all lists for the current user except shared lists 

    query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is null GROUP BY list_name order by date_created desc".format()
    rows = db.session.execute(query)
    output = rows.fetchall()

    # database query showing if a task is done (1) or not done (0)
    check_query = "SELECT mark_task from Todo where email = '"+ email +"' and list_name = '"+ list_name +"' ".format()
    check_rows = db.session.execute(check_query)
    check_output = check_rows.fetchall()
    for current_mark_task in check_output:  # format result from the database
        print(current_mark_task)      # format result from the database
        # end block
    
    # query to show all tasks (private and shared lists)
    share_list=current_user.email
    share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 0 order by date_created asc"
    share_rows = db.session.execute(share_query)
    tasks = share_rows.fetchall()


    #returns only shared lists for the current user. This will be important to show the shared lists on the left menu
    check_shared_list = "SELECT distinct(list_name) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is not null order by date_created desc".format()
    check_shared_list_rows = db.session.execute(check_shared_list)
    check_shared_list_output = check_shared_list_rows.fetchall()
   
    # count tasks to complete
    count_tasks = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 0".format() 
    count_rows = db.session.execute(count_tasks)
    count_output = count_rows.fetchall()
    for counting in count_output:  # format result from the database
        print(counting)  

    # count completed tasks
    count_tasks2 = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 1".format() 
    count_rows2 = db.session.execute(count_tasks2)
    count_output2 = count_rows2.fetchall()
    for counting2 in count_output2:  # format result from the database
        print(counting2)  

    # tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=list_name).all()
    
    return render_template('profile.html', tasks=tasks, name=current_user.name, photo=current_user.photo, list_name=list_name, get_list=output, share_list=check_shared_list_output, tasks_to_complete=counting, completed_tasks=counting2)



 # Do the logic to show COMPLETED TASKS

@main.route('/completed_tasks')
@login_required
def completed_tasks():
    password = current_user.password
    from .models import Todo
    email = current_user.email
    list_name='Completed Tasks'
 

    # return all lists for the current user except shared lists 

    query = "SELECT list_name from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is null GROUP BY list_name order by date_created desc".format()
    rows = db.session.execute(query)
    output = rows.fetchall()

    # database query showing if a task is done (1) or not done (0)
    check_query = "SELECT mark_task from Todo where email = '"+ email +"' and list_name = '"+ list_name +"' ".format()
    check_rows = db.session.execute(check_query)
    check_output = check_rows.fetchall()
    for current_mark_task in check_output:  # format result from the database
        print(current_mark_task)      # format result from the database
        # end block
    
    # query to show all tasks (private and shared lists)
    share_list=current_user.email
    share_query = "SELECT * from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 1 order by date_created asc"
    share_rows = db.session.execute(share_query)
    tasks = share_rows.fetchall()


    #returns only shared lists for the current user. This will be important to show the shared lists on the left menu
    check_shared_list = "SELECT distinct(list_name) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and share_list is not null order by date_created desc".format()
    check_shared_list_rows = db.session.execute(check_shared_list)
    check_shared_list_output = check_shared_list_rows.fetchall()
   
    # count tasks to complete
    count_tasks = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 0".format() 
    count_rows = db.session.execute(count_tasks)
    count_output = count_rows.fetchall()
    for counting in count_output:  # format result from the database
        print(counting)  

    # count completed tasks
    count_tasks2 = "SELECT count(*) from Todo where (email = '"+ email +"' or share_list LIKE '%"+ email +"%') and mark_task = 1".format() 
    count_rows2 = db.session.execute(count_tasks2)
    count_output2 = count_rows2.fetchall()
    for counting2 in count_output2:  # format result from the database
        print(counting2)  

    # tasks = Todo.query.order_by(Todo.date_created).filter_by(email=current_user.email, list_name=list_name).all()
    
    return render_template('profile.html', tasks=tasks, name=current_user.name, photo=current_user.photo, list_name=list_name, get_list=output, share_list=check_shared_list_output, tasks_to_complete=counting, completed_tasks=counting2)


