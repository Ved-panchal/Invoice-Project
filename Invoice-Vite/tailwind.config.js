import { nextui } from '@nextui-org/react'

/** @type {import('tailwindcss').Config} */
export default {
  prefix: 'tw-', // Add a prefix to all Tailwind classes
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@nextui-org/theme/dist/**/*.{js,ts,jsx,tsx}",
    "!./src/Components/Sidebar/Sidebar.jsx", 
  ],
  theme: {
    extend: {},
  },
  plugins: [nextui()],
}

