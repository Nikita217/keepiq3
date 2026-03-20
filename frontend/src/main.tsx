import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './App';
import { ErrorBoundary } from './ErrorBoundary';
import './styles/index.css';

declare global {
  interface Window {
    __KEEPIQ_BOOT__?: {
      set: (message: string) => void;
      clear: () => void;
    };
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
);
