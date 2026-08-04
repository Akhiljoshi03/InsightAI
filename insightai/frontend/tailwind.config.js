/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#08080D",
        panel: "rgba(255,255,255,0.03)",
        border: "rgba(255,255,255,0.08)",
        violet: { DEFAULT: "#8B5CF6", dark: "#6D28D9" },
        cyan: "#22D3EE",
      },
      fontFamily: {
        display: ["Sora", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
