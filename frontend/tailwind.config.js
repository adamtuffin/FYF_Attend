/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        // Find Your Feet CIC Brand Colours
        'fyf-primary': '#F36F21',      // Orange - Primary actions, highlights
        'fyf-secondary': '#D8D9D1',    // Light Grey - Cards, subtle elements
        'fyf-tertiary': '#333333',     // Dark Grey - Text, headings
        'fyf-background': '#242323',   // Dark background - rgb(36,35,35)
      },
      fontFamily: {
        // Brand Typography
        'heading': ['Futura', 'Trebuchet MS', 'sans-serif'],
        'body': ['Avenir', 'Avenir Next', 'Segoe UI', 'sans-serif'],
      },
      // Accessible focus ring
      ringColor: {
        DEFAULT: '#F36F21',
      },
    },
  },
  plugins: [],
}
