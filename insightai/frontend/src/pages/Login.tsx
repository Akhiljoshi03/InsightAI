import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { api } from "../api/client";
import { useAuthStore } from "../store/authStore";

interface FormValues {
  email: string;
  password: string;
}

export default function Login() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>();
  const [serverError, setServerError] = useState<string | null>(null);
  const setTokens = useAuthStore((s) => s.setTokens);
  const navigate = useNavigate();

  async function onSubmit(values: FormValues) {
    setServerError(null);
    try {
      const { data } = await api.post("/api/auth/login", values);
      setTokens(data.access_token, data.refresh_token, data.user);
      navigate("/dashboard");
    } catch (err: any) {
      setServerError(err.response?.data?.detail || "Login failed");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg text-white px-4">
      <div className="w-full max-w-sm bg-panel border border-border rounded-2xl p-8">
        <h1 className="font-display text-xl font-semibold mb-6">Sign in to InsightAI</h1>

        <a
          href={`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/auth/google/login`}
          className="w-full block text-center py-2.5 rounded-lg border border-border mb-4 text-sm"
        >
          Continue with Google
        </a>
        <div className="text-center text-xs text-white/40 mb-4">or</div>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
          <input
            {...register("email", { required: "Email is required" })}
            placeholder="Email"
            type="email"
            className="px-3 py-2.5 rounded-lg bg-white/5 border border-border text-sm outline-none"
          />
          {errors.email && <span className="text-xs text-red-400">{errors.email.message}</span>}

          <input
            {...register("password", { required: "Password is required" })}
            placeholder="Password"
            type="password"
            className="px-3 py-2.5 rounded-lg bg-white/5 border border-border text-sm outline-none"
          />
          {errors.password && <span className="text-xs text-red-400">{errors.password.message}</span>}

          {serverError && <span className="text-xs text-red-400">{serverError}</span>}

          <button
            type="submit"
            className="mt-2 py-2.5 rounded-lg bg-gradient-to-br from-violet to-violet-dark font-semibold text-sm"
          >
            Sign in
          </button>
        </form>

        <div className="text-center text-xs text-white/40 mt-5">
          No account? <Link to="/register" className="text-cyan">Register</Link>
        </div>
        <div className="text-center text-xs text-white/40 mt-2">
          <Link to="/forgot-password" className="text-cyan">Forgot password?</Link>
        </div>
      </div>
    </div>
  );
}
