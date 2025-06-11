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
                    App.renderBooks(books); // Crée une méthode pour afficher les livres (voir plus bas)
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
                    ${book.quantity > 0 ? `<button class="btn" id="borrow-btn">Emprunter ce livre</button>` : `<span class="text-danger">Indisponible</span>`}
                    <button class="btn mt-20" onclick="App.loadPage('books')">Retour à la liste</button>
                </div>
            `;

            UI.setContent(html);

            // Dans App.viewBookDetails, après UI.setContent(html);
            if (book.quantity > 0) {
                const borrowBtn = document.getElementById('borrow-btn');
                if (borrowBtn) {
                    borrowBtn.addEventListener('click', async () => {
                        try {
                            await Api.borrowBook(book.id);
                            UI.showMessage('Livre emprunté avec succès !', 'success');
                            App.loadPage('loans');
                        } catch (error) {
                            // L'erreur est déjà affichée par Api.call
                        }
                    });
                }
            }
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