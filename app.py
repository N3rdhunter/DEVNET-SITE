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
=======
@app.route('/messages')
@jwt_required()
def 

messages_page():
    return render_template('messages.html')

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
