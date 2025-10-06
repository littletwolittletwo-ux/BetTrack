/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0d12",
        card: "#10141b",
        line: "#1c2430",
        text: "#e6eef7",
        mut: "#98a8ba",
        acc: "#5aa9ff",
        danger: "#ff6b6b",
        ok: "#33d69f"
      },
      borderRadius: { xl: "14px", "2xl": "20px" },
      boxShadow: { soft: "0 10px 30px rgba(0,0,0,0.25)" }
    }
  },
  plugins: []
};