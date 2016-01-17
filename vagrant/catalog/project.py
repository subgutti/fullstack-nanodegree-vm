from flask import Flask, render_template, url_for, request, flash
from flask import make_response, redirect, jsonify
from sqlalchemy import create_engine, asc, desc, and_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import random
import string
import httplib2
import json
import requests
import os

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON APIs to view Catalog Information

@app.route('/catalog/JSON')
def catalogJSON():
    """Returns the json response of the entire catalog

    Returns:
        JSON response of entire catalog
    """
    categories = session.query(Category).all()
    response = []
    for category in categories:
        categoryJson = category.serialize
        items = session.query(Item).filter_by(category_id=category.id).all()
        if items:
            categoryJson['item'] = [i.serialize for i in items]
        response.append(categoryJson)

    return jsonify(Category=response)


@app.route('/catalog/<int:category_id>/JSON')
def categoryJSON(category_id):
    """Returns the json response of a particular category in the catalog

    Args:
      category_id: The category id

    Returns:
        JSON response of items in a category_id
    """
    items = session.query(Item).filter_by(category_id=category_id).all()
    if items:
        return jsonify(Item=[i.serialize for i in items])
    else:
        return ('', 204)


@app.route('/catalog/<int:category_id>/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    """Returns the json response of a particular item in a category

    Args:
      category_id: The catalog category id
      item_id: The catalog item id

    Returns:
        JSON response of item description
    """
    item = session.query(Item).filter_by(
        id=item_id).filter_by(category_id=category_id).one()
    if item:
        return jsonify(Item=[item.serialize])
    else:
        return ('', 204)


# User connect and disconnect apis

@app.route('/login')
def showLogin():
    """Display the login page for a user

    Returns:
        HTML page that allows user to login
        either using Google or Facebook.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Validate facebook login response and get required
    user information. Creates a new user if user doesn't
    exist.

    Returns:
        HTML page that confirms the user details and automatically
        redirects to the catalog home page
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s" % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: " \
    "150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Validate google login response and get required
    user information. Creates a new user if user doesn't
    exist.

    Returns:
        HTML page that confirms the user details and automatically
        redirects to the catalog home page
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    client_id = json.loads(open('client_secrets.json', 'r').read())[
        'web']['client_id']
    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: " \
    "150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def createUser(login_session):
    """Create a new user.

    Args:
      login_session: A tuples containing username,
      email and picture

    Returns:
        New user id
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Get user information given a user id.

    Args:
      user_id: User id

    Returns:
        User object that provides information about
        username, user id, email, picture
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Get user id given a user email.

    Args:
      email: user Email

    Returns:
        User id associated to the given email or
        None if no associated email.
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/fbdisconnect')
def fbdisconnect():
    """Disconnect user by clearing out any facebook
    related information.

    Returns:
        A confirmation message that user has been
        logged out.
    """
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gdisconnect')
def gdisconnect():
    """Disconnect user by clearing out any Google
    related information.

    Returns:
        A confirmation message that user has been
        logged out.
    """
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    """Disconnect user by clearing out any Facebook or Google
    related information.

    Returns:
        A confirmation message that user has been
        logged out.
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))

# Catalog related apis


@app.route('/')
@app.route('/catalog')
def showCatalog():
    """Display the entire catalog.

    Returns:
        HTML page that displays the full catalog.
    """
    categories = session.query(Category).order_by(asc(Category.name))
    recentItems = session.query(Item).order_by(desc(Item.id)).limit(5)
    recentlyAddedItems = []
    for item in recentItems:
        category = session.query(Category).filter_by(id=item.category_id).one()
        recentlyAddedItems.append(
            dict([('item_name', item.title),
                  ('category_name', category.name)]))

    return render_template('catalog.html',
                           categories=categories,
                           recentlyAddedItems=recentlyAddedItems)


@app.route('/<string:category_name>')
def showCategoryItems(category_name):
    """Display a particular catalog category items.

    Args:
      category_name: Category name for which items should be
      displayed

    Returns:
        HTML page that displays the category items. If the requested
        category doesn't exists then redirects to home page.
    """
    categories = session.query(Category).order_by(asc(Category.name))
    currentCategory = session.query(
        Category).filter_by(name=category_name).first()
    if currentCategory:
        categoryItems = session.query(Item).filter_by(
            category_id=currentCategory.id).all()
        return render_template('category.html',
                               categories=categories,
                               currentCategory=currentCategory,
                               categoryItems=categoryItems)
    else:
        return redirect(url_for('showCatalog'))


@app.route('/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    """Display a particular item information

    Args:
      category_name: Category name the item belongs to
      item_name: Item name to display information

    Returns:
        HTML page that displays the item information. If the requested
        item doesn't exists then redirects to home page.
    """
    selectedCategory = session.query(
        Category).filter_by(name=category_name).first()
    if selectedCategory:
        selectedCategoryItems = session.query(Item).filter_by(
            category_id=selectedCategory.id).all()
        selectedItem = session.query(Item).filter_by(
            title=item_name).filter_by(category_id=selectedCategory.id).one()
        return render_template('item.html',
                               selectedCategory=selectedCategory,
                               selectedCategoryItems=selectedCategoryItems,
                               selectedItem=selectedItem)
    else:
        return redirect(url_for('showCatalog'))


@app.route('/catalog/item/add', methods=['GET', 'POST'])
def addItem():
    """Display a HTML page that allows user to add a new item.
    Also save the newly created item in database.

    Returns:
        HTML page that allows user to create new item. If user
        is not logged in, then redirects to login page.
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Item(title=request.form['name'],
                       description=request.form['description'],
                       image=request.form['image'],
                       category_id=request.form['category'],
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Item successfully created : %s' % (newItem.title))
        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('newitem.html', categories=categories)


@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    """Display a HTML page that allows user to edit an item.
    Also save the newly edit item in database.

    Args:
      item_name: Item name to edit

    Returns:
        HTML page that allows user to edit an item.
        If user is not logged in, then redirects to login page.
        If user is not authorized to edit, displays a warning message.
    """
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    itemToEdit = session.query(Item).filter_by(title=item_name).first()
    if not itemToEdit:
        return redirect(url_for('showCatalog'))
    if login_session['user_id'] != itemToEdit.user_id:
        return "<script>function myFunction() {alert('You are not " \
            "authorized to edit this item. Please create your own " \
            "item in order to edit.');}" \
            "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.title = request.form['name']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        if request.form['image']:
            itemToEdit.image = request.form['image']
        if request.form['category']:
            itemToEdit.category_id = request.form['category']
        session.add(itemToEdit)
        session.commit()
        flash('Item successfully edited %s' % (itemToEdit.title))
        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('edititem.html',
                               item=itemToEdit,
                               categories=categories)


@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    """Display a HTML page that allows user to delete an item.
    Also delete the item in database.

    Args:
      item_name: Item name to delete

    Returns:
        HTML page that allows user to delete an item.
        If user is not logged in, then redirects to login page.
        If user is not authorized to delete, displays a warning message.
    """
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    itemToDelete = session.query(Item).filter_by(title=item_name).first()
    if not itemToDelete:
        return redirect(url_for('showCatalog'))
    if login_session['user_id'] != itemToDelete.user_id:
        return "<script>function myFunction() {alert('You are not " \
            "authorized to delete this item. Please create your own " \
            " item in order to delete.');}" \
            "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item successfully deleted %s' % (itemToDelete.title))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteitem.html', item=itemToDelete)


@app.context_processor
def override_url_for():
    """Override static folder urls to include timestamp. So that
    the modified static files are reflected immediately to the user.

    Returns:
        Modified URL for static files with timestamp
    """
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    """Override static folder urls to include timestamp. So that
    the modified static files are reflected immediately to the user.

    Returns:
        Modified URL for static files with timestamp
    """
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
