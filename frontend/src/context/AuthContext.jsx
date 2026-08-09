import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getMe, login as loginRequest } from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("revenueshield_token"));
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("revenueshield_user") || "null");
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(Boolean(token));

  useEffect(() => {
    const onExpired = () => {
      setToken(null);
      setUser(null);
      setLoading(false);
    };
    window.addEventListener("auth-expired", onExpired);
    return () => window.removeEventListener("auth-expired", onExpired);
  }, []);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    getMe()
      .then((me) => {
        setUser(me);
        localStorage.setItem("revenueshield_user", JSON.stringify(me));
      })
      .catch(() => {
        localStorage.removeItem("revenueshield_token");
        localStorage.removeItem("revenueshield_user");
        setToken(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  async function login(email, password) {
    const data = await loginRequest(email, password);
    localStorage.setItem("revenueshield_token", data.access_token);
    setToken(data.access_token);

    const me = await getMe();
    localStorage.setItem("revenueshield_user", JSON.stringify(me));
    setUser(me);

    return me;
  }

  function logout() {
    localStorage.removeItem("revenueshield_token");
    localStorage.removeItem("revenueshield_user");
    setToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token && user),
      isAdmin: user?.role === "ADMIN",
      login,
      logout,
    }),
    [token, user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}