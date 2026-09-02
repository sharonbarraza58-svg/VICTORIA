// static/js/auth.js
//
// Une el frontend (este HTML) con el backend (FastAPI) así:
//   1. iniciarSesion()  -> POST /api/v1/auth/login  (definido en api/v1/auth.py)
//   2. obtenerPerfil()  -> GET  /api/v1/auth/me     (definido en api/v1/auth.py)
// Las URLs son RELATIVAS ("/api/v1/...") porque main.py sirve este mismo
// archivo y la API desde el mismo servidor/puerto -> mismo origen -> sin
// CORS, sin URL base que configurar, sin nada más que correr:
//   uvicorn main:app --reload
// y abrir http://127.0.0.1:8000/login

(function () {
  const TOKEN_KEY = "victoria_token";

  function getToken() {
    return sessionStorage.getItem(TOKEN_KEY);
  }

  function setToken(token) {
    sessionStorage.setItem(TOKEN_KEY, token);
  }

  function clearToken() {
    sessionStorage.removeItem(TOKEN_KEY);
  }

  async function iniciarSesion(numeroDocumento, contrasena) {
    // OAuth2PasswordRequestForm en el backend espera
    // application/x-www-form-urlencoded con "username" y "password".
    const body = new URLSearchParams();
    body.set("username", numeroDocumento);
    body.set("password", contrasena);

    const respuesta = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    });

    const datos = await respuesta.json().catch(() => ({}));

    if (!respuesta.ok) {
      const detalle = datos.detail || "No fue posible iniciar sesión.";
      throw new Error(detalle);
    }

    setToken(datos.access_token);
    return datos;
  }

  async function obtenerPerfil() {
    const token = getToken();
    if (!token) return null;

    const respuesta = await fetch("/api/v1/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!respuesta.ok) {
      clearToken();
      return null;
    }

    return respuesta.json();
  }

  function cerrarSesion() {
    clearToken();
    window.location.href = "/login";
  }

  // -----------------------------------------------------------------------
  // SEGURIDAD DE NAVEGACIÓN:
  // Si el navegador vuelve/avanza en el historial, NO reutilizamos la
  // sesión anterior. Esto evita que una vista autenticada reaparezca con
  // los botones Atrás/Adelante después de cerrar o abandonar la sesión.
  // En una recarga normal (F5) la sesión SÍ se conserva.
  // -----------------------------------------------------------------------
  function cerrarSesionPorHistorial() {
    clearToken();
    sessionStorage.removeItem("victoria_user_id");
    sessionStorage.removeItem("victoria_user_name");
    sessionStorage.removeItem("victoria_user_role");
  }

  window.addEventListener("pageshow", function (evento) {
    const navegacion = performance.getEntriesByType("navigation")[0];
    const esHistorial = navegacion && navegacion.type === "back_forward";

    if (evento.persisted || esHistorial) {
      cerrarSesionPorHistorial();

      if (window.location.pathname !== "/login") {
        window.location.replace("/login");
      }
    }
  });

  // ---- Página de login ----
  const formLogin = document.getElementById("login-form");
  if (formLogin) {
    const errorBox = document.getElementById("login-error");
    const botonSubmit = document.getElementById("login-submit");

    formLogin.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      errorBox.style.display = "none";

      const usuario = document.getElementById("username").value.trim();
      const contrasena = document.getElementById("password").value;

      botonSubmit.disabled = true;
      try {
        await iniciarSesion(usuario, contrasena);
        const perfil = await obtenerPerfil();
        if (perfil && (perfil.rol_nombre || '').toLowerCase() === 'instructor') {
          window.location.href = '/instructor';
        } else {
          window.location.href = '/dashboard';
        }
      } catch (err) {
        errorBox.textContent = err.message;
        errorBox.style.display = "block";
      } finally {
        botonSubmit.disabled = false;
      }
    });
  }

  // ---- Página de dashboard ----
  const dashboardRoot = document.getElementById("dashboard-root");
  if (dashboardRoot) {
    obtenerPerfil().then((perfil) => {
      if (!perfil) {
        window.location.href = "/login";
        return;
      }

      const nombreCompleto = [perfil.nombre, perfil.apellido].filter(Boolean).join(" ");
      document.getElementById("dashboard-nombre").textContent = nombreCompleto;
      document.getElementById("dashboard-documento").textContent =
        `${perfil.tipo_documento} ${perfil.numero_documento}`;
      document.getElementById("dashboard-correo-sena").textContent = perfil.correo_sena;
      document.getElementById("dashboard-correo-personal").textContent = perfil.correo_personal;
      document.getElementById("dashboard-estado").textContent = perfil.estado;
      document.getElementById("dashboard-rol").textContent = `Rol: ${perfil.rol_nombre || 'No definido'}`;
    });

    const botonLogout = document.getElementById("logout-btn");
    if (botonLogout) {
      botonLogout.addEventListener("click", cerrarSesion);
    }
  }
})();
