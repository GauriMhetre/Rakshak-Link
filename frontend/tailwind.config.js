/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ashgray: '#BCD4CC',
        darkblue: '#002F45',
        earth: '#E3A750',
        police: {
          900: '#002F45',
          800: '#1a4d5c',
          700: '#000000',
          500: '#E3A750',
          100: '#BCD4CC',
        }
      }
    },
  },
  plugins: [],
}
