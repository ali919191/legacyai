import { render, screen } from '@testing-library/react';

import App from './App';

describe('App', () => {
  it('renders the legacy ai chat interface', () => {
    render(<App />);
    expect(screen.getByText(/legacy ai chat interface/i)).toBeTruthy();
    expect(screen.getByRole('heading', { name: /enhanced questions/i })).toBeTruthy();
  });
});