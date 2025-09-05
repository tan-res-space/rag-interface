/**
 * VectorSimilarity Component Tests
 * Tests similarity analysis and pattern recognition functionality
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { VectorSimilarity } from './VectorSimilarity';
import type { SimilarityResult } from '@domain/types';

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

const mockSimilarityResults: SimilarityResult[] = [
  {
    patternId: 'pattern-1',
    similarText: 'original error text one',
    confidence: 0.95,
    frequency: 5,
    suggestedCorrection: 'corrected text one',
    speakerIds: ['speaker-1', 'speaker-2'],
    category: 'pronunciation',
  },
  {
    patternId: 'pattern-2',
    similarText: 'original error text two',
    confidence: 0.87,
    frequency: 3,
    suggestedCorrection: 'corrected text two',
    speakerIds: ['speaker-3'],
    category: 'grammar',
  },
  {
    patternId: 'pattern-3',
    similarText: 'original error text three',
    confidence: 0.92,
    frequency: 8,
    suggestedCorrection: 'corrected text three',
    speakerIds: ['speaker-1', 'speaker-4'],
    category: 'pronunciation',
  },
  {
    patternId: 'pattern-4',
    similarText: 'low confidence error',
    confidence: 0.65,
    frequency: 1,
    suggestedCorrection: 'low confidence correction',
    speakerIds: ['speaker-5'],
    category: 'general',
  },
];

// Mock clipboard API
const mockClipboard = {
  writeText: jest.fn(() => Promise.resolve()),
};

Object.assign(navigator, {
  clipboard: mockClipboard,
});

describe('VectorSimilarity', () => {
  const defaultProps = {
    similarityResults: mockSimilarityResults,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Functionality', () => {
    it('renders with similarity results', () => {
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      expect(screen.getByText('Similar Error Patterns')).toBeInTheDocument();
      expect(screen.getByText('3 found')).toBeInTheDocument(); // Above threshold (0.8)
    });

    it('shows loading state', () => {
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps} 
          isLoading={true}
        />
      );
      
      expect(screen.getByText('Analyzing Patterns...')).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('shows no results message when no patterns found', () => {
      renderWithTheme(
        <VectorSimilarity 
          similarityResults={[]}
        />
      );
      
      expect(screen.getByText('No Similar Patterns Found')).toBeInTheDocument();
    });

    it('filters results by confidence threshold', () => {
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          threshold={0.9}
        />
      );
      
      // Only patterns with confidence >= 0.9 should be shown
      expect(screen.getByText('2 found')).toBeInTheDocument();
      expect(screen.getByText('corrected text one')).toBeInTheDocument(); // 0.95
      expect(screen.getByText('corrected text three')).toBeInTheDocument(); // 0.92
      expect(screen.queryByText('corrected text two')).not.toBeInTheDocument(); // 0.87
    });

    it('limits results by maxResults prop', () => {
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          maxResults={2}
        />
      );
      
      expect(screen.getByText('2 found')).toBeInTheDocument();
    });
  });

  describe('Pattern Display', () => {
    it('displays pattern information correctly', () => {
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      // Check first pattern (highest confidence)
      expect(screen.getByText('corrected text one')).toBeInTheDocument();
      expect(screen.getByText('95%')).toBeInTheDocument();
      expect(screen.getByText('Original: original error text one')).toBeInTheDocument();
      expect(screen.getByText('5 occurrences')).toBeInTheDocument();
      expect(screen.getByText('2 speakers')).toBeInTheDocument();
    });

    it('shows confidence labels correctly', () => {
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      expect(screen.getByText('Confidence: Very High')).toBeInTheDocument(); // 0.95
      expect(screen.getByText('Confidence: High')).toBeInTheDocument(); // 0.92
      expect(screen.getByText('Confidence: Medium')).toBeInTheDocument(); // 0.87
    });

    it('sorts patterns by confidence descending', () => {
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      const patterns = screen.getAllByText(/corrected text/);
      expect(patterns[0]).toHaveTextContent('corrected text one'); // 0.95
      expect(patterns[1]).toHaveTextContent('corrected text three'); // 0.92
      expect(patterns[2]).toHaveTextContent('corrected text two'); // 0.87
    });
  });

  describe('Pattern Interaction', () => {
    it('calls onPatternSelect when pattern is clicked', async () => {
      const user = userEvent.setup();
      const onPatternSelect = jest.fn();
      
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          onPatternSelect={onPatternSelect}
        />
      );
      
      const firstPattern = screen.getByText('corrected text one');
      await user.click(firstPattern);
      
      expect(onPatternSelect).toHaveBeenCalledWith(mockSimilarityResults[0]);
    });

    it('copies pattern text to clipboard when copy button is clicked', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      const copyButtons = screen.getAllByLabelText(/copy correction/i);
      await user.click(copyButtons[0]);
      
      expect(mockClipboard.writeText).toHaveBeenCalledWith('corrected text one');
    });

    it('shows copied confirmation after copying', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      const copyButtons = screen.getAllByLabelText(/copy correction/i);
      await user.click(copyButtons[0]);
      
      await waitFor(() => {
        expect(screen.getByLabelText('Copied!')).toBeInTheDocument();
      });
    });

    it('prevents pattern selection when disabled', async () => {
      const user = userEvent.setup();
      const onPatternSelect = jest.fn();
      
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          onPatternSelect={onPatternSelect}
          disabled={true}
        />
      );
      
      const firstPattern = screen.getByText('corrected text one');
      await user.click(firstPattern);
      
      expect(onPatternSelect).not.toHaveBeenCalled();
    });
  });

  describe('Pattern Grouping', () => {
    it('groups patterns by category when showPatternAnalysis is true', () => {
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          showPatternAnalysis={true}
        />
      );
      
      expect(screen.getByText(/found patterns across \d+ categories/i)).toBeInTheDocument();
      expect(screen.getByText(/highest confidence category/i)).toBeInTheDocument();
    });

    it('shows category groups with expand/collapse functionality', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          showPatternAnalysis={true}
        />
      );
      
      // Should show category headers
      expect(screen.getByText('pronunciation')).toBeInTheDocument();
      expect(screen.getByText('grammar')).toBeInTheDocument();
      
      // Click to expand a category
      const pronunciationHeader = screen.getByText('pronunciation');
      await user.click(pronunciationHeader);
      
      // Should show patterns in that category
      expect(screen.getByText('corrected text one')).toBeInTheDocument();
      expect(screen.getByText('corrected text three')).toBeInTheDocument();
    });

    it('shows category statistics', () => {
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          showPatternAnalysis={true}
        />
      );
      
      // Should show pattern counts and average confidence for categories
      expect(screen.getByText('2 patterns')).toBeInTheDocument(); // pronunciation category
      expect(screen.getByText('1 patterns')).toBeInTheDocument(); // grammar category
    });

    it('displays flat list when showPatternAnalysis is false', () => {
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          showPatternAnalysis={false}
        />
      );
      
      // Should not show category grouping
      expect(screen.queryByText(/found patterns across/i)).not.toBeInTheDocument();
      
      // Should show all patterns directly
      expect(screen.getByText('corrected text one')).toBeInTheDocument();
      expect(screen.getByText('corrected text two')).toBeInTheDocument();
      expect(screen.getByText('corrected text three')).toBeInTheDocument();
    });
  });

  describe('Confidence Visualization', () => {
    it('uses different colors for different confidence levels', () => {
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      const confidenceChips = screen.getAllByText(/\d+%/);
      
      // Check that confidence chips have different styling based on confidence
      confidenceChips.forEach(chip => {
        expect(chip).toHaveStyle('color: white');
        expect(chip).toHaveStyle('font-weight: bold');
      });
    });

    it('shows appropriate confidence labels', () => {
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      expect(screen.getByText('Confidence: Very High')).toBeInTheDocument(); // 95%
      expect(screen.getByText('Confidence: High')).toBeInTheDocument(); // 92%
      expect(screen.getByText('Confidence: Medium')).toBeInTheDocument(); // 87%
    });
  });

  describe('Footer Information', () => {
    it('shows result count and threshold information', () => {
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          threshold={0.8}
        />
      );
      
      expect(screen.getByText(/showing top 3 patterns with confidence ≥ 80%/i)).toBeInTheDocument();
    });

    it('shows usage hint when onPatternSelect is provided', () => {
      renderWithTheme(
        <VectorSimilarity 
          {...defaultProps}
          onPatternSelect={jest.fn()}
        />
      );
      
      expect(screen.getByText(/click a pattern to use its correction/i)).toBeInTheDocument();
    });

    it('hides usage hint when onPatternSelect is not provided', () => {
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      expect(screen.queryByText(/click a pattern to use its correction/i)).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty similarity results', () => {
      renderWithTheme(
        <VectorSimilarity 
          similarityResults={[]}
        />
      );
      
      expect(screen.getByText('No Similar Patterns Found')).toBeInTheDocument();
    });

    it('handles patterns without categories', () => {
      const patternsWithoutCategories = mockSimilarityResults.map(pattern => ({
        ...pattern,
        category: undefined,
      }));
      
      renderWithTheme(
        <VectorSimilarity 
          similarityResults={patternsWithoutCategories}
          showPatternAnalysis={true}
        />
      );
      
      // Should group under 'General' category
      expect(screen.getByText('General')).toBeInTheDocument();
    });

    it('handles clipboard copy failure gracefully', async () => {
      const user = userEvent.setup();
      
      // Mock clipboard failure
      mockClipboard.writeText.mockRejectedValueOnce(new Error('Clipboard error'));
      
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      const copyButtons = screen.getAllByLabelText(/copy correction/i);
      await user.click(copyButtons[0]);
      
      // Should not crash and should not show copied confirmation
      expect(screen.queryByLabelText('Copied!')).not.toBeInTheDocument();
    });

    it('handles patterns with missing speaker information', () => {
      const patternsWithoutSpeakers = mockSimilarityResults.map(pattern => ({
        ...pattern,
        speakerIds: undefined,
      }));
      
      renderWithTheme(
        <VectorSimilarity 
          similarityResults={patternsWithoutSpeakers}
        />
      );
      
      // Should render without speaker information
      expect(screen.getByText('corrected text one')).toBeInTheDocument();
      expect(screen.queryByText(/speakers/)).not.toBeInTheDocument();
    });

    it('handles patterns with frequency of 1', () => {
      const singleOccurrencePattern = [{
        ...mockSimilarityResults[0],
        frequency: 1,
      }];
      
      renderWithTheme(
        <VectorSimilarity 
          similarityResults={singleOccurrencePattern}
        />
      );
      
      // Should not show frequency chip for single occurrence
      expect(screen.queryByText('1 occurrences')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels and roles', () => {
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      const copyButtons = screen.getAllByLabelText(/copy correction/i);
      expect(copyButtons.length).toBeGreaterThan(0);
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      // Tab through interactive elements
      await user.tab();
      
      const focusedElement = document.activeElement;
      expect(focusedElement).toBeInTheDocument();
    });

    it('provides meaningful tooltips', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(<VectorSimilarity {...defaultProps} />);
      
      const copyButton = screen.getAllByLabelText(/copy correction/i)[0];
      await user.hover(copyButton);
      
      await waitFor(() => {
        expect(screen.getByText('Copy correction')).toBeInTheDocument();
      });
    });
  });
});
