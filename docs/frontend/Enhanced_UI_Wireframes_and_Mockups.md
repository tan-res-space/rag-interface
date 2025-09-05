# Enhanced UI Wireframes and Mockups - Quality-Based Speaker Bucket Management

**Date:** December 19, 2024  
**Version:** 2.0  
**Design System:** Material-UI with Custom Quality-Based Bucket Theme

---

## Design System Overview

### Color Palette for Bucket Types
```
🎯 No Touch (Excellent):    #4CAF50 (Green)
🔧 Low Touch (Good):        #2196F3 (Blue)  
⚙️ Medium Touch (Fair):     #FF9800 (Orange)
🛠️ High Touch (Poor):       #F44336 (Red)

Supporting Colors:
- Success:     #4CAF50
- Warning:     #FF9800  
- Error:       #F44336
- Info:        #2196F3
- Background:  #F5F5F5
- Surface:     #FFFFFF
- Text:        #212121
```

### Typography Scale
```
H1: 32px - Page titles
H2: 24px - Section headers
H3: 20px - Subsection headers
H4: 18px - Component titles
Body1: 16px - Primary text
Body2: 14px - Secondary text
Caption: 12px - Helper text
```

---

## 1. Enhanced Error Reporting Interface

### 1.1 Step 4: Enhanced Metadata Input Form

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Add Context - Enhanced Metadata                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─ Required Information ────────────────────────────────────┐   │
│ │                                                           │   │
│ │ Speaker ID *                                              │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ demo-speaker-456                                    │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ │                                                           │   │
│ │ ┌─ Speaker Bucket Status ─────────────────────────────┐   │   │
│ │ │ ⚙️ Medium Touch                                      │   │   │
│ │ │ Current Speaker Level                                │   │   │
│ │ │ ASR draft is of medium quality, some corrections    │   │   │
│ │ │ are required                                         │   │   │
│ │ │                                                      │   │   │
│ │ │ Progress to Low Touch                    75%         │   │   │
│ │ │ ████████████████████████████████████░░░░░░░░░░░░     │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ │                                                           │   │
│ │ Client ID *                                               │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ client-medical-center-789                           │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ │                                                           │   │
│ │ Speaker Bucket Type *                                     │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ ⚙️ Medium Touch ▼                                   │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Audio Quality Assessment ───────────────────────────────┐   │
│ │                                                           │   │
│ │ Overall Audio Quality                                     │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ Good - Clear audio with minor imperfections ▼      │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ │                                                           │   │
│ │ Background Noise Level                                    │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ 🔉 Low Background Noise ▼                          │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ │                                                           │   │
│ │ Speaker Clarity                                           │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ Clear - Generally clear speech ▼                   │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Enhanced Context Information ───────────────────────────┐   │
│ │                                                           │   │
│ │ Number of Speakers *                                      │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ One ▼                                               │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ │                                                           │   │
│ │ Overlapping Speech *                                      │   │
│ │ ○ Yes    ● No                                            │   │
│ │                                                           │   │
│ │ Requires Specialized Knowledge *                          │   │
│ │ ● Yes    ○ No                                            │   │
│ │                                                           │   │
│ │ Additional Notes                                          │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ Complex medical terminology used throughout the     │   │   │
│ │ │ transcript. Patient discussion includes technical   │   │   │
│ │ │ terms that may require specialized knowledge.       │   │   │
│ │ │                                                     │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ │ 127 / 1000 characters                                    │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Priority Level ─────────────────────────────────────────┐   │
│ │ ○ Low Priority  ● Medium Priority  ○ High Priority      │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Cancel]                           [Back]    [Next] →      │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Bucket Type Dropdown Options

```
┌─────────────────────────────────────────────────────────────┐
│ Select Speaker Bucket Type                                  │
├─────────────────────────────────────────────────────────────┤
│ 🎯 No Touch                                                │
│    ASR draft is of very high quality and no corrections    │
│    are required                                             │
├─────────────────────────────────────────────────────────────┤
│ 🔧 Low Touch                                               │
│    ASR draft is of high quality and minimal corrections    │
│    are required by MTs                                      │
├─────────────────────────────────────────────────────────────┤
│ ⚙️ Medium Touch                                             │
│    ASR draft is of medium quality and some corrections     │
│    are required                                             │
├─────────────────────────────────────────────────────────────┤
│ 🛠️ High Touch                                               │
│    ASR draft is of low quality and significant corrections │
│    are required                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Speaker History Dashboard

### 2.1 Speaker Search and History View

```
┌─────────────────────────────────────────────────────────────────┐
│ Speaker History & Performance Tracking                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─ Speaker Search ─────────────────────────────────────────┐   │
│ │ 🔍 Search Speaker ID                                     │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ speaker-123                                         │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ │ Recent: speaker-456, speaker-789, speaker-321           │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Speaker Profile: speaker-123 ──────────────────────────┐   │
│ │                                                           │   │
│ │ Current Status: ⚙️ Medium Touch                          │   │
│ │ Assigned: Dec 1, 2024 by qa-user-456                    │   │
│ │ Reason: Quality improvement - error rate decreased       │   │
│ │                                                           │   │
│ │ ┌─ Performance Metrics ─────────────────────────────┐   │   │
│ │ │ Total Errors: 15    Rectified: 12    Rate: 80%   │   │   │
│ │ │ Quality Trend: ↗️ Improving                       │   │   │
│ │ │ Time in Bucket: 18 days                          │   │   │
│ │ │ Last Assessment: Dec 15, 2024                    │   │   │
│ │ └───────────────────────────────────────────────────┘   │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Bucket History Timeline ────────────────────────────────┐   │
│ │                                                           │   │
│ │ Dec 1, 2024  🛠️ → ⚙️  High Touch → Medium Touch         │   │
│ │              Quality improvement observed                 │   │
│ │                                                           │   │
│ │ Nov 1, 2024  ⚙️ → 🛠️  Medium Touch → High Touch         │   │
│ │              Multiple errors reported                     │   │
│ │                                                           │   │
│ │ Oct 15, 2024 Initial   ⚙️ Medium Touch                   │   │
│ │              Initial assessment                           │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Error History (Last 30 Days) ───────────────────────────┐   │
│ │                                                           │   │
│ │ Dec 15  Medical Terminology  "hypertension" → "high BP"  │   │
│ │         Status: ✅ Rectified                             │   │
│ │                                                           │   │
│ │ Dec 10  Pronunciation       "showed" → "revealed"        │   │
│ │         Status: ⏳ Pending Verification                  │   │
│ │                                                           │   │
│ │ Dec 5   Grammar             "was" → "were"               │   │
│ │         Status: ✅ Rectified                             │   │
│ │                                                           │   │
│ │ [View All Errors] [Export Report]                        │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Performance Trend Charts

```
┌─────────────────────────────────────────────────────────────────┐
│ Speaker Performance Trends - speaker-123                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─ Error Count Over Time ──────────────────────────────────┐   │
│ │     Errors                                                │   │
│ │ 10  │                                                     │   │
│ │  8  │ ●                                                   │   │
│ │  6  │   ●                                                 │   │
│ │  4  │     ●                                               │   │
│ │  2  │       ●─●                                           │   │
│ │  0  └─────────────────────────────────────────────────── │   │
│ │     Oct   Nov   Dec   Jan   Feb   Mar                    │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Bucket Progression Timeline ────────────────────────────┐   │
│ │                                                           │   │
│ │ 🛠️ High Touch    ████████████████████████████████████   │   │
│ │ ⚙️ Medium Touch  ████████████████████████████████████   │   │
│ │ 🔧 Low Touch     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │   │
│ │ 🎯 No Touch      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │   │
│ │                                                           │   │
│ │ Oct ──── Nov ──── Dec ──── Jan ──── Feb ──── Mar        │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Rectification Rate ─────────────────────────────────────┐   │
│ │ 100% │                                                   │   │
│ │  80% │         ●─●─●                                     │   │
│ │  60% │       ●                                           │   │
│ │  40% │     ●                                             │   │
│ │  20% │   ●                                               │   │
│ │   0% └─────────────────────────────────────────────────── │   │
│ │      Oct   Nov   Dec   Jan   Feb   Mar                  │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Verification Workflow Interface

### 3.1 Job Retrieval and Selection

```
┌─────────────────────────────────────────────────────────────────┐
│ Verification Workflow - Pull Jobs for Verification             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─ Job Retrieval Criteria ─────────────────────────────────┐   │
│ │                                                           │   │
│ │ Speaker ID: speaker-123                                   │   │
│ │                                                           │   │
│ │ Date Range:                                               │   │
│ │ From: [Dec 1, 2024 ▼]  To: [Dec 19, 2024 ▼]            │   │
│ │                                                           │   │
│ │ Error Types to Verify:                                    │   │
│ │ ☑️ Medical Terminology  ☑️ Pronunciation                 │   │
│ │ ☐ Grammar              ☐ Punctuation                    │   │
│ │                                                           │   │
│ │ Max Jobs: [10 ▼]                                         │   │
│ │                                                           │   │
│ │ [Pull Jobs from InstaNote DB]                            │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Retrieved Jobs (5 found) ───────────────────────────────┐   │
│ │                                                           │   │
│ │ ☑️ Job: instanote-job-456  Date: Dec 15, 2024           │   │
│ │    Corrections: Medical Terminology (1), Pronunciation   │   │
│ │    Status: Pending Verification                          │   │
│ │                                                           │   │
│ │ ☑️ Job: instanote-job-457  Date: Dec 14, 2024           │   │
│ │    Corrections: Medical Terminology (2)                  │   │
│ │    Status: Pending Verification                          │   │
│ │                                                           │   │
│ │ ☐ Job: instanote-job-458  Date: Dec 13, 2024           │   │
│ │    Corrections: Grammar (1), Punctuation (1)            │   │
│ │    Status: Pending Verification                          │   │
│ │                                                           │   │
│ │ [Select All] [Verify Selected Jobs]                      │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Side-by-Side Verification Interface

```
┌─────────────────────────────────────────────────────────────────┐
│ Verification: instanote-job-456 - speaker-123                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─ Original Draft ─────────────┐ ┌─ RAG-Corrected Draft ─────┐ │
│ │                              │ │                            │ │
│ │ The patient has severe       │ │ The patient has severe     │ │
│ │ hypertension and diabetes.   │ │ high blood pressure and    │ │
│ │ The doctor prescribed        │ │ diabetes. The doctor       │ │
│ │ medication for the condition.│ │ prescribed medication for  │ │
│ │ During the examination, the  │ │ the condition. During the  │ │
│ │ patient complained of chest  │ │ examination, the patient   │ │
│ │ pain and shortness of breath.│ │ complained of chest pain   │ │
│ │                              │ │ and shortness of breath.   │ │
│ └──────────────────────────────┘ └────────────────────────────┘ │
│                                                                 │
│ ┌─ Corrections Applied ────────────────────────────────────┐   │
│ │                                                           │   │
│ │ 1. Medical Terminology                                    │   │
│ │    "hypertension" → "high blood pressure"                │   │
│ │    Confidence: 95%                                        │   │
│ │    ○ Rectified  ○ Not Rectified  ○ Partially Rectified  │   │
│ │                                                           │   │
│ │ 2. Pronunciation                                          │   │
│ │    "showed" → "revealed" (not found in this draft)       │   │
│ │    ○ Not Applicable                                       │   │
│ │                                                           │   │
│ │ QA Comments:                                              │   │
│ │ ┌─────────────────────────────────────────────────────┐   │   │
│ │ │ Medical terminology correction applied correctly.   │   │   │
│ │ │ Patient-friendly language used appropriately.      │   │   │
│ │ └─────────────────────────────────────────────────────┘   │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Previous Job]  [Mark as Verified]  [Next Job]            │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Enhanced Dashboard Overview

### 4.1 Speaker Bucket Distribution Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│ Speaker Bucket Management Dashboard                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─ Bucket Distribution Overview ───────────────────────────┐   │
│ │                                                           │   │
│ │ Total Speakers: 1,250                                     │   │
│ │                                                           │   │
│ │     ┌─────────────────────────────────────────────┐       │   │
│ │     │           Bucket Distribution               │       │   │
│ │     │                                             │       │   │
│ │     │        🎯 No Touch                         │       │   │
│ │     │         125 (10%)                          │       │   │
│ │     │                                             │       │   │
│ │     │    🔧 Low Touch                            │       │   │
│ │     │     375 (30%)                              │       │   │
│ │     │                                             │       │   │
│ │     │ ⚙️ Medium Touch                            │       │   │
│ │     │  500 (40%)                                 │       │   │
│ │     │                                             │       │   │
│ │     │🛠️ High Touch                               │       │   │
│ │     │ 250 (20%)                                  │       │   │
│ │     └─────────────────────────────────────────────┘       │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Quality Metrics (Last 30 Days) ─────────────────────────┐   │
│ │                                                           │   │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │   │
│ │ │ 1,847       │ │ 82%         │ │ 3.8 days    │         │   │
│ │ │ Errors      │ │ Rectified   │ │ Avg Time    │         │   │
│ │ │ Reported    │ │ Rate        │ │ to Fix      │         │   │
│ │ └─────────────┘ └─────────────┘ └─────────────┘         │   │
│ │                                                           │   │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │   │
│ │ │ 156         │ │ 86%         │ │ 127 hrs     │         │   │
│ │ │ Bucket      │ │ Improvement │ │ Time        │         │   │
│ │ │ Transitions │ │ Rate        │ │ Saved       │         │   │
│ │ └─────────────┘ └─────────────┘ └─────────────┘         │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Resource Allocation ────────────────────────────────────┐   │
│ │                                                           │   │
│ │ MT Workload Distribution:                                 │   │
│ │                                                           │   │
│ │ 🎯 No Touch:     ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  5%  │   │
│ │ 🔧 Low Touch:    ████████████░░░░░░░░░░░░░░░░░░░░░░░░ 25% │   │
│ │ ⚙️ Medium Touch: ████████████████████████░░░░░░░░░░░░ 45% │   │
│ │ 🛠️ High Touch:   ████████████░░░░░░░░░░░░░░░░░░░░░░░░ 25% │   │
│ │                                                           │   │
│ │ Efficiency Gain: +15% compared to previous month         │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Mobile-Responsive Design Considerations

### 5.1 Mobile Error Reporting Interface

```
┌─────────────────────────┐
│ ☰ RAG Interface    👤  │
├─────────────────────────┤
│ Step 4: Add Context     │
│                         │
│ Required Information    │
│ ┌─────────────────────┐ │
│ │ Speaker ID *        │ │
│ │ demo-speaker-456    │ │
│ └─────────────────────┘ │
│                         │
│ ┌─ Bucket Status ───┐   │
│ │ ⚙️ Medium Touch   │   │
│ │ Progress: 75%     │   │
│ │ ████████████░░░░  │   │
│ └───────────────────┘   │
│                         │
│ ┌─────────────────────┐ │
│ │ Client ID *         │ │
│ │ client-789          │ │
│ └─────────────────────┘ │
│                         │
│ Audio Quality           │
│ ┌─────────────────────┐ │
│ │ Good ▼              │ │
│ └─────────────────────┘ │
│                         │
│ Enhanced Context        │
│ Speakers: One ▼         │
│ Overlapping: ○Yes ●No   │
│ Specialized: ●Yes ○No   │
│                         │
│ ┌─────────────────────┐ │
│ │ Additional Notes    │ │
│ │ Complex medical...  │ │
│ └─────────────────────┘ │
│                         │
│ ┌─────────────────────┐ │
│ │ [Back]    [Next] → │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

### 5.2 Touch-Optimized Selection Interface

```
┌─────────────────────────┐
│ Select Error Text       │
├─────────────────────────┤
│                         │
│ The patient has severe  │
│ ████████████████████    │
│ hypertension and        │
│ ████████████            │
│ diabetes. The doctor... │
│                         │
│ ┌─ Selection Info ───┐  │
│ │ 📍 1 selection     │  │
│ │ "hypertension"     │  │
│ │ [Clear] [Edit]     │  │
│ └────────────────────┘  │
│                         │
│ Touch and drag to       │
│ select error text       │
│                         │
│ ┌─────────────────────┐ │
│ │ [Cancel] [Next] →  │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

---

## 6. Accessibility Features

### 6.1 Screen Reader Support
- All form fields have proper labels and descriptions
- Bucket status information announced clearly
- Progress indicators have text alternatives
- Error messages are announced immediately

### 6.2 Keyboard Navigation
- Tab order follows logical flow through form
- All interactive elements accessible via keyboard
- Dropdown menus navigable with arrow keys
- Form submission possible without mouse

### 6.3 High Contrast Mode
- Alternative color scheme for bucket types
- Increased contrast ratios for all text
- Clear visual focus indicators
- Pattern-based differentiation for color-blind users
