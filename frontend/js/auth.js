// Gestion de l'authentification
const Auth = {
    // Stocke le token JWT et les informations utilisateur
    setToken: function(token, expiresIn = CONFIG.TOKEN_EXPIRY) {
        const now = new Date();
        const expiryTime = now.getTime() + expiresIn;

        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, token);
        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN_EXPIRY, expiryTime);
    },

    // Récupère le token JWT
    getToken: function() {
        return localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
    },

    // Vérifie si le token est valide et non expiré
    isAuthenticated: function() {
        const token = this.getToken();
        if (!token) return false;

        const expiryTime = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN_EXPIRY);
        if (!expiryTime) return false;

        const now = new Date();
        return now.getTime() < parseInt(expiryTime);
    },

    // Stocke les informations utilisateur
    setUser: function(userData) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER, JSON.stringify(userData));
    },

    // Récupère les informations utilisateur
    getUser: function() {
        const userData = localStorage.getItem(CONFIG.STORAGE_KEYS.USER);
        return userData ? JSON.parse(userData) : null;
    },

    // Déconnecte l'utilisateur
    logout: function() {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN_EXPIRY);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
    }
};