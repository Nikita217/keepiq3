import { Component, type ErrorInfo, type ReactNode } from 'react';

import { AppShell } from './components/AppShell';
import { EmptyState } from './components/EmptyState';

export class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; message: string }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, message: '' };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Mini App crashed', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <AppShell header={<><p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted">KeepiQ</p><h1 className="mt-2 text-3xl font-extrabold tracking-tight text-ink">Ошибка запуска</h1></>}>
          <EmptyState title="Фронтенд упал при старте" body={this.state.message || 'Unknown frontend error'} />
        </AppShell>
      );
    }

    return this.props.children;
  }
}
