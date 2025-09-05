/**
 * Enhanced Correction Input Component
 * Supports voice input, real-time validation, and AI-assisted suggestions
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Typography,
  Chip,
  Alert,
  CircularProgress,
  Tooltip,
  FormControl,
  FormLabel,
  FormHelperText,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Mic as MicIcon,
  MicOff as MicOffIcon,
  VolumeUp as VolumeUpIcon,
  AutoAwesome as AIIcon,
  Check as CheckIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import type { SimilarityResult, ValidationError } from '@domain/types';

export interface CorrectionInputProps {
  value: string;
  onChange: (value: string) => void;
  originalText: string;
  similarPatterns?: SimilarityResult[];
  onSimilaritySearch?: (text: string) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  validationErrors?: ValidationError[];
  placeholder?: string;
  maxLength?: number;
  voiceInputEnabled?: boolean;
  aiSuggestionsEnabled?: boolean;
}

export const CorrectionInput: React.FC<CorrectionInputProps> = ({
  value,
  onChange,
  originalText,
  similarPatterns = [],
  onSimilaritySearch,
  disabled = false,
  required = false,
  error,
  validationErrors = [],
  placeholder = "Enter the corrected text...",
  maxLength = 1000,
  voiceInputEnabled = true,
  aiSuggestionsEnabled = true,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Voice input state
  const [isRecording, setIsRecording] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  
  // AI suggestions state
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  
  // Text-to-speech state
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  // Initialize speech recognition
  useEffect(() => {
    if (voiceInputEnabled && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        setIsRecording(true);
      };
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        onChange(transcript);
        setIsRecording(false);
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };
      
      recognition.onend = () => {
        setIsRecording(false);
      };
      
      recognitionRef.current = recognition;
      setVoiceSupported(true);
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [voiceInputEnabled, onChange]);

  // Handle voice input toggle
  const handleVoiceToggle = useCallback(() => {
    if (!recognitionRef.current || disabled) return;
    
    if (isRecording) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  }, [isRecording, disabled]);

  // Handle text-to-speech
  const handleSpeak = useCallback((text: string) => {
    if (!text || disabled || isSpeaking) return;
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.8;
    utterance.pitch = 1;
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    
    speechSynthesis.speak(utterance);
  }, [disabled, isSpeaking]);

  // Handle text change with similarity search
  const handleTextChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    
    if (newValue.length <= maxLength) {
      onChange(newValue);
      
      // Trigger similarity search with debouncing
      if (onSimilaritySearch && newValue.length > 3) {
        setIsLoadingSuggestions(true);
        const timeoutId = setTimeout(() => {
          onSimilaritySearch(newValue);
          setIsLoadingSuggestions(false);
        }, 500);
        
        return () => clearTimeout(timeoutId);
      }
    }
  }, [onChange, maxLength, onSimilaritySearch]);

  // Handle suggestion selection
  const handleSuggestionSelect = useCallback((suggestion: SimilarityResult) => {
    onChange(suggestion.suggestedCorrection);
    setShowSuggestions(false);
  }, [onChange]);

  // Toggle suggestions visibility
  const handleToggleSuggestions = useCallback(() => {
    setShowSuggestions(prev => !prev);
  }, []);

  // Calculate text similarity score
  const calculateSimilarity = useCallback((text1: string, text2: string): number => {
    const longer = text1.length > text2.length ? text1 : text2;
    const shorter = text1.length > text2.length ? text2 : text1;
    
    if (longer.length === 0) return 1.0;
    
    const editDistance = levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  }, []);

  // Levenshtein distance calculation
  const levenshteinDistance = useCallback((str1: string, str2: string): number => {
    const matrix = [];
    
    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i];
    }
    
    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j;
    }
    
    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    
    return matrix[str2.length][str1.length];
  }, []);

  // Get similarity score for current text
  const similarityScore = calculateSimilarity(originalText, value);
  const isSignificantChange = similarityScore < 0.8;

  return (
    <FormControl
      component="fieldset"
      error={!!error}
      disabled={disabled}
      fullWidth
    >
      <FormLabel
        component="legend"
        sx={{ mb: 2 }}
        role="group"
        aria-label="Correction input"
      >
        Corrected Text
        {required && (
          <Typography component="span" color="error" sx={{ ml: 0.5 }}>
            *
          </Typography>
        )}
      </FormLabel>

      {/* Original Text Reference */}
      <Box sx={{ mb: 2, p: 2, backgroundColor: theme.palette.grey[50], borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Original Text:
        </Typography>
        <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
          {originalText}
          <Tooltip title="Listen to original text">
            <IconButton
              size="small"
              onClick={() => handleSpeak(originalText)}
              disabled={disabled || isSpeaking}
              sx={{ ml: 1 }}
            >
              <VolumeUpIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Typography>
      </Box>

      {/* Correction Input Field */}
      <TextField
        value={value}
        onChange={handleTextChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        error={!!error}
        multiline
        rows={4}
        fullWidth
        inputProps={{
          maxLength,
          'aria-describedby': 'correction-helper-text',
        }}
        InputProps={{
          endAdornment: (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              {/* Voice Input Button */}
              {voiceInputEnabled && voiceSupported && (
                <Tooltip title={isRecording ? "Stop recording" : "Start voice input"}>
                  <IconButton
                    onClick={handleVoiceToggle}
                    disabled={disabled}
                    color={isRecording ? "error" : "default"}
                    size="small"
                  >
                    {isRecording ? <MicOffIcon /> : <MicIcon />}
                  </IconButton>
                </Tooltip>
              )}
              
              {/* AI Suggestions Button */}
              {aiSuggestionsEnabled && similarPatterns.length > 0 && (
                <Tooltip title="Show AI suggestions">
                  <IconButton
                    onClick={handleToggleSuggestions}
                    disabled={disabled}
                    color={showSuggestions ? "primary" : "default"}
                    size="small"
                  >
                    {isLoadingSuggestions ? (
                      <CircularProgress size={16} />
                    ) : (
                      <AIIcon />
                    )}
                  </IconButton>
                </Tooltip>
              )}
              
              {/* Text-to-Speech Button */}
              {value && (
                <Tooltip title="Listen to correction">
                  <IconButton
                    onClick={() => handleSpeak(value)}
                    disabled={disabled || isSpeaking}
                    size="small"
                  >
                    <VolumeUpIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          ),
        }}
      />

      {/* Character Count */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
        <Typography variant="caption" color="text.secondary">
          {value.length} / {maxLength} characters
        </Typography>
        
        {/* Similarity Score */}
        {value && (
          <Typography 
            variant="caption" 
            color={isSignificantChange ? "success.main" : "text.secondary"}
          >
            Similarity: {Math.round(similarityScore * 100)}%
          </Typography>
        )}
      </Box>

      {/* AI Suggestions */}
      {showSuggestions && similarPatterns.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" gutterBottom>
            AI Suggestions:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {similarPatterns.slice(0, 5).map((pattern, index) => (
              <Chip
                key={pattern.patternId}
                label={pattern.suggestedCorrection}
                variant="outlined"
                clickable
                onClick={() => handleSuggestionSelect(pattern)}
                icon={<CheckIcon />}
                size="small"
                sx={{
                  maxWidth: '200px',
                  '& .MuiChip-label': {
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  },
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <Box sx={{ mt: 1 }}>
          {validationErrors.map((validationError, index) => (
            <Alert key={index} severity="error" size="small" sx={{ mt: 0.5 }}>
              {validationError.message}
            </Alert>
          ))}
        </Box>
      )}

      {/* Error Message */}
      {error && (
        <FormHelperText error id="correction-helper-text">
          {error}
        </FormHelperText>
      )}

      {/* Recording Indicator */}
      {isRecording && (
        <Alert severity="info" sx={{ mt: 1 }}>
          🎤 Recording... Speak clearly and pause when finished.
        </Alert>
      )}
    </FormControl>
  );
};
