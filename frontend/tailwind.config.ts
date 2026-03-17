export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        soft: '0 18px 50px rgba(18, 32, 46, 0.12)',
      },
      colors: {
        ink: 'var(--ink)',
        canvas: 'var(--canvas)',
        card: 'var(--card)',
        accent: 'var(--accent)',
        muted: 'var(--muted)',
        line: 'var(--line)',
      },
      fontFamily: {
        sans: ['"Manrope"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
