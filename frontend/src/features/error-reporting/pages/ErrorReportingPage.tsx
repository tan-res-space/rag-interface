/**
 * Error reporting page component
 * Demonstrates the implemented text selection and categorization components
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Divider,
} from '@mui/material';
import { TextSelection } from '../components/TextSelection';
import { ErrorCategorization } from '../components/ErrorCategorization';
import type { TextSelection as TextSelectionType, ErrorCategory } from '@domain/types';

// Sample text for demonstration
const sampleText = `This is a sample transcription text that contains various types of errors that need to be identified and categorized. The text includes grammatical mistakes, spelling errors, and punctuation issues that quality assurance personnel need to review and correct. Users can select multiple non-contiguous text segments to report different types of errors within the same document.`;

// Sample error categories
const sampleCategories: ErrorCategory[] = [
  {
    id: 'grammar',
    name: 'Grammar',
    description: 'Grammatical errors including subject-verb agreement, tense issues, and sentence structure',
    isActive: true,
  },
  {
    id: 'spelling',
    name: 'Spelling',
    description: 'Spelling mistakes, typos, and incorrect word usage',
    isActive: true,
  },
  {
    id: 'punctuation',
    name: 'Punctuation',
    description: 'Missing or incorrect punctuation marks',
    parentCategory: 'grammar',
    isActive: true,
  },
  {
    id: 'syntax',
    name: 'Syntax',
    description: 'Word order and sentence construction errors',
    parentCategory: 'grammar',
    isActive: true,
  },
  {
    id: 'terminology',
    name: 'Terminology',
    description: 'Incorrect technical terms or domain-specific vocabulary',
    isActive: true,
  },
  {
    id: 'formatting',
    name: 'Formatting',
    description: 'Text formatting and structure issues',
    isActive: true,
  },
];

const ErrorReportingPage: React.FC = () => {
  const [textSelections, setTextSelections] = useState<TextSelectionType[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Error Reporting Interface
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Select text segments below and categorize the types of errors found. This demonstrates the advanced text selection and error categorization components implemented in Phase 2.
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Text Selection Component */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Text Selection
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select text segments to identify errors. Hold Ctrl/Cmd for multiple selections.
          </Typography>

          <TextSelection
            text={sampleText}
            selections={textSelections}
            onSelectionChange={setTextSelections}
            maxSelections={5}
            allowOverlapping={false}
          />
        </Paper>

        {/* Error Categorization Component */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Error Categories
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select the types of errors found in the selected text.
          </Typography>

          <ErrorCategorization
            categories={sampleCategories}
            selectedCategories={selectedCategories}
            onCategoriesChange={setSelectedCategories}
            maxSelections={3}
            required={true}
          />
        </Paper>

        {/* Selection Summary */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Selection Summary
          </Typography>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" gutterBottom>
            Selected Text Segments ({textSelections.length}):
          </Typography>
          {textSelections.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No text selected
            </Typography>
          ) : (
            <Box sx={{ mb: 2 }}>
              {textSelections.map((selection, index) => (
                <Box key={selection.selectionId} sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    <strong>Selection {index + 1}:</strong> "{selection.text}"
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Position: {selection.startPosition}-{selection.endPosition}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}

          <Typography variant="subtitle2" gutterBottom>
            Selected Categories ({selectedCategories.length}):
          </Typography>
          {selectedCategories.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No categories selected
            </Typography>
          ) : (
            <Box>
              {selectedCategories.map(categoryId => {
                const category = sampleCategories.find(cat => cat.id === categoryId);
                return (
                  <Typography key={categoryId} variant="body2">
                    • {category?.name}: {category?.description}
                  </Typography>
                );
              })}
            </Box>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default ErrorReportingPage;
