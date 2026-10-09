/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        police: {
          900: '#0b192c',
          800: '#1e3e62',
          700: '#000000',
          500: '#ff6500',
          100: '#e2e8f0',
        }
      }
    },
  },
  plugins: [],
}
