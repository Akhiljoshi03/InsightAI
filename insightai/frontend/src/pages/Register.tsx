import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { api } from "../api/client";
import { useAuthStore } from "../store/authStore";

interface FormValues {
  full_name: string;
  email: string;
  password: string;
}

export default function Register() {
  const { register, handleSubmit } = useForm<FormValues>();
  const [serverError, setServerError] = useState<string | null>(null);
  const setTokens = useAuthStore((s) => s.setTokens);
  const navigate = useNavigate();

  async function onSubmit(values: FormValues) {
    setServerError(null);
    try {
      const { data } = await api.post("/api/auth/register", values);
      setTokens(data.access_token, data.refresh_token, data.user);
      navigate("/dashboard");
    } catch (err: any) {
      setServerError(err.response?.data?.detail || "Registration failed");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg text-white px-4">
      <div className="w-full max-w-sm bg-panel border border-border rounded-2xl p-8">
        <h1 className="font-display text-xl font-semibold mb-6">Create your account</h1>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
          <input {...register("full_name")} placeholder="Full name" className="px-3 py-2.5 rounded-lg bg-white/5 border border-border text-sm outline-none" />
          <input {...register("email", { required: true })} placeholder="Email" type="email" className="px-3 py-2.5 rounded-lg bg-white/5 border border-border text-sm outline-none" />
          <input {...register("password", { required: true, minLength: 8 })} placeholder="Password (8+ characters)" type="password" className="px-3 py-2.5 rounded-lg bg-white/5 border border-border text-sm outline-none" />
          {serverError && <span className="text-xs text-red-400">{serverError}</span>}
          <button type="submit" className="mt-2 py-2.5 rounded-lg bg-gradient-to-br from-violet to-violet-dark font-semibold text-sm">
            Create account
          </button>
        </form>
        <div className="text-center text-xs text-white/40 mt-5">
          Already have an account? <Link to="/login" className="text-cyan">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
