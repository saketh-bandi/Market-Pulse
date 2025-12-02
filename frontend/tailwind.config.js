/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: '#0a0a0b',
          surface: '#141417',
          border: '#2a2a2e',
          text: {
            primary: '#ffffff',
            secondary: '#a1a1aa',
            muted: '#71717a'
          },
          accent: {
            green: '#22c55e',
            red: '#ef4444',
            blue: '#3b82f6',
            yellow: '#eab308'
          }
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Dank Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}

module.exports = config
