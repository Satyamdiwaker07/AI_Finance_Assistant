import React, { Component } from "react";

// A rendering error should never leave the user with an unexplained blank page.
export default class ErrorBoundary extends Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <main className="startup-error" role="alert">
          <h1>Finance Assistant could not start</h1>
          <p>Refresh the page. If this continues, make sure you opened the frontend URL shown by Vite.</p>
          <code>{this.state.error.message}</code>
        </main>
      );
    }

    return this.props.children;
  }
}
