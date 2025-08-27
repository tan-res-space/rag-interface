# Speaker Management Feature

## Overview

The Speaker Management feature provides a comprehensive interface for managing speaker categorization, quality assessment, and bucket transitions in the ASR Error Reporting System. It includes advanced search capabilities, real-time statistics, and workflow management tools.

## Features

### 🔍 **Advanced Speaker Search & Selection**
- **Real-time search** with debounced input
- **Multi-criteria filtering** (bucket, quality trend, SER score range, data sufficiency)
- **Quick filter options** with speaker counts
- **Bulk selection** with advanced actions
- **Export capabilities** for selected speakers

### 📊 **Comprehensive Statistics & Analytics**
- **Bucket distribution** visualization
- **Quality metrics** dashboard
- **Trend analysis** with historical data
- **Data coverage** monitoring
- **Transition metrics** tracking

### 👥 **Speaker Management**
- **CRUD operations** for speakers
- **Detailed speaker profiles** with comprehensive views
- **Quality assessment** workflows
- **Bucket transition** request management
- **Historical data** tracking

### 🔄 **Workflow Orchestration**
- **Automated assessment** workflows
- **Bulk operations** for efficiency
- **Transition approval** process
- **Progress tracking** and notifications

## Architecture

### Component Structure

```
src/features/speaker-management/
├── components/
│   ├── SpeakerSearchAndSelection.tsx    # Main search interface
│   ├── SpeakerTable.tsx                 # Advanced data table
│   ├── SpeakerStatistics.tsx            # Statistics dashboard
│   ├── SpeakerDetailsDialog.tsx         # Detailed speaker view
│   ├── CreateSpeakerDialog.tsx          # Create/edit speaker form
│   └── BulkActionsToolbar.tsx           # Bulk operations toolbar
├── pages/
│   └── SpeakerManagementPage.tsx        # Main feature page
├── speaker-slice.ts                     # Redux state management
└── index.ts                             # Feature exports
```

### State Management

The feature uses Redux Toolkit for state management with the following structure:

```typescript
interface SpeakerState {
  // Data
  speakers: Speaker[];
  selectedSpeaker: Speaker | null;
  bucketStatistics: SpeakerBucketStats | null;
  
  // UI State
  searchFilters: SpeakerSearchFilters;
  selectedSpeakerIds: string[];
  viewMode: 'table' | 'grid' | 'analytics';
  
  // Pagination
  currentPage: number;
  pageSize: number;
  totalCount: number;
  
  // Loading & Error States
  loading: { [key: string]: boolean };
  error: { [key: string]: string | null };
}
```

### API Integration

The feature integrates with multiple microservices:

- **User Management Service**: Speaker CRUD, bucket transitions
- **Verification Service**: SER calculations, MT validation
- **RAG Integration Service**: Error pattern analysis
- **API Gateway**: Workflow orchestration, dashboard data

## Usage

### Basic Usage

```typescript
import { SpeakerManagementPage } from '@features/speaker-management';

// In your router
<Route path="/speakers" component={SpeakerManagementPage} />
```

### Using Individual Components

```typescript
import {
  SpeakerSearchAndSelection,
  SpeakerTable,
  SpeakerStatistics
} from '@features/speaker-management';

// Search and selection
<SpeakerSearchAndSelection
  onSpeakerSelect={handleSpeakerSelect}
  multiSelect={true}
  showQuickFilters={true}
/>

// Data table
<SpeakerTable
  onSpeakerView={handleView}
  onSpeakerEdit={handleEdit}
  selectable={true}
/>

// Statistics dashboard
<SpeakerStatistics compact={false} />
```

### Redux Integration

```typescript
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import {
  searchSpeakers,
  selectSpeakers,
  selectSpeakersLoading,
  setSearchFilters
} from '@features/speaker-management';

const MyComponent = () => {
  const dispatch = useAppDispatch();
  const speakers = useAppSelector(selectSpeakers);
  const loading = useAppSelector(selectSpeakersLoading);

  // Search speakers
  useEffect(() => {
    dispatch(searchSpeakers({ page: 1, page_size: 50 }));
  }, [dispatch]);

  // Apply filters
  const handleFilterChange = (filters) => {
    dispatch(setSearchFilters(filters));
    dispatch(searchSpeakers({ ...filters, page: 1 }));
  };
};
```

## Key Components

### SpeakerSearchAndSelection

Advanced search interface with real-time filtering and quick filter options.

**Props:**
- `onSpeakerSelect?: (speakerId: string) => void`
- `multiSelect?: boolean`
- `showViewModeToggle?: boolean`
- `showQuickFilters?: boolean`
- `compact?: boolean`

### SpeakerTable

High-performance data table with sorting, pagination, and inline actions.

**Props:**
- `onSpeakerView?: (speaker: Speaker) => void`
- `onSpeakerEdit?: (speaker: Speaker) => void`
- `onSpeakerAssess?: (speaker: Speaker) => void`
- `selectable?: boolean`
- `compact?: boolean`

### SpeakerStatistics

Comprehensive statistics dashboard with interactive visualizations.

**Props:**
- `compact?: boolean`
- `showRefresh?: boolean`

### SpeakerDetailsDialog

Modal dialog for viewing detailed speaker information with tabbed interface.

**Props:**
- `speaker: Speaker`
- `open: boolean`
- `onClose: () => void`
- `onEdit?: () => void`
- `onAssess?: () => void`

## Styling & Theming

The feature uses Material-UI components with consistent theming:

```typescript
// Bucket color mapping
const getBucketColor = (bucket: SpeakerBucket) => {
  switch (bucket) {
    case SpeakerBucket.HIGH_TOUCH: return 'error';
    case SpeakerBucket.MEDIUM_TOUCH: return 'warning';
    case SpeakerBucket.LOW_TOUCH: return 'info';
    case SpeakerBucket.NO_TOUCH: return 'success';
  }
};
```

## Performance Considerations

### Optimization Features

1. **Debounced Search**: 300ms debounce on search input
2. **Server-side Pagination**: Efficient data loading
3. **Memoized Selectors**: Optimized Redux selectors
4. **Virtual Scrolling**: For large datasets (via DataGrid)
5. **Lazy Loading**: Components loaded on demand

### Best Practices

- Use `React.memo` for expensive components
- Implement proper error boundaries
- Cache API responses where appropriate
- Use skeleton loading states
- Optimize bundle size with code splitting

## Testing

### Unit Tests

```typescript
// Example test structure
describe('SpeakerSearchAndSelection', () => {
  it('should filter speakers by search text', () => {
    // Test implementation
  });

  it('should handle quick filter selection', () => {
    // Test implementation
  });
});
```

### Integration Tests

```typescript
// Example integration test
describe('Speaker Management Workflow', () => {
  it('should complete speaker assessment workflow', () => {
    // Test full workflow
  });
});
```

## Accessibility

The feature implements comprehensive accessibility features:

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Support**: ARIA labels and descriptions
- **Focus Management**: Proper focus handling in dialogs
- **Color Contrast**: WCAG AA compliant colors
- **Semantic HTML**: Proper heading hierarchy and landmarks

## Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile Support**: iOS Safari 14+, Chrome Mobile 90+
- **Responsive Design**: Optimized for desktop, tablet, and mobile

## Future Enhancements

### Planned Features

1. **Advanced Analytics**: Machine learning insights
2. **Real-time Updates**: WebSocket integration
3. **Collaborative Features**: Multi-user workflows
4. **Mobile App**: React Native implementation
5. **Offline Support**: Progressive Web App features

### Performance Improvements

1. **GraphQL Integration**: More efficient data fetching
2. **Service Worker**: Background sync and caching
3. **Bundle Optimization**: Further code splitting
4. **CDN Integration**: Static asset optimization
