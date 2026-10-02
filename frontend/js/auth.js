const API_URL = "" // URL base da API

function toggleSenha(idCampo, botao) {
  const campo = document.getElementById(idCampo);
  const icone = botao.querySelector("i");
  const escondida = campo.type === "password";

  campo.type = escondida ? "text" : "password";
  icone.classList.toggle("fa-eye", !escondida);
  icone.classList.toggle("fa-eye-slash", escondida);
  botao.setAttribute("aria-label", escondida ? "Ocultar senha" : "Mostrar senha");
}

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

