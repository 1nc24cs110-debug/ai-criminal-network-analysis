/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        intel: {
          bg: "#080D1A",
          surface: "#0F172A",
          panel: "#141E33",
          border: "#1E293B",
          accent: "#0284C7",
          cyan: "#06B6D4",
          highlight: "#38BDF8",
          warning: "#F59E0B",
          danger: "#EF4444",
          success: "#10B981"
        }
      }
    },
  },
  plugins: [],
}
