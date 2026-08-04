import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="min-h-screen bg-bg text-white relative overflow-hidden">
      <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[900px] h-[500px] rounded-full bg-violet/30 blur-[80px]" />
      <nav className="relative flex items-center justify-between px-12 py-6">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-violet to-cyan" />
          <span className="font-display font-bold text-lg">InsightAI</span>
        </div>
        <div className="hidden md:flex gap-8 text-sm text-white/60">
          <span>Product</span><span>Pricing</span><span>Docs</span>
        </div>
        <Link to="/login" className="px-4 py-2 rounded-lg border border-border bg-white/5 text-sm">
          Sign in
        </Link>
      </nav>

      <section className="relative text-center px-6 pt-20 pb-10">
        <h1 className="font-display font-bold text-5xl md:text-6xl leading-tight max-w-3xl mx-auto tracking-tight">
          Transform raw data into{" "}
          <span className="bg-gradient-to-r from-violet to-cyan bg-clip-text text-transparent">
            business intelligence
          </span>{" "}
          with AI
        </h1>
        <p className="text-white/60 max-w-xl mx-auto mt-5 text-lg">
          Upload your dataset. Ask questions in plain English. Get instant insights,
          visualizations, predictions, and reports.
        </p>
        <div className="flex gap-3 justify-center mt-8">
          <Link
            to="/register"
            className="px-6 py-3 rounded-xl bg-gradient-to-br from-violet to-violet-dark font-semibold shadow-lg shadow-violet/30"
          >
            Start free
          </Link>
          <Link to="/login" className="px-6 py-3 rounded-xl border border-border bg-white/5">
            Live demo
          </Link>
        </div>
      </section>
    </div>
  );
}
