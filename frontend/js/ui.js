// Gestion de l'interface utilisateur
const UI = {
    // Éléments DOM
    elements: {
        content: document.getElementById('content'),
        pageContent: document.getElementById('page-content'),
        loading: document.getElementById('loading'),
        messageContainer: document.getElementById('message-container'),
        message: document.getElementById('message'),
        navLinks: document.querySelectorAll('.nav-link'),
        authRequired: document.querySelectorAll('.auth-required'),
        logoutLink: document.getElementById('logout-link')
    },

    // Initialisation de l'interface
    init: function() {
        this.updateNavigation();
        this.setupEventListeners();
    },

    // Configuration des écouteurs d'événements
    setupEventListeners: function() {
        // Navigation
        this.elements.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                App.loadPage(page);
            });
        });

        // Déconnexion
        this.elements.logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            Auth.logout();
            this.updateNavigation();
            App.loadPage('login');
            this.showMessage('Vous avez été déconnecté avec succès', 'success');
        });
    },

    // Mise à jour de la navigation en fonction de l'état d'authentification
    updateNavigation: function() {
        const isAuthenticated = Auth.isAuthenticated();

        this.elements.authRequired.forEach(item => {
            item.classList.toggle('hidden', !isAuthenticated);
        });

        // Afficher/masquer les liens de connexion/inscription
        document.querySelectorAll('[data-page="login"], [data-page="register"]').forEach(link => {
            const listItem = link.parentElement;
            listItem.classList.toggle('hidden', isAuthenticated);
        });
    },

    // Affiche un message à l'utilisateur
    showMessage: function(text, type = 'success') {
        this.elements.message.textContent = text;
        this.elements.message.className = type;
        this.elements.messageContainer.classList.remove('hidden');

        // Masquer le message après 5 secondes
        setTimeout(() => {
            this.hideMessage();
        }, 5000);
    },

    // Masque le message
    hideMessage: function() {
        this.elements.messageContainer.classList.add('hidden');
    },

    // Affiche l'indicateur de chargement
    showLoading: function() {
        this.elements.loading.classList.remove('hidden');
    },

    // Masque l'indicateur de chargement
    hideLoading: function() {
        this.elements.loading.classList.add('hidden');
    },

    // Charge le contenu HTML dans la page
    setContent: function(html) {
        this.elements.pageContent.innerHTML = html;
    }
};