// Landing target for Google OAuth: backend redirects here with tokens in the query string.
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuthStore } from "../store/authStore";

export default function OAuthCallback() {
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");
    if (accessToken && refreshToken) {
      api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
      // A "me" endpoint would normally hydrate the user here; for brevity we
      // decode nothing client-side and instead trigger a profile fetch upstream.
      setTokens(accessToken, refreshToken, { id: "", email: "", plan: "free", theme: "dark", is_admin: false });
      navigate("/dashboard");
    } else {
      navigate("/login");
    }
  }, []);

  return <div className="min-h-screen flex items-center justify-center text-white bg-bg text-sm">Signing you in…</div>;
}
