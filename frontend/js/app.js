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
        const authRequiredPages = ['books', 'profile', 'loans'];
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
            case 'change-password':
                this.loadChangePasswordPage();
                break;
            case 'loans':
                this.loadLoansPage();
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
            const params = {
                skip: (currentPage - 1) * 10,
                limit: 10,
                sort_by: sortBy,
                sort_desc: sortDesc,
                ...lastSearchParams // pour garder les filtres de recherche
            };
            const books = await Api.getBooks(params);
            const page = books.page;
            const pages = books.pages;

            let html = `
                <h2 class="mb-20">Catalogue de Livres</h2>
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
            `;

            const user = Auth.getUser();
            if (user && user.is_admin) {
                html += `<button class="btn" id="add-book-btn" style="margin-right:16px;">Ajouter un livre</button>`;
            }

            html += `
                <form id="search-form" style="display: flex; align-items: center; gap: 8px; margin-bottom: 0;">
                    <input type="text" id="search-query" placeholder="Titre, auteur, ISBN..." class="form-control" style="width:200px;">
                    <input type="text" id="search-author" placeholder="Auteur" class="form-control" style="width:150px;">
                    <input type="number" id="search-year" placeholder="Année" class="form-control" style="width:100px;">
                    <button type="submit" class="btn">Rechercher</button>
                </form>
            </div>
            <div class="mb-20">
                <label for="sort-by">Trier par :</label>
                <select id="sort-by" class="form-control" style="width:150px;display:inline-block;">
                    <option value="title">Titre</option>
                    <option value="author">Auteur</option>
                    <option value="publication_year">Année</option>
                </select>
                <button id="sort-dir" class="btn" type="button">${sortDesc ? "⬇️" : "⬆️"}</button>
            </div>
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

            html += `</div>
<div class="pagination">
    <button id="prev-page" class="btn" ${page <= 1 ? 'disabled' : ''}>Précédent</button>
    <span>Page ${page} / ${pages}</span>
    <button id="next-page" class="btn" ${page >= pages ? 'disabled' : ''}>Suivant</button>
</div>
`;

            UI.setContent(html);

            // Recherche
            document.getElementById('search-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const query = document.getElementById('search-query').value;
                const author = document.getElementById('search-author').value;
                const publication_year = document.getElementById('search-year').value;

                lastSearchParams = {};
                if (query) lastSearchParams.query = query;
                if (author) lastSearchParams.author = author;
                if (publication_year) lastSearchParams.publication_year = publication_year;
                currentPage = 1;
                // Utilise searchBooks si au moins un champ est rempli, sinon getBooks
                if (query || author || publication_year) {
                    const books = await Api.searchBooks({
                        ...lastSearchParams,
                        skip: 0,
                        limit: 10,
                        sort_by: sortBy,
                        sort_desc: sortDesc
                    });
                    App.renderBooks(books);
                } else {
                    App.loadBooksPage();
                }
            });

            // Pagination
            document.getElementById('prev-page').addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    App.loadBooksPage();
                }
            });
            document.getElementById('next-page').addEventListener('click', () => {
                if (currentPage < pages) {
                    currentPage++;
                    App.loadBooksPage();
                }
            });

            // Tri
            document.getElementById('sort-by').addEventListener('change', (e) => {
                sortBy = e.target.value;
                currentPage = 1;
                App.loadBooksPage();
            });
            document.getElementById('sort-dir').addEventListener('click', () => {
                sortDesc = !sortDesc;
                currentPage = 1;
                App.loadBooksPage();
            });
            document.getElementById('sort-by').value = sortBy;

            // Handler bouton ajouter un livre
            if (user && user.is_admin) {
                document.getElementById('add-book-btn').addEventListener('click', () => {
                    App.loadAddBookPage();
                });
            }

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
            const user = Auth.getUser();

            let html = `
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
            `;

            // Si admin, afficher le formulaire d'édition
            if (user && user.is_admin) {
                html += `
                    <h3>Modifier le livre</h3>
                    <form id="edit-book-form">
                        <div class="form-group">
                            <label for="edit-title">Titre</label>
                            <input type="text" id="edit-title" class="form-control" value="${book.title}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-author">Auteur</label>
                            <input type="text" id="edit-author" class="form-control" value="${book.author}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-isbn">ISBN</label>
                            <input type="text" id="edit-isbn" class="form-control" value="${book.isbn}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-publication-year">Année de publication</label>
                            <input type="number" id="edit-publication-year" class="form-control" value="${book.publication_year}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-publisher">Éditeur</label>
                            <input type="text" id="edit-publisher" class="form-control" value="${book.publisher || ''}">
                        </div>
                        <div class="form-group">
                            <label for="edit-language">Langue</label>
                            <input type="text" id="edit-language" class="form-control" value="${book.language || ''}">
                        </div>
                        <div class="form-group">
                            <label for="edit-pages">Pages</label>
                            <input type="number" id="edit-pages" class="form-control" value="${book.pages || ''}">
                        </div>
                        <div class="form-group">
                            <label for="edit-quantity">Quantité d'exemplaires</label>
                            <input type="number" id="edit-quantity" class="form-control" value="${book.quantity}" min="0" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-description">Description</label>
                            <textarea id="edit-description" class="form-control">${book.description || ''}</textarea>
                        </div>
                        <button type="submit" class="btn">Enregistrer</button>
                    </form>
                `;
            }

            // Formulaire d'emprunt
            if (user && !user.is_admin && book.quantity > 0) {
                html += `
                    <form id="borrow-form">
                        <button type="submit" class="btn">Emprunter ce livre</button>
                    </form>
                `;
            }

            html += `<button class="btn mt-20" onclick="App.loadPage('books')">Retour à la liste</button></div>`;

            UI.setContent(html);

            // Handler pour l'édition (admin uniquement)
            if (user && user.is_admin) {
                document.getElementById('edit-book-form').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    const data = {
                        title: document.getElementById('edit-title').value,
                        author: document.getElementById('edit-author').value,
                        isbn: document.getElementById('edit-isbn').value,
                        publication_year: parseInt(document.getElementById('edit-publication-year').value),
                        publisher: document.getElementById('edit-publisher').value,
                        language: document.getElementById('edit-language').value,
                        pages: parseInt(document.getElementById('edit-pages').value),
                        quantity: parseInt(document.getElementById('edit-quantity').value),
                        description: document.getElementById('edit-description').value
                    };
                    try {
                        await Api.updateBook(book.id, data);
                        UI.showMessage('Livre modifié avec succès', 'success');
                        App.viewBookDetails(book.id); // recharge la page
                    } catch (error) {
                        // message d'erreur déjà géré par Api.call
                    }
                });
            }

            // Handler pour l'emprunt
            if (user && !user.is_admin && book.quantity > 0) {
                document.getElementById('borrow-form').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    try {
                        await Api.borrowBook(book.id);
                        UI.showMessage('Livre emprunté avec succès !', 'success');
                        App.viewBookDetails(book.id); // recharge la page
                    } catch (error) {
                        // message d'erreur déjà géré par Api.call
                    }
                });
            }

            UI.hideLoading();
        } catch (error) {
            UI.setContent(`<p>Erreur lors du chargement des détails du livre.</p>`);
            UI.hideLoading();
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
                    <button class="btn" id="change-password-btn">Changer le mot de passe</button>
                </div>
            `;

            UI.setContent(html);
            UI.hideLoading();

            document.getElementById('edit-profile-btn').addEventListener('click', () => {
                this.loadEditProfilePage(user);
            });
            document.getElementById('change-password-btn').addEventListener('click', () => {
                this.loadPage('change-password');
            });
        } catch (error) {
            console.error('Erreur lors du chargement du profil:', error);
            UI.setContent(`<p>Erreur lors du chargement du profil. Veuillez réessayer.</p>`);
            UI.hideLoading();
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
    },

    // Charge la page de changement de mot de passe
    loadChangePasswordPage: function() {
        const html = `
            <div class="form-container">
                <h2 class="text-center mb-20">Changer le mot de passe</h2>
                <form id="change-password-form">
                    <div class="form-group">
                        <label for="current_password">Mot de passe actuel</label>
                        <input type="password" id="current_password" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="new_password">Nouveau mot de passe</label>
                        <input type="password" id="new_password" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="confirm_new_password">Confirmer le nouveau mot de passe</label>
                        <input type="password" id="confirm_new_password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-block">Changer le mot de passe</button>
                </form>
                <button class="btn btn-block mt-20" onclick="App.loadPage('profile')">Annuler</button>
            </div>
        `;
        UI.setContent(html);

        document.getElementById('change-password-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const currentPassword = document.getElementById('current_password').value;
            const newPassword = document.getElementById('new_password').value;
            const confirmNewPassword = document.getElementById('confirm_new_password').value;

            if (newPassword !== confirmNewPassword) {
                UI.showMessage('Les nouveaux mots de passe ne correspondent pas', 'error');
                return;
            }

            try {
                await Api.changePassword(currentPassword, newPassword);
                UI.showMessage('Mot de passe changé avec succès', 'success');
                App.loadPage('profile');
            } catch (error) {
                // L'erreur est déjà affichée par Api.changePassword
            }
        });
    },

    // Affiche les livres recherchés
    renderBooks: function(books) {
        const page = books.page || 1;
        const pages = books.pages || 1;
        let html = `
            <h2 class="mb-20">Résultats de la recherche</h2>
            <form id="search-form" class="mb-20">
                <input type="text" id="search-query" placeholder="Titre, auteur, ISBN..." class="form-control" style="width:200px;display:inline-block;">
                <input type="text" id="search-author" placeholder="Auteur" class="form-control" style="width:150px;display:inline-block;">
                <input type="number" id="search-year" placeholder="Année" class="form-control" style="width:100px;display:inline-block;">
                <button type="submit" class="btn">Rechercher</button>
            </form>
            <div class="mb-20">
                <label for="sort-by">Trier par :</label>
                <select id="sort-by" class="form-control" style="width:150px;display:inline-block;">
                    <option value="title">Titre</option>
                    <option value="author">Auteur</option>
                    <option value="publication_year">Année</option>
                </select>
                <button id="sort-dir" class="btn" type="button">${sortDesc ? "⬇️" : "⬆️"}</button>
            </div>
            <div class="card-container">
        `;

        if (!books.items || books.items.length === 0) {
            html += `<p>Aucun résultat trouvé.</p>`;
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

        html += `</div>
            <div class="pagination">
                <button id="prev-page" class="btn" ${page <= 1 ? 'disabled' : ''}>Précédent</button>
                <span>Page ${page} / ${pages}</span>
                <button id="next-page" class="btn" ${page >= pages ? 'disabled' : ''}>Suivant</button>
            </div>
        `;

        UI.setContent(html);

        // Réattache les handlers comme dans loadBooksPage
        document.getElementById('search-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = document.getElementById('search-query').value;
            const author = document.getElementById('search-author').value;
            const publication_year = document.getElementById('search-year').value;

            lastSearchParams = {};
            if (query) lastSearchParams.query = query;
            if (author) lastSearchParams.author = author;
            if (publication_year) lastSearchParams.publication_year = publication_year;
            currentPage = 1;
            if (query || author || publication_year) {
                const books = await Api.searchBooks({
                    ...lastSearchParams,
                    skip: 0,
                    limit: 10,
                    sort_by: sortBy,
                    sort_desc: sortDesc
                });
                App.renderBooks(books);
            } else {
                App.loadBooksPage();
            }
        });

        document.getElementById('prev-page').addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                App.loadBooksPage();
            }
        });
        document.getElementById('next-page').addEventListener('click', () => {
            if (currentPage < pages) {
                currentPage++;
                App.loadBooksPage();
            }
        });
        document.getElementById('sort-by').addEventListener('change', (e) => {
            sortBy = e.target.value;
            currentPage = 1;
            App.loadBooksPage();
        });
        document.getElementById('sort-dir').addEventListener('click', () => {
            sortDesc = !sortDesc;
            currentPage = 1;
            App.loadBooksPage();
        });
        document.getElementById('sort-by').value = sortBy;
    },

    // Charge la page des emprunts
    loadLoansPage: async function() {
        UI.showLoading();
        try {
            const user = Auth.getUser();
            let html = `<h2 class="mb-20">Mes emprunts</h2><div class="card-container">`;

            if (user && user.is_admin) {
                html = `
        <h2 class="mb-20">Tous les emprunts</h2>
        <form id="search-loans-form" class="mb-20">
            <input type="text" id="search-book" placeholder="Titre du livre" class="form-control" style="width:160px;display:inline-block;">
            <input type="text" id="search-author" placeholder="Auteur" class="form-control" style="width:120px;display:inline-block;">
            <input type="text" id="search-user" placeholder="Nom utilisateur" class="form-control" style="width:120px;display:inline-block;">
            <input type="text" id="search-email" placeholder="Email utilisateur" class="form-control" style="width:150px;display:inline-block;">
            <button type="submit" class="btn">Rechercher</button>
        </form>
        <div class="mb-20">
            <label for="sort-loans-by">Trier par :</label>
            <select id="sort-loans-by" class="form-control" style="width:150px;display:inline-block;">
                <option value="loan_date">Date d'emprunt</option>
                <option value="due_date">Date de rendu</option>
                <option value="book_title">Titre du livre</option>
                <option value="user_name">Nom utilisateur</option>
            </select>
            <button id="sort-loans-dir" class="btn" type="button">${sortDesc ? "⬇️" : "⬆️"}</button>
        </div>
        <div class="card-container" id="admin-loans-list"></div>
    `;

                // Fonction d'affichage
                function renderAdminLoans(loans) {
                    if (!loans || loans.length === 0) {
                        return `<p>Aucun emprunt trouvé.</p>`;
                    }
                    let html = '';
                    loans.forEach(loan => {
                        html += `
                <div class="card">
                    <div class="card-header">
                        <h3>${loan.book.title}</h3>
                    </div>
                    <div class="card-body">
                        <p><strong>Utilisateur:</strong> ${loan.user.full_name} (${loan.user.email})</p>
                        <p><strong>Auteur:</strong> ${loan.book.author}</p>
                        <p><strong>Date d'emprunt:</strong> ${new Date(loan.loan_date).toLocaleDateString()}</p>
                        <p><strong>À rendre avant:</strong> ${new Date(loan.due_date).toLocaleDateString()}</p>
                        <p><strong>Statut:</strong> ${loan.return_date ? "Rendu" : "En cours"}</p>
                    </div>
                    <div class="card-footer">
                        ${!loan.return_date ? `<button class="btn" onclick="App.returnLoan(${loan.id})">Retourner</button>` : ""}
                    </div>
                </div>
            `;
                    });
                    return html;
                }

                // Fonction pour charger et afficher les emprunts avec filtres/tri
                async function loadAndRenderLoans() {
                    let params = {};
                    const book = document.getElementById('search-book').value;
                    const author = document.getElementById('search-author').value;
                    const userName = document.getElementById('search-user').value;
                    const userEmail = document.getElementById('search-email').value;
                    params.sort_by = sortBy;
                    params.sort_desc = sortDesc;
                    if (book) params.book_title = book;
                    if (author) params.author = author;
                    if (userName) params.user_name = userName;
                    if (userEmail) params.user_email = userEmail;
                    const loans = await Api.getAllLoans(params);
                    document.getElementById('admin-loans-list').innerHTML = renderAdminLoans(loans);
                }

                // Affichage initial
                setTimeout(() => {
                    loadAndRenderLoans();

                    document.getElementById('search-loans-form').addEventListener('submit', async (e) => {
                        e.preventDefault();
                        loadAndRenderLoans();
                    });

                    document.getElementById('sort-loans-by').addEventListener('change', function() {
                        sortBy = this.value;
                        loadAndRenderLoans();
                    });
                    document.getElementById('sort-loans-dir').addEventListener('click', function() {
                        sortDesc = !sortDesc;
                        this.textContent = sortDesc ? "⬇️" : "⬆️";
                        loadAndRenderLoans();
                    });

                    // Met à jour la sélection et la flèche au chargement
                    document.getElementById('sort-loans-by').value = sortBy;
                    document.getElementById('sort-loans-dir').textContent = sortDesc ? "⬇️" : "⬆️";
                }, 0);

            } else if (user) {
                // UTILISATEUR : voir seulement ses emprunts, sans bouton retourner
                const loans = await Api.getUserLoans();
                if (!loans || loans.length === 0) {
                    html += `<p>Vous n'avez aucun emprunt en cours.</p>`;
                } else {
                    loans.forEach(loan => {
                        html += `
                            <div class="card">
                                <div class="card-header">
                                    <h3>${loan.book.title}</h3>
                                </div>
                                <div class="card-body">
                                    <p><strong>Auteur:</strong> ${loan.book.author}</p>
                                    <p><strong>Date d'emprunt:</strong> ${new Date(loan.loan_date).toLocaleDateString()}</p>
                                    <p><strong>À rendre avant:</strong> ${new Date(loan.due_date).toLocaleDateString()}</p>
                                    <p><strong>Statut:</strong> ${loan.return_date ? "Rendu" : "En cours"}</p>
                                </div>
                            </div>
                        `;
                    });
                }
            } else {
                html += `<p>Vous n'avez pas accès à cette page.</p>`;
            }

            html += `</div><button class="btn mt-20" onclick="App.loadPage('books')">Retour aux livres</button>`;
            UI.setContent(html);
        } catch (error) {
            UI.setContent(`<p>Erreur lors du chargement des emprunts.</p>`);
        } finally {
            UI.hideLoading();
        }
    },

    returnLoan: async function(loanId) {
        try {
            await Api.returnLoan(loanId);
            UI.showMessage('Livre retourné avec succès !', 'success');
            App.loadLoansPage();
        } catch (error) {
            // L'erreur est déjà affichée par Api.call
        }
    },

    // Charge la page d'édition du livre
    loadEditBookPage: async function(bookId) {
        UI.showLoading();
        try {
            const book = await Api.getBook(bookId);

            const html = `
                <div class="form-container">
                    <h2 class="text-center mb-20">Modifier le livre</h2>
                    <form id="edit-book-form">
                        <div class="form-group">
                            <label for="edit-title">Titre</label>
                            <input type="text" id="edit-title" class="form-control" value="${book.title}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-author">Auteur</label>
                            <input type="text" id="edit-author" class="form-control" value="${book.author}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-isbn">ISBN</label>
                            <input type="text" id="edit-isbn" class="form-control" value="${book.isbn}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-publication-year">Année de publication</label>
                            <input type="number" id="edit-publication-year" class="form-control" value="${book.publication_year}" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-publisher">Éditeur</label>
                            <input type="text" id="edit-publisher" class="form-control" value="${book.publisher || ''}">
                        </div>
                        <div class="form-group">
                            <label for="edit-language">Langue</label>
                            <input type="text" id="edit-language" class="form-control" value="${book.language || ''}">
                        </div>
                        <div class="form-group">
                            <label for="edit-pages">Pages</label>
                            <input type="number" id="edit-pages" class="form-control" value="${book.pages || ''}">
                        </div>
                        <div class="form-group">
                            <label for="edit-quantity">Quantité d'exemplaires</label>
                            <input type="number" id="edit-quantity" class="form-control" value="${book.quantity}" min="0" required>
                        </div>
                        <div class="form-group">
                            <label for="edit-description">Description</label>
                            <textarea id="edit-description" class="form-control">${book.description || ''}</textarea>
                        </div>
                        <button type="submit" class="btn">Enregistrer</button>
                    </form>
                </div>
            `;

            UI.setContent(html);

            // Configurer le formulaire d'édition du livre
            document.getElementById('edit-book-form').addEventListener('submit', async function(e) {
                e.preventDefault();

                // 1. Récupération des valeurs
                const title = document.getElementById('edit-title').value.trim();
                const author = document.getElementById('edit-author').value.trim();
                const isbn = document.getElementById('edit-isbn').value.trim();
                const publication_year = parseInt(document.getElementById('edit-publication-year').value);
                const publisher = document.getElementById('edit-publisher').value.trim();
                const language = document.getElementById('edit-language').value.trim();
                let pagesValue = document.getElementById('edit-pages').value;
                let pages = pagesValue ? parseInt(pagesValue) : null;
                const quantity = parseInt(document.getElementById('edit-quantity').value);
                const description = document.getElementById('edit-description').value.trim();

                // 2. Validation stricte AVANT de construire l'objet à envoyer
                if (!title || title.length < 1 || title.length > 100) {
                    UI.showMessage("Le titre doit faire entre 1 et 100 caractères.", "error");
                    return;
                }
                if (!author || author.length < 1 || author.length > 100) {
                    UI.showMessage("L'auteur doit faire entre 1 et 100 caractères.", "error");
                    return;
                }
                if (!isbn || isbn.length < 10 || isbn.length > 13) {
                    UI.showMessage("L'ISBN doit faire entre 10 et 13 caractères.", "error");
                    return;
                }
                if (isNaN(publication_year) || publication_year < 1000 || publication_year > new Date().getFullYear()) {
                    UI.showMessage(`L'année de publication doit être comprise entre 1000 et ${new Date().getFullYear()}.`, "error");
                    return;
                }
                if (isNaN(quantity) || quantity < 0) {
                    UI.showMessage("La quantité doit être un nombre entier positif ou nul.", "error");
                    return;
                }
                if (pages !== null && (isNaN(pages) || pages <= 0)) {
                    UI.showMessage("Le nombre de pages doit être strictement positif.", "error");
                    return;
                }
                if (publisher && publisher.length > 100) {
                    UI.showMessage("L'éditeur ne doit pas dépasser 100 caractères.", "error");
                    return;
                }
                if (language && language.length > 50) {
                    UI.showMessage("La langue ne doit pas dépasser 50 caractères.", "error");
                    return;
                }
                if (description && description.length > 1000) {
                    UI.showMessage("La description ne doit pas dépasser 1000 caractères.", "error");
                    return;
                }

                // 3. Construction de l'objet à envoyer SEULEMENT si tout est valide
                const data = {
                    title,
                    author,
                    isbn,
                    publication_year,
                    quantity
                };
    if (publisher && publisher.length <= 100) data.publisher = publisher;
    if (language && language.length <= 50) data.language = language;
    if (pages !== null && !isNaN(pages) && pages > 0) data.pages = pages;
    if (description && description.length <= 1000) data.description = description;

                try {
                    await Api.updateBook(book.id, data);
                    UI.showMessage('Livre modifié avec succès', 'success');
                    App.viewBookDetails(book.id);
                } catch (error) {
                    // message d'erreur déjà géré par Api.call
                }
            });
        } catch (error) {
            console.error('Erreur lors du chargement des détails du livre:', error);
            UI.setContent(`
                <p>Erreur lors du chargement des détails du livre. Veuillez réessayer.</p>
                <button class="btn mt-20" onclick="App.loadPage('books')">Retour à la liste</button>
            `);
        }
    },

    // Charge la page d'ajout de livre
    loadAddBookPage: function() {
        const html = `
        <div class="form-container">
            <h2 class="text-center mb-20">Ajouter un livre</h2>
            <form id="add-book-form">
                <div class="form-group">
                    <label for="title">Titre</label>
                    <input type="text" id="title" class="form-control" required>
                </div>
                <div class="form-group">
                    <label for="author">Auteur</label>
                    <input type="text" id="author" class="form-control" required>
                </div>
                <div class="form-group">
                    <label for="isbn">ISBN</label>
                    <input type="text" id="isbn" class="form-control" required>
                </div>
                <div class="form-group">
                    <label for="publication_year">Année de publication</label>
                    <input type="number" id="publication_year" class="form-control" required>
                </div>
                <div class="form-group">
                    <label for="quantity">Quantité d'exemplaires</label>
                    <input type="number" id="quantity" class="form-control" min="1" value="1" required>
                </div>
                <div class="form-group">
                    <label for="publisher">Éditeur</label>
                    <input type="text" id="publisher" class="form-control">
                </div>
                <div class="form-group">
                    <label for="language">Langue</label>
                    <input type="text" id="language" class="form-control">
                </div>
                <div class="form-group">
                    <label for="pages">Pages</label>
                    <input type="number" id="pages" class="form-control">
                </div>
                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" class="form-control"></textarea>
                </div>
                <button type="submit" class="btn btn-block">Ajouter</button>
            </form>
            <button class="btn btn-block mt-20" onclick="App.loadBooksPage()">Annuler</button>
        </div>
    `;
        UI.setContent(html);

        document.getElementById('add-book-form').addEventListener('submit', async function(e) {
            e.preventDefault();

            // Récupération des valeurs
            const title = document.getElementById('title').value.trim();
            const author = document.getElementById('author').value.trim();
            const isbn = document.getElementById('isbn').value.trim();
            const publication_year = parseInt(document.getElementById('publication_year').value);
            const quantity = parseInt(document.getElementById('quantity').value);
            const publisher = document.getElementById('publisher').value.trim();
            const language = document.getElementById('language').value.trim();
            let pagesValue = document.getElementById('pages').value;
            let pages = pagesValue ? parseInt(pagesValue) : null;
            const description = document.getElementById('description').value.trim();

            // Validation frontend stricte
            if (!title || title.length < 1 || title.length > 100) {
                UI.showMessage("Le titre doit faire entre 1 et 100 caractères.", "error");
                return;
            }
            if (!author || author.length < 1 || author.length > 100) {
                UI.showMessage("L'auteur doit faire entre 1 et 100 caractères.", "error");
                return;
            }
            if (!isbn || isbn.length < 10 || isbn.length > 13) {
                UI.showMessage("L'ISBN doit faire entre 10 et 13 caractères.", "error");
                return;
            }
            if (isNaN(publication_year) || publication_year < 1000 || publication_year > new Date().getFullYear()) {
                UI.showMessage(`L'année de publication doit être comprise entre 1000 et ${new Date().getFullYear()}.`, "error");
                return;
            }
            if (isNaN(quantity) || quantity < 1) {
                UI.showMessage("La quantité doit être un nombre entier positif.", "error");
                return;
            }
            if (pages !== null && (isNaN(pages) || pages <= 0)) {
                UI.showMessage("Le nombre de pages doit être strictement positif.", "error");
                return;
            }
            if (publisher && publisher.length > 100) {
                UI.showMessage("L'éditeur ne doit pas dépasser 100 caractères.", "error");
                return;
            }
            if (language && language.length > 50) {
                UI.showMessage("La langue ne doit pas dépasser 50 caractères.", "error");
                return;
            }
            if (description && description.length > 1000) {
                UI.showMessage("La description ne doit pas dépasser 1000 caractères.", "error");
                return;
            }

            // Construction de l'objet à envoyer
            const data = {
                title,
                author,
                isbn,
                publication_year,
                quantity
            };

            // Champs optionnels : n'ajouter que s'ils sont non vides et valides
            if (publisher && publisher.length <= 100) {
                data.publisher = publisher;
            }
            if (language && language.length <= 50) {
                data.language = language;
            }
            if (pages !== null && !isNaN(pages) && pages > 0) {
                data.pages = pages;
            }
            if (description && description.length <= 1000) {
                data.description = description;
            }

            try {
                await Api.createBook(data);
                UI.showMessage('Livre ajouté avec succès', 'success');
                App.loadBooksPage();
            } catch (error) {
                // message d'erreur déjà géré par Api.call
            }
        });
    },
};

// Variables globales pour la pagination et le tri
let currentPage = 1;
let sortBy = "loan_date";
let sortDesc = true; // Tri décroissant par défaut (plus récents en premier)
let lastSearchParams = {};

// Initialiser l'application au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});