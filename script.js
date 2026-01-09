 // Authentication Functions
async function registerUser(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    // For static demo, simulate registration
    alert('Usuário registrado com sucesso!');
    window.location.href = 'login.html';
}

async function loginUser(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    // For static demo, simulate login
    localStorage.setItem('access_token', 'demo-token');
    alert('Login realizado com sucesso!');
    window.location.href = 'feed.html';
}

async function createPost(event) {
    event.preventDefault();
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('Você precisa estar logado para postar');
        return;
    }

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch('/api/post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        if (response.ok) {
            alert('Post criado com sucesso!');
            loadPosts(); // Reload posts
            event.target.reset();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao criar post');
    }
}

// Load posts from API
async function loadPosts() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
        const response = await fetch('/api/posts', {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const posts = await response.json();
            renderPosts(posts);
        } else {
            console.error('Failed to load posts');
        }
    } catch (error) {
        console.error('Error loading posts:', error);
    }
}

// Render posts
function renderPosts(posts) {
    const container = document.getElementById('posts-container');
    container.innerHTML = ''; // Clear existing

    posts.forEach(post => {
        const postElement = document.createElement('div');
        postElement.className = 'post';
        postElement.innerHTML = `
            <div class="post-header">
                <div class="post-user-info">
                    <div class="user-avatar">
                        <i class="fas fa-user-circle"></i>
                    </div>
                    <div class="user-details">
                        <div class="post-author">
                            <strong>${post.user}</strong>
                        </div>
                        <div class="post-time">${post.created_at}</div>
                    </div>
                </div>
            </div>
            <div class="post-content">
                <p>${post.content.replace(/\n/g, '<br>')}</p>
                ${post.code_snippet ? `<pre><code class="language-javascript">${post.code_snippet}</code></pre>` : ''}
            </div>
            <div class="post-actions">
                <button class="btn-like">
                    <i class="fas fa-heart"></i> ${post.likes}
                </button>
                <button class="btn-comment">
                    <i class="fas fa-comment"></i> ${post.comments.length}
                </button>
                <button class="btn-share">
                    <i class="fas fa-share"></i> Compartilhar
                </button>
                <div class="reactions">
                    <button class="reaction-btn" data-emoji="❤️">❤️</button>
                    <button class="reaction-btn" data-emoji="👍">👍</button>
                    <button class="reaction-btn" data-emoji="😂">😂</button>
                    <button class="reaction-btn" data-emoji="😮">😮</button>
                    <button class="reaction-btn" data-emoji="😢">😢</button>
                </div>
            </div>
            <div class="comments-section">
                ${post.comments.map(comment => `
                    <div class="comment">
                        <div class="comment-avatar">
                            <i class="fas fa-user-circle"></i>
                        </div>
                        <div class="comment-content">
                            <strong>${comment.user}</strong> ${comment.content}
                            <div class="comment-time">${comment.created_at}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(postElement);
    });

    // Re-apply Prism
    Prism.highlightAll();
}
// Theme Toggle
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const languageSelect = document.getElementById('language-select');

    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }

    // Load saved language
    const savedLang = localStorage.getItem('language') || 'pt';
    languageSelect.value = savedLang;

    // Theme toggle event
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const isDark = document.body.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        themeToggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });

    // Language select event
    languageSelect.addEventListener('change', (e) => {
        const lang = e.target.value;
        localStorage.setItem('language', lang);
        // For demo, just alert
        alert(`Idioma alterado para ${lang === 'pt' ? 'Português' : 'English'}`);
    });

    // OAuth simulation
    const githubBtn = document.querySelector('.github-btn');
    const googleBtn = document.querySelector('.google-btn');
    if (githubBtn) {
        githubBtn.addEventListener('click', (e) => {
            e.preventDefault();
            alert('Login com GitHub simulado! Redirecionando...');
            localStorage.setItem('access_token', 'demo-github-token');
            window.location.href = 'feed.html';
        });
    }
    if (googleBtn) {
        googleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            alert('Login com Google simulado! Redirecionando...');
            localStorage.setItem('access_token', 'demo-google-token');
            window.location.href = 'feed.html';
        });
    }

    // Update nav based on login status
    const loginLink = document.querySelector('a[href="login.html"]');
    const registerLink = document.querySelector('a[href="register.html"]');
    if (localStorage.getItem('access_token')) {
        if (loginLink) loginLink.textContent = 'Logout';
        if (loginLink) loginLink.href = '#';
        if (loginLink) loginLink.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('access_token');
            alert('Logout realizado!');
            window.location.href = 'index.html';
        });
        if (registerLink) registerLink.style.display = 'none';
    }

    // Change avatar
    const changeAvatarBtn = document.getElementById('change-avatar');
    if (changeAvatarBtn) {
        const avatars = ['fa-user-circle', 'fa-user', 'fa-user-astronaut', 'fa-user-ninja', 'fa-user-secret'];
        let currentAvatar = 0;
        changeAvatarBtn.addEventListener('click', () => {
            const avatarIcon = document.querySelector('.user-profile .user-avatar i');
            if (avatarIcon) {
                avatarIcon.className = `fas ${avatars[currentAvatar]}`;
                currentAvatar = (currentAvatar + 1) % avatars.length;
            }
        });
    }
});
async function createRepository(event) {
    event.preventDefault();
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('Você precisa estar logado para criar um repositório');
        return;
    }

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch('/repository/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        if (response.ok) {
            alert('Repositório criado com sucesso!');
            window.location.href = '/repositories';
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao criar repositório');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', registerUser);
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', loginUser);
    }

    const postForm = document.getElementById('post-form');
    if (postForm) {
        postForm.addEventListener('submit', createPost);
    }

    const repoForm = document.getElementById('repo-form');
    if (repoForm) {
        repoForm.addEventListener('submit', createRepository);
    }

    // Highlight code blocks
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
});

// Follow/Unfollow functionality
async function followUser(userId, isFollowing) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('Você precisa estar logado para seguir usuários');
        return;
    }

    const action = isFollowing ? 'unfollow' : 'follow';

    try {
        const response = await fetch(`/${action}/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
        });

        const result = await response.json();
        if (response.ok) {
            location.reload(); // Reload to update the UI
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao seguir/deixar de seguir usuário');
    }
}

// Event listener for follow button
document.addEventListener('click', function(event) {
    if (event.target.id === 'follow-btn') {
        const userId = event.target.getAttribute('data-user-id');
        const isFollowing = event.target.classList.contains('unfollow');
        followUser(userId, isFollowing);
    }
});

// Like functionality
async function likePost(postId) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('Você precisa estar logado para curtir posts');
        return;
    }

    try {
        const response = await fetch(`/like/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
        });

        const result = await response.json();
        if (response.ok) {
            // Update like count
            const likeBtn = document.querySelector(`.like-btn[data-post-id="${postId}"]`);
            const likeCount = likeBtn.querySelector('.like-count') || likeBtn;
            const currentCount = parseInt(likeCount.textContent.match(/\d+/)[0]);
            likeCount.textContent = result.liked ? `Curtir (${currentCount + 1})` : `Curtir (${currentCount - 1})`;
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao curtir post');
    }
}

// Comment functionality
async function addComment(postId) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('Você precisa estar logado para comentar');
        return;
    }

    const commentText = document.getElementById(`comment-text-${postId}`).value;
    if (!commentText.trim()) {
        alert('Comentário não pode estar vazio');
        return;
    }

    try {
        const response = await fetch(`/comment/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ content: commentText }),
        });

        const result = await response.json();
        if (response.ok) {
            // Add comment to UI
            const commentsDiv = document.getElementById(`comments-${postId}`);
            const newComment = document.createElement('div');
            newComment.className = 'comment';
            newComment.innerHTML = `<strong><a href="/user/${result.comment.user_id}">${result.comment.username}</a>:</strong> ${result.comment.content}`;
            commentsDiv.appendChild(newComment);

            // Clear textarea
            document.getElementById(`comment-text-${postId}`).value = '';
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao adicionar comentário');
    }
}

// Copy code functionality
function copyCode(button) {
    const codeBlock = button.closest('.code-block').querySelector('pre code');
    const text = codeBlock.textContent || codeBlock.innerText;

    navigator.clipboard.writeText(text).then(function() {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copiado!';
        button.style.background = '#28a745';
        setTimeout(() => {
            button.innerHTML = originalText;
            button.style.background = '#007bff';
        }, 2000);
    }).catch(function(err) {
        console.error('Erro ao copiar: ', err);
        alert('Erro ao copiar código');
    });
}

// Cancel comment functionality
function cancelComment(postId) {
    const commentForm = document.getElementById(`comment-form-${postId}`);
    const textarea = commentForm.querySelector('textarea');
    textarea.value = '';
    commentForm.style.display = 'none';
}

// AI Suggestion functionality
async function getAISuggestion() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('Você precisa estar logado para usar a sugestão IA');
        return;
    }

    const codeSnippet = document.getElementById('code_snippet').value;
    if (!codeSnippet.trim()) {
        alert('Por favor, insira algum código para obter sugestões');
        return;
    }

    const aiBtn = document.getElementById('ai-suggest-btn');
    const originalText = aiBtn.innerHTML;
    aiBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analisando...';
    aiBtn.disabled = true;

    try {
        const response = await fetch('/suggest_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
                code: codeSnippet,
                language: 'python' // You can make this dynamic based on user selection
            }),
        });

        const result = await response.json();
        if (response.ok) {
            // Show suggestion in a modal or alert
            showAISuggestion(result.suggestion);
        } else {
            alert(result.error || 'Erro ao obter sugestão da IA');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao conectar com o serviço de IA');
    } finally {
        aiBtn.innerHTML = originalText;
        aiBtn.disabled = false;
    }
}

// Function to show AI suggestion
function showAISuggestion(suggestion) {
    // Create modal for suggestion
    const modal = document.createElement('div');
    modal.className = 'ai-suggestion-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-robot"></i> Sugestão da IA</h3>
                <button class="close-modal">&times;</button>
            </div>
            <div class="modal-body">
                <pre class="suggestion-text">${suggestion}</pre>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary close-modal">Fechar</button>
                <button class="btn-primary" onclick="applySuggestion()">Aplicar Sugestão</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Close modal functionality
    modal.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    });

    // Store suggestion for applying
    modal.dataset.suggestion = suggestion;
}

// Function to apply AI suggestion
function applySuggestion() {
    const modal = document.querySelector('.ai-suggestion-modal');
    const suggestion = modal.dataset.suggestion;
    document.getElementById('code_snippet').value = suggestion;
    document.body.removeChild(modal);
}

// Event listeners for like and comment buttons
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('like-btn')) {
        const postId = event.target.getAttribute('data-post-id');
        likePost(postId);
    }

    if (event.target.classList.contains('comment-btn')) {
        const postId = event.target.getAttribute('data-post-id');
        const commentForm = document.getElementById(`comment-form-${postId}`);
        if (commentForm) {
            commentForm.style.display = commentForm.style.display === 'none' ? 'block' : 'none';
        }
    }

    if (event.target.classList.contains('share-btn')) {
        const postId = event.target.getAttribute('data-post-id');
        const url = `${window.location.origin}/post/${postId}`;
        navigator.clipboard.writeText(url).then(function() {
            alert('Link copiado para a área de transferência!');
        }).catch(function(err) {
            console.error('Erro ao copiar link: ', err);
            alert('Erro ao copiar link');
        });
    }

    if (event.target.id === 'ai-suggest-btn') {
        getAISuggestion();
    }
});

// Check if user is logged in
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token && (window.location.pathname === '/feed' || window.location.pathname === '/repositories')) {
        window.location.href = '/login';
    }
}

checkAuth();
