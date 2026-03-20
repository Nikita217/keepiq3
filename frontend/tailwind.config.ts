export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        soft: '0 24px 60px rgba(13, 20, 28, 0.14)',
      },
      colors: {
        ink: 'var(--ink)',
        'ink-soft': 'var(--ink-soft)',
        canvas: 'var(--canvas)',
        card: 'var(--panel)',
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
