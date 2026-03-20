declare global {
  interface TelegramInsets {
    top: number;
    bottom: number;
    left: number;
    right: number;
  }

  interface Window {
    Telegram?: {
      WebApp?: {
        ready: () => void;
        expand: () => void;
        initData: string;
        colorScheme?: 'light' | 'dark';
        themeParams?: Record<string, string>;
        safeAreaInset?: TelegramInsets;
        contentSafeAreaInset?: TelegramInsets;
        onEvent?: (eventType: string, eventHandler: () => void) => void;
      };
    };
  }
}

function applyInsets(prefix: '--tg-safe-area-inset' | '--tg-content-safe-area-inset', insets?: TelegramInsets) {
  if (!insets) return;

  const root = document.documentElement;
  root.style.setProperty(`${prefix}-top`, `${insets.top}px`);
  root.style.setProperty(`${prefix}-bottom`, `${insets.bottom}px`);
  root.style.setProperty(`${prefix}-left`, `${insets.left}px`);
  root.style.setProperty(`${prefix}-right`, `${insets.right}px`);
}

export function setupTelegramTheme() {
  const webApp = window.Telegram?.WebApp;
  webApp?.ready();
  webApp?.expand();

  const syncInsets = () => {
    applyInsets('--tg-safe-area-inset', webApp?.safeAreaInset);
    applyInsets('--tg-content-safe-area-inset', webApp?.contentSafeAreaInset);
  };

  syncInsets();
  webApp?.onEvent?.('safeAreaChanged', syncInsets);
  webApp?.onEvent?.('contentSafeAreaChanged', syncInsets);
}

export function getInitData(): string {
  return window.Telegram?.WebApp?.initData ?? '';
}