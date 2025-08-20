/**
 * Error Categorization Interface Component
 * Supports hierarchical categories with search and validation
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  Box,
  TextField,
  Chip,
  Typography,
  InputAdornment,
  IconButton,
  Alert,
  Tooltip,
  FormControl,
  FormLabel,
  FormHelperText,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import type { ErrorCategory } from '@domain/types';

export interface ErrorCategorizationProps {
  categories: ErrorCategory[];
  selectedCategories: string[];
  onCategoriesChange: (categories: string[]) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  maxSelections?: number;
  searchable?: boolean;
  showHierarchy?: boolean;
}

export const ErrorCategorization: React.FC<ErrorCategorizationProps> = ({
  categories,
  selectedCategories,
  onCategoriesChange,
  disabled = false,
  required = false,
  error,
  maxSelections = 10,
  searchable = true,
  showHierarchy = true,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  // Filter categories based on search term
  const filteredCategories = useMemo(() => {
    if (!searchTerm) return categories;
    
    return categories.filter(category =>
      category.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      category.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [categories, searchTerm]);

  // Group categories by parent-child relationships
  const categorizedGroups = useMemo(() => {
    const parentCategories = filteredCategories.filter(cat => !cat.parentCategory);
    const childCategories = filteredCategories.filter(cat => cat.parentCategory);
    
    return parentCategories.map(parent => ({
      parent,
      children: childCategories.filter(child => child.parentCategory === parent.id),
    }));
  }, [filteredCategories]);

  // Get all child categories for a parent
  const getChildCategories = useCallback((parentId: string): string[] => {
    return categories
      .filter(cat => cat.parentCategory === parentId)
      .map(cat => cat.id);
  }, [categories]);

  // Get parent category for a child
  const getParentCategory = useCallback((childId: string): string | undefined => {
    const child = categories.find(cat => cat.id === childId);
    return child?.parentCategory;
  }, [categories]);

  // Handle category selection
  const handleCategoryToggle = useCallback((categoryId: string) => {
    if (disabled) return;

    const isSelected = selectedCategories.includes(categoryId);
    let newSelection: string[];

    if (isSelected) {
      // Deselecting - remove category and its children
      const childIds = getChildCategories(categoryId);
      newSelection = selectedCategories.filter(
        id => id !== categoryId && !childIds.includes(id)
      );
    } else {
      // Selecting - check max limit
      if (selectedCategories.length >= maxSelections) {
        return;
      }

      // Add category
      newSelection = [...selectedCategories, categoryId];

      // If it's a child category, also select parent
      const parentId = getParentCategory(categoryId);
      if (parentId && !selectedCategories.includes(parentId)) {
        newSelection.push(parentId);
      }

      // If it's a parent category, check if we should auto-select children
      const childIds = getChildCategories(categoryId);
      if (childIds.length === 0) {
        // No children, just add the category
      } else {
        // Has children - for now, just add the parent
        // Could implement auto-select children logic here
      }
    }

    onCategoriesChange(newSelection);
  }, [disabled, selectedCategories, maxSelections, onCategoriesChange, getChildCategories, getParentCategory]);

  // Handle search
  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  }, []);

  const handleClearSearch = useCallback(() => {
    setSearchTerm('');
  }, []);

  // Render category chip
  const renderCategoryChip = useCallback((category: ErrorCategory, isChild = false) => {
    const isSelected = selectedCategories.includes(category.id);
    const isDisabled = disabled || !category.isActive;

    return (
      <Tooltip
        key={category.id}
        title={category.description}
        placement="top"
      >
        <Chip
          label={category.name}
          variant={isSelected ? 'filled' : 'outlined'}
          color={isSelected ? 'primary' : 'default'}
          disabled={isDisabled}
          clickable={!isDisabled}
          onClick={() => handleCategoryToggle(category.id)}
          icon={isSelected ? <CheckIcon /> : undefined}
          size={isChild ? 'small' : 'medium'}
          sx={{
            margin: 0.5,
            ...(isChild && {
              marginLeft: 2,
              opacity: 0.8,
            }),
          }}
          aria-pressed={isSelected}
          role="button"
          tabIndex={isDisabled ? -1 : 0}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault();
              handleCategoryToggle(category.id);
            }
          }}
        />
      </Tooltip>
    );
  }, [selectedCategories, disabled, handleCategoryToggle]);

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
        aria-label="Error categories"
      >
        Error Categories
        {required && (
          <Typography component="span" color="error" sx={{ ml: 0.5 }}>
            *
          </Typography>
        )}
      </FormLabel>

      {/* Search Input */}
      {searchable && (
        <TextField
          placeholder="Search categories..."
          value={searchTerm}
          onChange={handleSearchChange}
          disabled={disabled}
          size="small"
          sx={{ mb: 2 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton
                  size="small"
                  onClick={handleClearSearch}
                  aria-label="Clear search"
                  disabled={disabled}
                >
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      )}

      {/* Selection Counter */}
      {maxSelections > 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {selectedCategories.length} of {maxSelections} categories selected
        </Typography>
      )}

      {/* Categories Display */}
      <Box sx={{ minHeight: 100 }}>
        {filteredCategories.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
            No categories found
          </Typography>
        ) : showHierarchy ? (
          // Hierarchical display
          categorizedGroups.map(({ parent, children }) => (
            <Box key={parent.id} data-testid={`category-group-${parent.id}`} sx={{ mb: 2 }}>
              {renderCategoryChip(parent)}
              {children.length > 0 && (
                <Box sx={{ ml: 2, mt: 1 }}>
                  {children.map(child => renderCategoryChip(child, true))}
                </Box>
              )}
            </Box>
          ))
        ) : (
          // Flat display
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {filteredCategories.map(category => renderCategoryChip(category))}
          </Box>
        )}
      </Box>

      {/* Error Message */}
      {error && (
        <FormHelperText error>
          {error}
        </FormHelperText>
      )}

      {/* Validation Alert */}
      {required && selectedCategories.length === 0 && !error && (
        <Alert severity="info" sx={{ mt: 1 }}>
          Please select at least one error category
        </Alert>
      )}

      {/* Max Selection Warning */}
      {selectedCategories.length >= maxSelections && (
        <Alert severity="warning" sx={{ mt: 1 }}>
          Maximum number of categories selected ({maxSelections})
        </Alert>
      )}
    </FormControl>
  );
};
