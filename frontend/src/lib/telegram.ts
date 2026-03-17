declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        ready: () => void;
        expand: () => void;
        initData: string;
        colorScheme?: 'light' | 'dark';
        themeParams?: Record<string, string>;
      };
    };
  }
}

export function setupTelegramTheme() {
  const webApp = window.Telegram?.WebApp;
  webApp?.ready();
  webApp?.expand();
  const theme = webApp?.themeParams;
  if (!theme) return;
  const root = document.documentElement;
  if (theme.bg_color) root.style.setProperty('--canvas', theme.bg_color);
  if (theme.secondary_bg_color) root.style.setProperty('--card', theme.secondary_bg_color);
  if (theme.text_color) root.style.setProperty('--ink', theme.text_color);
  if (theme.hint_color) root.style.setProperty('--muted', theme.hint_color);
  if (theme.button_color) root.style.setProperty('--accent', theme.button_color);
}

export function getInitData(): string {
  return window.Telegram?.WebApp?.initData ?? '';
}
