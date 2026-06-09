const API_URL = "http://localhost:8000" // URL base da API

function salvarToken(token) {
    localStorage.setItem('token', token);
}

function getToken() {
    return localStorage.getItem('token'); // só busca, sem redirecionar
}

function verificarLogin() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html'; // redireciona se não tiver token
    }
    return token;
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = 'login.html';
}

function chamarAPI(url, metodo, body = null) {
    const token = getToken();

    const opcoes = {
        method: metodo,
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
    }

    if (body) {
        opcoes.body = JSON.stringify(body); // só adiciona body se existir
    }

    return fetch(API_URL + url, opcoes); // retorna a promise do fetch
}