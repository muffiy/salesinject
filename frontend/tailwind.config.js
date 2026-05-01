/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0B0E',
        surface: '#15151C',
        primary: '#FF2A5F',
        secondary: '#00F0FF',
        accent: '#B026FF',
        success: '#00FFA3',
        warning: '#FFB800',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Space Mono', 'monospace'],
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.0) 100%)',
        'glass-gradient-hover': 'linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.0) 100%)',
      },
      boxShadow: {
        'glass': '0 4px 30px rgba(0, 0, 0, 0.1)',
        'neon-primary': '0 0 10px rgba(255, 42, 95, 0.5), 0 0 20px rgba(255, 42, 95, 0.3)',
        'neon-secondary': '0 0 10px rgba(0, 240, 255, 0.5), 0 0 20px rgba(0, 240, 255, 0.3)',
      }
    },
  },
  plugins: [],
}
