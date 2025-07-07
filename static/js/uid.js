function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }
  
  function setCookie(name, value, days = 365) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
  }
  
  function ensureUID() {
    let uid = getCookie("uid");
    if (!uid) {
      uid = crypto.randomUUID();
      setCookie("uid", uid);
      console.log("Nuevo UID generado:", uid);
    } else {
      console.log("UID existente:", uid);
    }
    return uid;
  }
  