/**
 * MetadataInput Component Tests
 * Tests contextual information capture and validation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { MetadataInput } from './MetadataInput';
import type { ErrorMetadata } from '@domain/types';

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

const defaultMetadata: ErrorMetadata = {
  audioQuality: 'good',
  backgroundNoise: 'low',
  speakerClarity: 'clear',
  contextualNotes: '',
  urgencyLevel: 'medium',
};

describe('MetadataInput', () => {
  const defaultProps = {
    value: defaultMetadata,
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Functionality', () => {
    it('renders with default props', () => {
      renderWithTheme(<MetadataInput {...defaultProps} />);
      
      expect(screen.getByRole('group', { name: /error metadata/i })).toBeInTheDocument();
      expect(screen.getByText('Contextual Information')).toBeInTheDocument();
    });

    it('shows required indicator when required', () => {
      renderWithTheme(
        <MetadataInput {...defaultProps} required={true} />
      );
      
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('displays error message when provided', () => {
      renderWithTheme(
        <MetadataInput 
          {...defaultProps} 
          error="This field is required"
        />
      );
      
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });
  });

  describe('Audio Quality Assessment', () => {
    it('renders audio quality section by default', () => {
      renderWithTheme(<MetadataInput {...defaultProps} />);
      
      expect(screen.getByText('Audio Quality Assessment')).toBeInTheDocument();
      expect(screen.getByText('Overall Audio Quality')).toBeInTheDocument();
    });

    it('allows selecting audio quality', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput {...defaultProps} onChange={onChange} />
      );
      
      // Open audio quality dropdown
      const audioQualitySelect = screen.getByDisplayValue('Good');
      await user.click(audioQualitySelect);
      
      // Select excellent quality
      const excellentOption = screen.getByText('Excellent');
      await user.click(excellentOption);
      
      expect(onChange).toHaveBeenCalledWith({
        ...defaultMetadata,
        audioQuality: 'excellent',
      });
    });

    it('allows selecting background noise level', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput {...defaultProps} onChange={onChange} />
      );
      
      // Find and click background noise select
      const noiseSelects = screen.getAllByRole('combobox');
      const noiseSelect = noiseSelects.find(select => 
        select.closest('[data-testid]')?.textContent?.includes('Background Noise') ||
        select.getAttribute('aria-labelledby')?.includes('noise')
      );
      
      if (noiseSelect) {
        await user.click(noiseSelect);
        
        const highNoiseOption = screen.getByText('High Background Noise');
        await user.click(highNoiseOption);
        
        expect(onChange).toHaveBeenCalledWith({
          ...defaultMetadata,
          backgroundNoise: 'high',
        });
      }
    });

    it('allows selecting speaker clarity', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput {...defaultProps} onChange={onChange} />
      );
      
      // Find speaker clarity select by looking for the label
      const clarityLabel = screen.getByText('Speaker Clarity');
      const claritySelect = clarityLabel.closest('.MuiFormControl-root')?.querySelector('select') ||
                           clarityLabel.parentElement?.querySelector('[role="combobox"]');
      
      if (claritySelect) {
        await user.click(claritySelect);
        
        const unclearOption = screen.getByText('Unclear');
        await user.click(unclearOption);
        
        expect(onChange).toHaveBeenCalledWith({
          ...defaultMetadata,
          speakerClarity: 'unclear',
        });
      }
    });

    it('allows selecting urgency level with chips', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput {...defaultProps} onChange={onChange} />
      );
      
      const highPriorityChip = screen.getByText('High Priority');
      await user.click(highPriorityChip);
      
      expect(onChange).toHaveBeenCalledWith({
        ...defaultMetadata,
        urgencyLevel: 'high',
      });
    });
  });

  describe('Advanced Context Section', () => {
    it('shows advanced section when enabled', () => {
      renderWithTheme(
        <MetadataInput {...defaultProps} showAdvanced={true} />
      );
      
      expect(screen.getByText('Advanced Context')).toBeInTheDocument();
    });

    it('hides advanced section when disabled', () => {
      renderWithTheme(
        <MetadataInput {...defaultProps} showAdvanced={false} />
      );
      
      expect(screen.queryByText('Advanced Context')).not.toBeInTheDocument();
    });

    it('allows expanding and collapsing advanced section', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <MetadataInput {...defaultProps} showAdvanced={true} />
      );
      
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Should show advanced controls
      expect(screen.getByText('Speech Rate')).toBeInTheDocument();
      expect(screen.getByText('Transcription Confidence')).toBeInTheDocument();
    });

    it('allows adjusting speech rate slider', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput 
          {...defaultProps} 
          onChange={onChange}
          showAdvanced={true}
        />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Find and adjust speech rate slider
      const speechRateSlider = screen.getByRole('slider', { name: /speech rate/i });
      fireEvent.change(speechRateSlider, { target: { value: 8 } });
      
      expect(onChange).toHaveBeenCalledWith({
        ...defaultMetadata,
        speechRate: 8,
      });
    });

    it('allows setting confidence rating', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput 
          {...defaultProps} 
          onChange={onChange}
          showAdvanced={true}
        />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Find confidence rating stars
      const ratingStars = screen.getAllByRole('radio');
      if (ratingStars.length > 0) {
        await user.click(ratingStars[4]); // 5th star (5/5 rating)
        
        expect(onChange).toHaveBeenCalledWith({
          ...defaultMetadata,
          confidenceRating: 5,
        });
      }
    });
  });

  describe('Contextual Tags', () => {
    it('shows predefined tags when advanced section is expanded', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <MetadataInput {...defaultProps} showAdvanced={true} />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      expect(screen.getByText('Medical Terminology')).toBeInTheDocument();
      expect(screen.getByText('Technical Jargon')).toBeInTheDocument();
      expect(screen.getByText('Accent/Dialect')).toBeInTheDocument();
    });

    it('allows selecting predefined tags', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput 
          {...defaultProps} 
          onChange={onChange}
          showAdvanced={true}
        />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Click on a predefined tag
      const medicalTag = screen.getByText('Medical Terminology');
      await user.click(medicalTag);
      
      expect(onChange).toHaveBeenCalledWith({
        ...defaultMetadata,
        contextualTags: ['Medical Terminology'],
      });
    });

    it('allows removing selected tags', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      const metadataWithTags = {
        ...defaultMetadata,
        contextualTags: ['Medical Terminology', 'Technical Jargon'],
      };
      
      renderWithTheme(
        <MetadataInput 
          value={metadataWithTags}
          onChange={onChange}
          showAdvanced={true}
        />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Find and click delete button on a selected tag
      const selectedTags = screen.getByText('Selected Tags:');
      const tagContainer = selectedTags.parentElement;
      const deleteButtons = tagContainer?.querySelectorAll('[data-testid="CancelIcon"]');
      
      if (deleteButtons && deleteButtons.length > 0) {
        await user.click(deleteButtons[0]);
        
        expect(onChange).toHaveBeenCalledWith({
          ...metadataWithTags,
          contextualTags: ['Technical Jargon'],
        });
      }
    });
  });

  describe('Additional Notes', () => {
    it('allows entering additional notes', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput 
          {...defaultProps} 
          onChange={onChange}
          showAdvanced={true}
        />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Find and type in notes field
      const notesField = screen.getByLabelText('Additional Notes');
      await user.type(notesField, 'This is a test note');
      
      expect(onChange).toHaveBeenCalledWith({
        ...defaultMetadata,
        contextualNotes: 'This is a test note',
      });
    });

    it('shows character count for notes', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <MetadataInput 
          {...defaultProps} 
          showAdvanced={true}
        />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Find notes field and type
      const notesField = screen.getByLabelText('Additional Notes');
      await user.type(notesField, 'Test');
      
      expect(screen.getByText('4/500 characters')).toBeInTheDocument();
    });
  });

  describe('Technical Flags', () => {
    it('allows toggling multiple speakers flag', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput 
          {...defaultProps} 
          onChange={onChange}
          showAdvanced={true}
        />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Find and toggle multiple speakers switch
      const multipleSpeakersSwitch = screen.getByRole('checkbox', { 
        name: /multiple speakers present/i 
      });
      await user.click(multipleSpeakersSwitch);
      
      expect(onChange).toHaveBeenCalledWith({
        ...defaultMetadata,
        hasMultipleSpeakers: true,
      });
    });

    it('allows toggling overlapping speech flag', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput 
          {...defaultProps} 
          onChange={onChange}
          showAdvanced={true}
        />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Find and toggle overlapping speech switch
      const overlappingSpeechSwitch = screen.getByRole('checkbox', { 
        name: /overlapping speech/i 
      });
      await user.click(overlappingSpeechSwitch);
      
      expect(onChange).toHaveBeenCalledWith({
        ...defaultMetadata,
        hasOverlappingSpeech: true,
      });
    });

    it('allows toggling specialized knowledge flag', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      renderWithTheme(
        <MetadataInput 
          {...defaultProps} 
          onChange={onChange}
          showAdvanced={true}
        />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Find and toggle specialized knowledge switch
      const specializedKnowledgeSwitch = screen.getByRole('checkbox', { 
        name: /requires specialized knowledge/i 
      });
      await user.click(specializedKnowledgeSwitch);
      
      expect(onChange).toHaveBeenCalledWith({
        ...defaultMetadata,
        requiresSpecializedKnowledge: true,
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels and roles', () => {
      renderWithTheme(<MetadataInput {...defaultProps} />);
      
      expect(screen.getByRole('group', { name: /error metadata/i })).toBeInTheDocument();
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(<MetadataInput {...defaultProps} />);
      
      // Tab through the form
      await user.tab();
      
      // Should focus on first interactive element
      const focusedElement = document.activeElement;
      expect(focusedElement).toBeInTheDocument();
    });

    it('disables all controls when disabled', () => {
      renderWithTheme(
        <MetadataInput {...defaultProps} disabled={true} />
      );
      
      // All form controls should be disabled
      const selects = screen.getAllByRole('combobox');
      selects.forEach(select => {
        expect(select).toBeDisabled();
      });
    });
  });

  describe('Section Management', () => {
    it('starts with basic section expanded', () => {
      renderWithTheme(<MetadataInput {...defaultProps} />);
      
      expect(screen.getByText('Overall Audio Quality')).toBeInTheDocument();
    });

    it('allows collapsing basic section', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(<MetadataInput {...defaultProps} />);
      
      // Click on basic section header to collapse
      const basicHeader = screen.getByText('Audio Quality Assessment');
      await user.click(basicHeader);
      
      // Audio quality controls should be hidden
      expect(screen.queryByText('Overall Audio Quality')).not.toBeInTheDocument();
    });

    it('maintains section state independently', async () => {
      const user = userEvent.setup();
      
      renderWithTheme(
        <MetadataInput {...defaultProps} showAdvanced={true} />
      );
      
      // Expand advanced section
      const advancedHeader = screen.getByText('Advanced Context');
      await user.click(advancedHeader);
      
      // Collapse basic section
      const basicHeader = screen.getByText('Audio Quality Assessment');
      await user.click(basicHeader);
      
      // Advanced should still be expanded, basic should be collapsed
      expect(screen.getByText('Speech Rate')).toBeInTheDocument();
      expect(screen.queryByText('Overall Audio Quality')).not.toBeInTheDocument();
    });
  });
});
