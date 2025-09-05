# Quality-Based Speaker Bucket Management System Documentation

**Date:** December 19, 2024
**Status:** Updated for Quality-Based Classification System
**Technology Stack:** Python + FastAPI Backend, React + TypeScript Frontend

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Bucket Progression Algorithm](#2-bucket-progression-algorithm)
3. [Backend Implementation](#3-backend-implementation)
4. [Frontend Implementation](#4-frontend-implementation)
5. [API Endpoints](#5-api-endpoints)
6. [User Experience](#6-user-experience)
7. [Business Rules](#7-business-rules)
8. [Analytics and Reporting](#8-analytics-and-reporting)

---

## 1. System Overview

### 1.1 Purpose
The Quality-Based Speaker Bucket Management System categorizes speakers based on ASR draft quality and correction requirements, enabling targeted quality improvement and efficient resource allocation for Medical Transcriptionists and QA personnel.

### 1.2 Quality-Based Bucket Classification

| Bucket Type | Icon | Description | MT Effort Required | Quality Level |
|-------------|------|-------------|-------------------|---------------|
| 🎯 **No Touch** | no_touch | ASR draft is of very high quality and no corrections are required | None | Excellent |
| 🔧 **Low Touch** | low_touch | ASR draft is of high quality and minimal corrections are required by MTs | Minimal | Good |
| ⚙️ **Medium Touch** | medium_touch | ASR draft is of medium quality and some corrections are required | Moderate | Fair |
| 🛠️ **High Touch** | high_touch | ASR draft is of low quality and significant corrections are required | Extensive | Poor |

### 1.3 Key Benefits
- **Quality-Based Classification**: Speakers categorized by ASR output quality level
- **Resource Optimization**: Efficient allocation of MT resources based on quality levels
- **Performance Tracking**: Monitor ASR performance improvement over time
- **Error Rectification**: Systematic correction of errors from next draft onwards
- **Verification Workflow**: QA can verify error rectification in subsequent drafts

---

## 2. Bucket Progression Algorithm

### 2.1 Evaluation Criteria

#### Promotion Requirements
- **Minimum Reports**: 10 reports in evaluation window
- **Error Rate**: Must meet target bucket's error rate threshold
- **Correction Accuracy**: Must meet target bucket's accuracy threshold
- **Consistency Score**: ≥ 70% consistency in performance
- **Improvement Trend**: ≥ 10% improvement over time
- **Time in Bucket**: Minimum 7 days in current bucket

#### Demotion Triggers
- **Performance Decline**: Error rate exceeds current bucket threshold by 50%
- **Accuracy Drop**: Correction accuracy falls below current bucket threshold by 20%
- **Consistency Issues**: Consistency score below 70%
- **Minimum Reports**: 5 reports showing declining performance

### 2.2 Confidence Scoring
The algorithm calculates a confidence score (0-1) for each recommendation:

```python
promotion_score = (
    error_rate_score * 0.4 +      # 40% weight
    accuracy_score * 0.3 +        # 30% weight  
    consistency_score * 0.15 +    # 15% weight
    improvement_score * 0.15      # 15% weight
)
```

### 2.3 Safeguards
- **Cooldown Period**: 14 days between bucket changes
- **Change Limit**: Maximum 2 bucket changes per month
- **Minimum Activity**: Recent activity required for evaluation
- **Manual Override**: Admin can force evaluation or block changes

---

## 3. Backend Implementation

### 3.1 Domain Models

#### SpeakerProfile Entity
```python
@dataclass
class SpeakerProfile:
    speaker_id: str
    current_bucket: BucketType
    created_at: datetime
    updated_at: datetime
    total_reports: int
    total_errors_found: int
    total_corrections_made: int
    average_error_rate: float
    average_correction_accuracy: float
    last_report_date: Optional[datetime]
    bucket_change_count: int
    days_in_current_bucket: int
    metadata: Dict[str, Any]
```

#### BucketChangeLog Entity
```python
@dataclass
class BucketChangeLog:
    change_id: str
    speaker_id: str
    old_bucket: BucketType
    new_bucket: BucketType
    change_reason: str
    changed_at: datetime
    metrics_at_change: SpeakerMetrics
    metadata: Dict[str, Any]
```

### 3.2 Core Services

#### BucketProgressionService
- **evaluate_speaker_progression()**: Main evaluation logic
- **_calculate_promotion_score()**: Promotion confidence calculation
- **_calculate_demotion_score()**: Demotion confidence calculation
- **_meets_evaluation_requirements()**: Validation checks

#### SpeakerMetrics Calculator
- **calculate_from_reports()**: Metrics computation from error reports
- **_calculate_error_rate()**: Text-based error rate calculation
- **_calculate_correction_accuracy()**: Quality assessment
- **_calculate_consistency_score()**: Performance variance analysis
- **_calculate_improvement_trend()**: Temporal improvement tracking

### 3.3 Use Cases

#### EvaluateBucketProgressionUseCase
- Triggered on each error report submission
- Evaluates speaker against progression criteria
- Applies bucket changes when criteria are met
- Creates audit trail entries

#### BatchEvaluateBucketProgressionUseCase
- Processes multiple speakers in batch
- Used for scheduled evaluations
- Provides summary statistics

---

## 4. Frontend Implementation

### 4.1 Core Components

#### SpeakerBucketStatus
- Displays current bucket level in error reporting form
- Shows progress to next level
- Real-time performance metrics
- Compact and full display modes

#### BucketProgressionNotification
- Toast notifications for bucket changes
- Promotion/demotion animations
- Detailed change information
- Auto-hide with manual dismiss

#### SpeakerProfileDashboard
- Comprehensive speaker analytics
- Bucket progression history
- Performance trends
- Manual evaluation triggers

#### BucketProgressionAnalytics
- Global bucket distribution charts
- Progression trend analysis
- Performance comparisons
- Administrative insights

### 4.2 State Management

#### useBucketProgressionNotifications Hook
```typescript
const {
  notifications,
  addNotification,
  removeNotification,
  closeNotification,
  clearAllNotifications
} = useBucketProgressionNotifications();
```

#### React Query Integration
- Cached speaker profile data
- Real-time bucket statistics
- Optimistic updates
- Background refresh

### 4.3 User Experience Flow

1. **Error Report Submission**
   - Speaker bucket status displayed in form
   - Automatic evaluation triggered on submit
   - Bucket change notification if applicable

2. **Bucket Change Notification**
   - Immediate toast notification
   - Visual progression indicators
   - Congratulatory messaging for promotions

3. **Profile Dashboard**
   - Current level and progress
   - Historical progression
   - Performance analytics
   - Next level requirements

---

## 5. API Endpoints

### 5.1 Speaker Profile Management

#### GET /api/v1/speakers/{speaker_id}/profile
Returns complete speaker profile with current bucket and statistics.

#### GET /api/v1/speakers/{speaker_id}/bucket-history
Returns bucket change history with pagination.

#### POST /api/v1/speakers/{speaker_id}/evaluate-progression
Triggers manual bucket progression evaluation.

### 5.2 Analytics and Statistics

#### GET /api/v1/speakers/bucket-statistics
Returns global bucket distribution and change statistics.

#### POST /api/v1/speakers/batch-evaluate
Triggers batch evaluation for multiple speakers.

#### GET /api/v1/speakers/bucket-types
Returns bucket type definitions and progression order.

### 5.3 Integration Points

#### POST /api/v1/errors (Enhanced)
Error report submission now includes:
- Automatic bucket progression evaluation
- Bucket change notifications in response
- Speaker profile updates

---

## 6. User Experience

### 6.1 Speaker Journey

#### New Speaker (Beginner)
1. **Onboarding**: Starts at Beginner level
2. **Learning**: Bucket status visible during error reporting
3. **Progress**: Real-time feedback on performance
4. **Advancement**: Automatic promotion when criteria met

#### Experienced Speaker (Advanced/Expert)
1. **Maintenance**: Consistent performance tracking
2. **Recognition**: Expert level achievement celebration
3. **Mentoring**: Can view progression analytics
4. **Quality Assurance**: Demotion if performance declines

### 6.2 Notification System

#### Promotion Notifications
- 🎉 Celebration animations
- Clear progression messaging
- Performance highlights
- Next level preview

#### Demotion Notifications
- 📊 Constructive feedback
- Performance improvement suggestions
- Support resources
- Recovery guidance

### 6.3 Analytics Dashboard

#### Individual Analytics
- Personal progression timeline
- Performance trend charts
- Bucket change history
- Goal tracking

#### Administrative Analytics
- Global bucket distribution
- Progression rate analysis
- Quality trend monitoring
- Speaker development insights

---

## 7. Business Rules

### 7.1 Evaluation Criteria

#### Minimum Requirements
- **Reports**: 10 for promotion, 5 for demotion
- **Time**: 7 days minimum in current bucket
- **Activity**: Recent reports within 30 days
- **Cooldown**: 14 days between changes

#### Performance Thresholds
- **Error Rate**: Bucket-specific maximum rates
- **Accuracy**: Bucket-specific minimum accuracy
- **Consistency**: 70% minimum consistency score
- **Improvement**: 10% minimum improvement trend

### 7.2 Safeguards

#### Change Limits
- Maximum 2 bucket changes per month
- Cooldown period enforcement
- Manual override capabilities
- Emergency stop mechanisms

#### Quality Assurance
- Audit trail for all changes
- Performance metric validation
- Anomaly detection
- Manual review triggers

---

## 8. Analytics and Reporting

### 8.1 Key Metrics

#### Speaker Metrics
- Current bucket distribution
- Progression rates by level
- Average time in each bucket
- Success/failure rates

#### System Metrics
- Total bucket changes
- Evaluation frequency
- Algorithm performance
- User engagement

### 8.2 Reporting Capabilities

#### Real-time Dashboards
- Live bucket distribution
- Recent progressions
- Performance trends
- Alert notifications

#### Historical Analysis
- Progression timeline analysis
- Seasonal trend identification
- Cohort performance tracking
- ROI measurement

### 8.3 Data Export

#### CSV/Excel Reports
- Speaker progression history
- Performance metrics
- Bucket statistics
- Custom date ranges

#### API Data Access
- Programmatic data retrieval
- Integration with BI tools
- Custom analytics development
- Third-party reporting

---

## Implementation Status

✅ **Backend Implementation**: Complete  
✅ **Frontend Components**: Complete  
✅ **API Integration**: Complete  
✅ **Notification System**: Complete  
✅ **Analytics Dashboard**: Complete  
✅ **Documentation**: Complete  

**Next Steps:**
- Production deployment
- Performance monitoring
- User feedback collection
- Algorithm refinement based on real-world data
