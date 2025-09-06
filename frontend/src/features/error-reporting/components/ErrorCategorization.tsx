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
            margin: 0,
            minWidth: isChild ? '80px' : '100px',
            height: isChild ? '28px' : '32px',
            '& .MuiChip-label': {
              px: isChild ? 1 : 1.5,
              fontSize: isChild ? '0.75rem' : '0.875rem',
              fontWeight: isSelected ? 600 : 500,
            },
            ...(isChild && {
              opacity: 0.9,
            }),
            '&:hover': {
              transform: 'translateY(-1px)',
              boxShadow: 2,
            },
            transition: 'all 0.2s ease-in-out',
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
      <Box sx={{ minHeight: 120 }}>
        {filteredCategories.length === 0 ? (
          <Box sx={{
            p: 4,
            textAlign: 'center',
            border: '1px dashed',
            borderColor: 'divider',
            borderRadius: 2,
            backgroundColor: 'grey.50'
          }}>
            <Typography variant="body2" color="text.secondary">
              No categories found matching your search
            </Typography>
          </Box>
        ) : showHierarchy ? (
          // Hierarchical display - organized in horizontal grid
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 2,
            width: '100%'
          }}>
            {categorizedGroups.map(({ parent, children }) => (
              <Box
                key={parent.id}
                data-testid={`category-group-${parent.id}`}
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 1,
                  p: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 2,
                  backgroundColor: 'background.paper',
                  boxShadow: 1,
                  '&:hover': {
                    boxShadow: 2,
                  }
                }}
              >
                {/* Parent category header */}
                <Box sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  mb: 1,
                  pb: 1,
                  borderBottom: '1px solid',
                  borderColor: 'divider'
                }}>
                  <Typography
                    variant="subtitle2"
                    color="primary"
                    sx={{
                      fontWeight: 600,
                      minWidth: 'fit-content'
                    }}
                  >
                    {parent.name}
                  </Typography>
                  {renderCategoryChip(parent)}
                </Box>

                {/* Child categories in horizontal layout */}
                {children.length > 0 && (
                  <Box>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{
                        display: 'block',
                        mb: 1,
                        fontWeight: 500
                      }}
                    >
                      Subcategories:
                    </Typography>
                    <Box sx={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: 0.75,
                      alignItems: 'center'
                    }}>
                      {children.map(child => renderCategoryChip(child, true))}
                    </Box>
                  </Box>
                )}
              </Box>
            ))}
          </Box>
        ) : (
          // Flat display - organized horizontally
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
            gap: 1.5,
            p: 2,
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            backgroundColor: 'background.paper'
          }}>
            {filteredCategories.map(category => (
              <Box key={category.id} sx={{ display: 'flex', justifyContent: 'center' }}>
                {renderCategoryChip(category)}
              </Box>
            ))}
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
