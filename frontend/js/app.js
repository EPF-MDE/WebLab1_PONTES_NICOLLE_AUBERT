// Application principale
const App = {
    // Initialisation de l'application
    init: function() {
        UI.init();
        this.loadInitialPage();
    },

    // Charge la page initiale en fonction de l'état d'authentification
    loadInitialPage: function() {
        if (Auth.isAuthenticated()) {
            this.loadPage('books');
        } else {
            this.loadPage('login');
        }
    },

    // Charge une page spécifique
    loadPage: function(page) {
        // Vérifier si la page nécessite une authentification
        const authRequiredPages = ['books', 'profile'];
        if (authRequiredPages.includes(page) && !Auth.isAuthenticated()) {
            UI.showMessage('Vous devez être connecté pour accéder à cette page', 'error');
            page = 'login';
        }

        // Charger le contenu de la page
        switch (page) {
            case 'login':
                this.loadLoginPage();
                break;
            case 'register':
                this.loadRegisterPage();
                break;
            case 'books':
                this.loadBooksPage();
                break;
            case 'profile':
                this.loadProfilePage();
                break;
            default:
                this.loadLoginPage();
        }

        // Mettre à jour la navigation active
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.getAttribute('data-page') === page);
        });
    },

    // Charge la page de connexion
    loadLoginPage: function() {
        const html = `
            <div class="form-container">
                <h2 class="text-center mb-20">Connexion</h2>
                <form id="login-form">
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Mot de passe</label>
                        <input type="password" id="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-block">Se connecter</button>
                </form>
                <p class="text-center mt-20">
                    Vous n'avez pas de compte ? 
                    <a href="#" class="nav-link" data-page="register">Inscrivez-vous</a>
                </p>
            </div>
        `;

        UI.setContent(html);

        // Configurer le formulaire de connexion
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                await Api.login(email, password);
                UI.updateNavigation();
                UI.showMessage('Connexion réussie', 'success');
                this.loadPage('books');
            } catch (error) {
                console.error('Erreur de connexion:', error);
            }
        });

        // Configurer les liens de navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.loadPage(page);
            });
        });
    },

    // Charge la page d'inscription
    loadRegisterPage: function() {
        const html = `
            <div class="form-container">
                <h2 class="text-center mb-20">Inscription</h2>
                <form id="register-form">
                    <div class="form-group">
                        <label for="full_name">Nom complet</label>
                        <input type="text" id="full_name" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Mot de passe</label>
                        <input type="password" id="password" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="confirm_password">Confirmer le mot de passe</label>
                        <input type="password" id="confirm_password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-block">S'inscrire</button>
                </form>
                <p class="text-center mt-20">
                    Vous avez déjà un compte ? 
                    <a href="#" class="nav-link" data-page="login">Connectez-vous</a>
                </p>
            </div>
        `;

        UI.setContent(html);

        // Configurer le formulaire d'inscription
        document.getElementById('register-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const fullName = document.getElementById('full_name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            // Vérifier que les mots de passe correspondent
            if (password !== confirmPassword) {
                UI.showMessage('Les mots de passe ne correspondent pas', 'error');
                return;
            }

            try {
                const userData = {
                    full_name: fullName,
                    email: email,
                    password: password
                };

                await Api.register(userData);
                UI.showMessage('Inscription réussie. Vous pouvez maintenant vous connecter.', 'success');
                this.loadPage('login');
            } catch (error) {
                console.error('Erreur d\'inscription:', error);
            }
        });

        // Configurer les liens de navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.loadPage(page);
            });
        });
    },

    // Charge la page des livres
    loadBooksPage: async function() {
        UI.showLoading();

        try {
            const books = await Api.getBooks();

            let html = `
                <h2 class="mb-20">Catalogue de Livres</h2>
                <div class="card-container">
            `;

            if (!books.items || books.items.length === 0) {
                html += `<p>Aucun livre disponible.</p>`;
            } else {
                books.items.forEach(book => {
                    html += `
                        <div class="card">
                            <div class="card-header">
                                <h3>${book.title}</h3>
                            </div>
                            <div class="card-body">
                                <p><strong>Auteur:</strong> ${book.author}</p>
                                <p><strong>ISBN:</strong> ${book.isbn}</p>
                                <p><strong>Année:</strong> ${book.publication_year}</p>
                                <p><strong>Disponible:</strong> ${book.quantity} exemplaire(s)</p>
                            </div>
                            <div class="card-footer">
                                <button class="btn" onclick="App.viewBookDetails(${book.id})">Voir détails</button>
                            </div>
                        </div>
                    `;
                });
            }

            html += `</div>`;

            UI.setContent(html);
        } catch (error) {
            console.error('Erreur lors du chargement des livres:', error);
            UI.setContent(`<p>Erreur lors du chargement des livres. Veuillez réessayer.</p>`);
        }
    },

    // Affiche les détails d'un livre
    viewBookDetails: async function(bookId) {
        UI.showLoading();

        try {
            const book = await Api.getBook(bookId);

            const html = `
                <div class="book-details">
                    <h2>${book.title}</h2>
                    <div class="book-info">
                        <p><strong>Auteur:</strong> ${book.author}</p>
                        <p><strong>ISBN:</strong> ${book.isbn}</p>
                        <p><strong>Année de publication:</strong> ${book.publication_year}</p>
                        <p><strong>Éditeur:</strong> ${book.publisher || 'Non spécifié'}</p>
                        <p><strong>Langue:</strong> ${book.language || 'Non spécifiée'}</p>
                        <p><strong>Pages:</strong> ${book.pages || 'Non spécifié'}</p>
                        <p><strong>Quantité disponible:</strong> ${book.quantity}</p>
                    </div>
                    <div class="book-description">
                        <h3>Description</h3>
                        <p>${book.description || 'Aucune description disponible.'}</p>
                    </div>
                    <button class="btn mt-20" onclick="App.loadPage('books')">Retour à la liste</button>
                </div>
            `;

            UI.setContent(html);
        } catch (error) {
            console.error('Erreur lors du chargement des détails du livre:', error);
            UI.setContent(`
                <p>Erreur lors du chargement des détails du livre. Veuillez réessayer.</p>
                <button class="btn mt-20" onclick="App.loadPage('books')">Retour à la liste</button>
            `);
        }
    },

    // Charge la page de profil
    loadProfilePage: async function() {
        UI.showLoading();

        try {
            let user = Auth.getUser();

            if (!user) {
                await Api.getCurrentUser();
                user = Auth.getUser();
            }

            const initials = user.full_name
                .split(' ')
                .map(name => name.charAt(0))
                .join('')
                .toUpperCase();

            const html = `
                <div class="profile-container">
                    <div class="profile-header">
                        <div class="profile-avatar">${initials}</div>
                        <h2>${user.full_name}</h2>
                    </div>
                    <div class="profile-info">
                        <div class="profile-info-item">
                            <div class="profile-info-label">Email</div>
                            <div class="profile-info-value">${user.email}</div>
                        </div>
                        <div class="profile-info-item">
                            <div class="profile-info-label">Statut</div>
                            <div class="profile-info-value">${user.is_active ? 'Actif' : 'Inactif'}</div>
                        </div>
                        <div class="profile-info-item">
                            <div class="profile-info-label">Rôle</div>
                            <div class="profile-info-value">${user.is_admin ? 'Administrateur' : 'Utilisateur'}</div>
                        </div>
                        <div class="profile-info-item">
                            <div class="profile-info-label">Téléphone</div>
                            <div class="profile-info-value">${user.phone || 'Non spécifié'}</div>
                        </div>
                        <div class="profile-info-item">
                            <div class="profile-info-label">Adresse</div>
                            <div class="profile-info-value">${user.address || 'Non spécifiée'}</div>
                        </div>
                    </div>
                    <button class="btn" id="edit-profile-btn">Modifier le profil</button>
                </div>
            `;

            UI.setContent(html);
            UI.hideLoading(); // <-- AJOUTE CETTE LIGNE

            // Configurer le bouton de modification du profil
            document.getElementById('edit-profile-btn').addEventListener('click', () => {
                this.loadEditProfilePage(user);
            });
        } catch (error) {
            console.error('Erreur lors du chargement du profil:', error);
            UI.setContent(`<p>Erreur lors du chargement du profil. Veuillez réessayer.</p>`);
            UI.hideLoading(); // <-- Et ici aussi en cas d'erreur
        }
    },

    // Charge la page de modification du profil
    loadEditProfilePage: function(user) {
        const html = `
            <div class="form-container">
                <h2 class="text-center mb-20">Modifier le profil</h2>
                <form id="edit-profile-form">
                    <div class="form-group">
                        <label for="full_name">Nom complet</label>
                        <input type="text" id="full_name" class="form-control" value="${user.full_name}" required>
                    </div>
                    <div class="form-group">
                        <label for="phone">Téléphone</label>
                        <input type="text" id="phone" class="form-control" value="${user.phone || ''}">
                    </div>
                    <div class="form-group">
                        <label for="address">Adresse</label>
                        <textarea id="address" class="form-control">${user.address || ''}</textarea>
                    </div>
                    <button type="submit" class="btn btn-block">Enregistrer les modifications</button>
                </form>
                <button class="btn btn-block mt-20" onclick="App.loadPage('profile')">Annuler</button>
            </div>
        `;

        UI.setContent(html);

        // Configurer le formulaire de modification du profil
        document.getElementById('edit-profile-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const fullName = document.getElementById('full_name').value;
            const phone = document.getElementById('phone').value;
            const address = document.getElementById('address').value;

            try {
                const userData = {
                    full_name: fullName,
                    phone: phone || null,
                    address: address || null
                };

                await Api.call('/users/me', 'PUT', userData);
                await Api.getCurrentUser();
                UI.showMessage('Profil mis à jour avec succès', 'success');
                this.loadPage('profile');
            } catch (error) {
                console.error('Erreur lors de la mise à jour du profil:', error);
            }
        });
    }
};

// Initialiser l'application au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});