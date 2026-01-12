import React from 'react';
import { render } from '@testing-library/react-native';
import { Badge } from '../../src/components/ui/Badge';

describe('Badge Component', () => {
  it('renders label correctly', () => {
    const { getByText } = render(<Badge label="Premium" />);
    expect(getByText('Premium')).toBeTruthy();
  });

  it('renders with different variants', () => {
    const variants = ['primary', 'secondary', 'success', 'warning', 'premium'] as const;

    variants.forEach((variant) => {
      const { getByText } = render(<Badge label={variant} variant={variant} />);
      expect(getByText(variant)).toBeTruthy();
    });
  });

  it('renders with different sizes', () => {
    const { rerender, getByText } = render(
      <Badge label="Small" size="small" />
    );
    expect(getByText('Small')).toBeTruthy();

    rerender(<Badge label="Medium" size="medium" />);
    expect(getByText('Medium')).toBeTruthy();
  });

  it('applies testID correctly', () => {
    const { getByTestId } = render(
      <Badge label="Test" testID="my_badge" />
    );
    expect(getByTestId('my_badge')).toBeTruthy();
  });
});
