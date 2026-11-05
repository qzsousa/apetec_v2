const API_URL = ""; // URL base da API

function salvarToken(token) {
    localStorage.setItem('token', token);
}

function getToken() {
    return localStorage.getItem('token');
}

function verificarLogin() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
    }
    return token;
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = 'login.html';
}

function normalizarCaminho(url) {
    if (!url) return "/";
    return url.startsWith("/") ? url : "/" + url;
}

function normalizarApiUrl(base) {
    if (!base) return "";
    return String(base).replace(/\/+$/, "");
}

async function chamarAPI(url, metodo = "GET", body = null) {
    const token = getToken();

    const headers = {
        "Content-Type": "application/json"
    };

    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }

    const opcoes = {
        method: metodo,
        headers: headers
    };

    if (body !== null && body !== undefined) {
        opcoes.body = JSON.stringify(body);
    }

    const res = await fetch(normalizarApiUrl(API_URL) + normalizarCaminho(url), opcoes);

    if (res.status === 401) {
        logout();
    }

    return res;
}

function escapeHtml(valor) {
    if (valor === null || valor === undefined) return "";
    return String(valor)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

async function parsearErro(res) {
    try {
        const data = await res.json();
        if (data && typeof data === "object") {
            if (data.detail !== undefined && data.detail !== null) {
                return typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
            }
            return JSON.stringify(data);
        }
        return String(data);
    } catch (e) {
        try {
            return await res.text();
        } catch (e2) {
            return "";
        }
    }
}

function senhaValida(senha) {
    return !!senha &&
        senha.length >= 8 &&
        /[A-Z]/.test(senha) &&
        /[0-9]/.test(senha) &&
        /[!@#$%^&*(),.?":{}|<>]/.test(senha);
}


async function uploadArquivo(url, file) {
  const token = getToken();
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(normalizarApiUrl(API_URL) + normalizarCaminho(url), {
    method: "POST",
    headers: token ? { "Authorization": "Bearer " + token } : {},
    body: fd
  });
  if (res.status === 401) logout();
  if (!res.ok) throw new Error(await parsearErro(res));
  return res.json();
}
