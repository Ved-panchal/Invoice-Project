/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    !"./src/Components/Header/*.{jsx}",
    !"./src/Components/Sidebar/*.{jsx}"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}