/**
 * CorrectionInput Component Tests
 * Tests voice input, AI suggestions, and validation functionality
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CorrectionInput } from './CorrectionInput';
import type { SimilarityResult, ValidationError } from '@domain/types';

// Mock speech recognition
const mockSpeechRecognition = {
  start: jest.fn(),
  stop: jest.fn(),
  abort: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  continuous: false,
  interimResults: false,
  lang: 'en-US',
  onstart: null,
  onresult: null,
  onerror: null,
  onend: null,
};

// Mock speech synthesis
const mockSpeechSynthesis = {
  speak: jest.fn(),
  cancel: jest.fn(),
  pause: jest.fn(),
  resume: jest.fn(),
  getVoices: jest.fn(() => []),
};

// Setup global mocks
beforeAll(() => {
  global.webkitSpeechRecognition = jest.fn(() => mockSpeechRecognition);
  global.SpeechRecognition = jest.fn(() => mockSpeechRecognition);
  global.speechSynthesis = mockSpeechSynthesis;
  global.SpeechSynthesisUtterance = jest.fn();
});

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

const mockSimilarPatterns: SimilarityResult[] = [
  {
    patternId: 'pattern-1',
    similarText: 'original error text',
    confidence: 0.95,
    frequency: 5,
    suggestedCorrection: 'corrected text suggestion 1',
    speakerIds: ['speaker-1', 'speaker-2'],
    category: 'pronunciation',
  },
  {
    patternId: 'pattern-2',
    similarText: 'another error',
    confidence: 0.87,
    frequency: 3,
    suggestedCorrection: 'corrected text suggestion 2',
    speakerIds: ['speaker-3'],
    category: 'grammar',
  },
];

const mockValidationErrors: ValidationError[] = [
  {
    field: 'correctionText',
    message: 'Correction text is required',
    code: 'REQUIRED',
  },
];

describe('CorrectionInput', () => {
  const defaultProps = {
    value: '',
    onChange: jest.fn(),
    originalText: 'This is the original text with errors',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Functionality', () => {
    it('renders with default props', () => {
      renderWithTheme(<CorrectionInput {...defaultProps} />);
      
      expect(screen.getByLabelText(/corrected text/i)).toBeInTheDocument();
      expect(screen.getByText(/original text/i)).toBeInTheDocument();
      expect(screen.getByDisplayValue('')).toBeInTheDocument();
    });

    it('displays original text reference', () => {
      renderWithTheme(<CorrectionInput {...defaultProps} />);
      
      expect(screen.getByText(defaultProps.originalText)).toBeInTheDocument();
    });

    it('calls onChange when text is entered', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <CorrectionInput {...defaultProps} onChange={onChange} />
      );
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'corrected text');
      
      expect(onChange).toHaveBeenCalledWith('corrected text');
    });

    it('respects maxLength prop', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          onChange={onChange}
          maxLength={10}
        />
      );
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'this is a very long text that exceeds limit');
      
      // Should only call onChange for characters within limit
      expect(onChange).toHaveBeenLastCalledWith('this is a ');
    });

    it('shows character count', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          value="test text"
          maxLength={100}
        />
      );
      
      expect(screen.getByText('9 / 100 characters')).toBeInTheDocument();
    });
  });

  describe('Voice Input', () => {
    it('shows voice input button when enabled', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          voiceInputEnabled={true}
        />
      );
      
      expect(screen.getByLabelText(/start voice input/i)).toBeInTheDocument();
    });

    it('hides voice input button when disabled', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          voiceInputEnabled={false}
        />
      );
      
      expect(screen.queryByLabelText(/start voice input/i)).not.toBeInTheDocument();
    });

    it('starts speech recognition when voice button is clicked', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          voiceInputEnabled={true}
        />
      );
      
      const voiceButton = screen.getByLabelText(/start voice input/i);
      await user.click(voiceButton);
      
      expect(mockSpeechRecognition.start).toHaveBeenCalled();
    });

    it('handles speech recognition result', async () => {
      const onChange = jest.fn();
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          onChange={onChange}
          voiceInputEnabled={true}
        />
      );
      
      // Simulate speech recognition result
      act(() => {
        if (mockSpeechRecognition.onresult) {
          mockSpeechRecognition.onresult({
            results: [[{ transcript: 'voice input text' }]],
          } as any);
        }
      });
      
      expect(onChange).toHaveBeenCalledWith('voice input text');
    });

    it('shows recording indicator during voice input', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          voiceInputEnabled={true}
        />
      );
      
      const voiceButton = screen.getByLabelText(/start voice input/i);
      await user.click(voiceButton);
      
      // Simulate recording start
      act(() => {
        if (mockSpeechRecognition.onstart) {
          mockSpeechRecognition.onstart({} as any);
        }
      });
      
      expect(screen.getByText(/recording/i)).toBeInTheDocument();
    });
  });

  describe('AI Suggestions', () => {
    it('shows AI suggestions button when patterns are available', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          similarPatterns={mockSimilarPatterns}
          aiSuggestionsEnabled={true}
        />
      );
      
      expect(screen.getByLabelText(/show ai suggestions/i)).toBeInTheDocument();
    });

    it('displays suggestions when button is clicked', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          similarPatterns={mockSimilarPatterns}
          aiSuggestionsEnabled={true}
        />
      );
      
      const aiButton = screen.getByLabelText(/show ai suggestions/i);
      await user.click(aiButton);
      
      expect(screen.getByText('AI Suggestions:')).toBeInTheDocument();
      expect(screen.getByText('corrected text suggestion 1')).toBeInTheDocument();
      expect(screen.getByText('corrected text suggestion 2')).toBeInTheDocument();
    });

    it('applies suggestion when clicked', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          onChange={onChange}
          similarPatterns={mockSimilarPatterns}
          aiSuggestionsEnabled={true}
        />
      );
      
      // Open suggestions
      const aiButton = screen.getByLabelText(/show ai suggestions/i);
      await user.click(aiButton);
      
      // Click on first suggestion
      const suggestion = screen.getByText('corrected text suggestion 1');
      await user.click(suggestion);
      
      expect(onChange).toHaveBeenCalledWith('corrected text suggestion 1');
    });

    it('triggers similarity search on text change', async () => {
      const user = userEvent.setup();
      const onSimilaritySearch = jest.fn();
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          onSimilaritySearch={onSimilaritySearch}
        />
      );
      
      const input = screen.getByRole('textbox');
      await user.type(input, 'test search text');
      
      // Wait for debounced search
      await waitFor(() => {
        expect(onSimilaritySearch).toHaveBeenCalledWith('test search text');
      }, { timeout: 1000 });
    });
  });

  describe('Text-to-Speech', () => {
    it('shows speak button for original text', () => {
      renderWithTheme(<CorrectionInput {...defaultProps} />);
      
      expect(screen.getByLabelText(/listen to original text/i)).toBeInTheDocument();
    });

    it('shows speak button for correction text when available', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          value="corrected text"
        />
      );
      
      expect(screen.getByLabelText(/listen to correction/i)).toBeInTheDocument();
    });

    it('calls speech synthesis when speak button is clicked', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          value="test text"
        />
      );
      
      const speakButton = screen.getByLabelText(/listen to correction/i);
      await user.click(speakButton);
      
      expect(mockSpeechSynthesis.speak).toHaveBeenCalled();
    });
  });

  describe('Validation', () => {
    it('displays validation errors', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          validationErrors={mockValidationErrors}
        />
      );
      
      expect(screen.getByText('Correction text is required')).toBeInTheDocument();
    });

    it('shows error state when error prop is provided', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          error="This field is required"
        />
      );
      
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('shows required indicator when required', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          required={true}
        />
      );
      
      expect(screen.getByText('*')).toBeInTheDocument();
    });
  });

  describe('Similarity Score', () => {
    it('calculates and displays similarity score', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          value="This is the original text with corrections"
          originalText="This is the original text with errors"
        />
      );
      
      expect(screen.getByText(/similarity:/i)).toBeInTheDocument();
    });

    it('shows high similarity for similar text', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          value="This is the original text"
          originalText="This is the original text"
        />
      );
      
      expect(screen.getByText(/similarity: 100%/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      renderWithTheme(<CorrectionInput {...defaultProps} />);
      
      expect(screen.getByRole('group', { name: /correction input/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/corrected text/i)).toBeInTheDocument();
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(<CorrectionInput {...defaultProps} />);
      
      const input = screen.getByRole('textbox');
      await user.tab();
      
      expect(input).toHaveFocus();
    });

    it('disables all interactions when disabled', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          disabled={true}
          voiceInputEnabled={true}
        />
      );
      
      expect(screen.getByRole('textbox')).toBeDisabled();
      expect(screen.getByLabelText(/start voice input/i)).toBeDisabled();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty original text', () => {
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          originalText=""
        />
      );
      
      expect(screen.getByLabelText(/corrected text/i)).toBeInTheDocument();
    });

    it('handles speech recognition errors gracefully', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          voiceInputEnabled={true}
        />
      );
      
      const voiceButton = screen.getByLabelText(/start voice input/i);
      await user.click(voiceButton);
      
      // Simulate speech recognition error
      act(() => {
        if (mockSpeechRecognition.onerror) {
          mockSpeechRecognition.onerror({ error: 'network' } as any);
        }
      });
      
      // Should not crash and should reset recording state
      expect(screen.queryByText(/recording/i)).not.toBeInTheDocument();
    });

    it('handles missing speech synthesis gracefully', () => {
      // Temporarily remove speech synthesis
      const originalSpeechSynthesis = global.speechSynthesis;
      delete (global as any).speechSynthesis;
      
      renderWithTheme(
        <CorrectionInput 
          {...defaultProps} 
          value="test text"
        />
      );
      
      // Should render without crashing
      expect(screen.getByLabelText(/corrected text/i)).toBeInTheDocument();
      
      // Restore speech synthesis
      global.speechSynthesis = originalSpeechSynthesis;
    });
  });
});
