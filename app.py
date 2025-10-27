from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import os
from datetime import datetime
from sqlalchemy import or_
from authlib.integrations.flask_client import OAuth
import requests
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codehub.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-here')  # Change in production

db = SQLAlchemy(app)
jwt = JWTManager(app)

# OAuth Setup
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID', 'your-github-client-id'),  # Use environment variables
    client_secret=os.getenv('GITHUB_CLIENT_SECRET', 'your-github-client-secret'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id'),  # Use environment variables
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', 'your-google-client-secret'),
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text)
    skills = db.Column(db.String(500))
    github_username = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    code_snippet = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='posts', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.Text)
    language = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    forks = db.Column(db.Integer, default=0)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'message': 'Missing fields'}), 400

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({'message': 'User already exists'}), 400

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, email=email, password_hash=password_hash.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User created successfully'}), 201
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            access_token = create_access_token(identity=username)
            return jsonify({'access_token': access_token}), 200
        return jsonify({'message': 'Invalid credentials'}), 401
    return render_template('login.html')


@app.route('/dashboard')
@jwt_required()
def dashboard():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Get user stats
    posts_count = Post.query.filter_by(user_id=user.id).count()
    followers_count = Follow.query.filter_by(followed_id=user.id).count()
    likes_count = sum(len(post.likes) for post in user.posts) if user.posts else 0
    repos_count = Repository.query.filter_by(user_id=user.id).count()
    
    # Get recent posts
    recent_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).limit(5).all()
    
    # Get suggested connections (users not followed yet)
    followed_ids = [f.followed_id for f in Follow.query.filter_by(follower_id=user.id).all()]
    followed_ids.append(user.id)  # Exclude self
    suggestions = User.query.filter(~User.id.in_(followed_ids)).limit(5).all()
    
    return render_template('dashboard.html',
                         current_user=user,
                         posts_count=posts_count,
                         followers_count=followers_count,
                         likes_count=likes_count,
                         repos_count=repos_count,
                         recent_posts=recent_posts,
                         suggestions=suggestions)

@app.route('/feed')
@jwt_required()
def feed():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    # Get posts from followed users and own posts
    followed_user_ids = [f.followed_id for f in Follow.query.filter_by(follower_id=user.id).all()]
    followed_user_ids.append(user.id)  # Include own posts

    posts = Post.query.filter(Post.user_id.in_(followed_user_ids)).order_by(Post.created_at.desc()).all()
    return render_template('feed.html', posts=posts, current_user=current_user, user_id=user.id)

@app.route('/post', methods=['POST'])
@jwt_required()
def create_post():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    data = request.get_json()
    content = data['content']
    code_snippet = data.get('code_snippet')

    new_post = Post(content=content, code_snippet=code_snippet, user_id=user.id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully'}), 201

@app.route('/repositories')
@jwt_required()
def repositories():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    repos = Repository.query.filter_by(user_id=user.id).all()
    return render_template('repositories.html', repos=repos)

@app.route('/repository/create', methods=['GET', 'POST'])
@jwt_required()
def create_repository():
    if request.method == 'POST':
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        data = request.get_json()
        name = data['name']
        description = data['description']
        code = data['code']
        language = data['language']

        new_repo = Repository(name=name, description=description, code=code, language=language, user_id=user.id)
        db.session.add(new_repo)
        db.session.commit()

        return jsonify({'message': 'Repository created successfully'}), 201
    return render_template('create_repository.html')

@app.route('/search')
@jwt_required()
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', results=[], query='')

    # Search in users
    users = User.query.filter(
        or_(User.username.contains(query), User.bio.contains(query), User.skills.contains(query))
    ).all()

    # Search in posts
    posts = Post.query.filter(
        or_(Post.content.contains(query), Post.code_snippet.contains(query))
    ).all()

    # Search in repositories
    repos = Repository.query.filter(
        or_(Repository.name.contains(query), Repository.description.contains(query), Repository.code.contains(query))
    ).all()

    results = {
        'users': users,
        'posts': posts,
        'repositories': repos
    }

    return render_template('search.html', results=results, query=query)

# Follow System Routes
@app.route('/follow/<int:user_id>', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if user.id == user_id:
        return jsonify({'message': 'Cannot follow yourself'}), 400

    existing_follow = Follow.query.filter_by(follower_id=user.id, followed_id=user_id).first()
    if existing_follow:
        return jsonify({'message': 'Already following this user'}), 400

    new_follow = Follow(follower_id=user.id, followed_id=user_id)
    db.session.add(new_follow)
    db.session.commit()

    return jsonify({'message': 'User followed successfully'}), 201

@app.route('/unfollow/<int:user_id>', methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    follow = Follow.query.filter_by(follower_id=user.id, followed_id=user_id).first()
    if not follow:
        return jsonify({'message': 'Not following this user'}), 400

    db.session.delete(follow)
    db.session.commit()

    return jsonify({'message': 'User unfollowed successfully'}), 200

@app.route('/user/<int:user_id>')
@jwt_required()
def user_profile(user_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    profile_user = User.query.get_or_404(user_id)

    # Check if current user is following this profile
    is_following = Follow.query.filter_by(follower_id=user.id, followed_id=user_id).first() is not None

    # Get user's posts
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()

    # Get followers and following counts
    followers_count = Follow.query.filter_by(followed_id=user_id).count()
    following_count = Follow.query.filter_by(follower_id=user_id).count()

    return render_template('user_profile.html', profile_user=profile_user, posts=posts,
                         is_following=is_following, followers_count=followers_count,
                         following_count=following_count, current_user=current_user)

# Like System Routes
@app.route('/like/<int:post_id>', methods=['POST'])
@jwt_required()
def like_post(post_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    post = Post.query.get_or_404(post_id)

    existing_like = Like.query.filter_by(user_id=user.id, post_id=post_id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'message': 'Like removed', 'liked': False}), 200
    else:
        new_like = Like(user_id=user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        return jsonify({'message': 'Post liked', 'liked': True}), 201

# Comment System Routes
@app.route('/comment/<int:post_id>', methods=['POST'])
@jwt_required()
def comment_post(post_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    post = Post.query.get_or_404(post_id)

    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({'message': 'Comment content is required'}), 400

    new_comment = Comment(content=content, user_id=user.id, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        'message': 'Comment added successfully',
        'comment': {
            'id': new_comment.id,
            'content': new_comment.content,
            'username': user.username,
            'created_at': new_comment.created_at.strftime('%d/%m/%Y %H:%M')
        }
    }), 201

# OAuth Routes
@app.route('/login/github')
def login_github():
    try:
        redirect_uri = url_for('authorize_github', _external=True)
        return github.authorize_redirect(redirect_uri)
    except Exception as e:
        return jsonify({'error': 'GitHub OAuth not configured', 'message': str(e)}), 500

@app.route('/login/google')
def login_google():
    try:
        redirect_uri = url_for('authorize_google', _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        return jsonify({'error': 'Google OAuth not configured', 'message': str(e)}), 500

@app.route('/authorize/github')
def authorize_github():
    token = github.authorize_access_token()
    resp = github.get('user')
    profile = resp.json()
    email_resp = github.get('user/emails')
    emails = email_resp.json()
    primary_email = next((email['email'] for email in emails if email['primary']), profile['email'])

    # Check if user exists, if not create
    user = User.query.filter_by(email=primary_email).first()
    if not user:
        username = profile['login']
        # Ensure unique username
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1

        user = User(username=username, email=primary_email, password_hash='oauth', github_username=profile['login'])
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=user.username)
    return redirect(url_for('feed', token=access_token))

@app.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    profile = resp.json()

    # Check if user exists, if not create
    user = User.query.filter_by(email=profile['email']).first()
    if not user:
        username = profile['name'].replace(' ', '').lower()
        # Ensure unique username
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1

        user = User(username=username, email=profile['email'], password_hash='oauth')
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=user.username)
    return redirect(url_for('feed', token=access_token))

@app.route('/suggest_code', methods=['POST'])
@jwt_required()
def suggest_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')

        if not code:
            return jsonify({'error': 'No code provided'}), 400

        prompt = f"""
        You are an expert code reviewer and AI assistant for programmers. Analyze the following {language} code and provide:
        1. A brief summary of what the code does
        2. Any potential bugs or issues
        3. Suggestions for improvement (performance, readability, best practices)
        4. An improved version of the code if applicable

        Code to analyze:
        ```{language}
        {code}
        ```

        Please provide your response in a structured format.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful code review assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )

        suggestion = response.choices[0].message.content.strip()

        return jsonify({
            'suggestion': suggestion,
            'language': language
        }), 200

    except Exception as e:
        return jsonify({'error': f'AI suggestion failed: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
