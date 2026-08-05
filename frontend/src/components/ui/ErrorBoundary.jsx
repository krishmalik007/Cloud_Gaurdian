import React, { Component } from 'react';
import { HiOutlineShieldExclamation, HiOutlineRefresh } from 'react-icons/hi';
import { Button } from './Button';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  handleGoHome = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 text-center select-none text-text-primary">
          <div className="max-w-md w-full bg-surface border border-border-color rounded-2xl p-8 shadow-[0_0_50px_rgba(239,68,68,0.1)] flex flex-col items-center">
            <div className="p-4 bg-red/10 border border-red/20 rounded-full text-red mb-5 animate-pulse">
              <HiOutlineShieldExclamation className="w-12 h-12" />
            </div>

            <h1 className="text-xl font-extrabold mb-2 tracking-tight">
              Application Context Crashed
            </h1>
            
            <p className="text-xs text-text-secondary mb-6 leading-relaxed">
              A critical runtime exception occurred in the frontend view thread. The details have been captured and logged.
            </p>

            {this.state.error && (
              <div className="w-full bg-background/50 border border-border-color rounded-xl p-3 mb-6 font-mono text-[10px] text-red text-left max-h-32 overflow-y-auto">
                {this.state.error.toString()}
              </div>
            )}

            <div className="flex flex-col sm:flex-row items-center gap-3 w-full">
              <Button
                variant="primary"
                size="sm"
                className="w-full justify-center"
                onClick={this.handleReset}
              >
                <HiOutlineRefresh className="w-4 h-4 mr-1.5" />
                Recover Interface
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-center"
                onClick={this.handleGoHome}
              >
                Dashboard Home
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
