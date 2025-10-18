# Database Schema Redesign

## New Hierarchy

```
Course (Online Sharia)
├── Subject 1 (Fiqh)
│   ├── Lesson 1 (Class 1)
│   ├── Lesson 2 (Class 2)
│   ├── Lesson 3 (Class 3)
│   └── Lesson 4 (Class 4)
├── Subject 2 (Quran)
│   ├── Lesson 1 (Class 1)
│   ├── Lesson 2 (Class 2)
│   └── Lesson 3 (Class 3)
├── Subject 3 (Nahv)
│   ├── Lesson 1 (Class 1)
│   └── Lesson 2 (Class 2)
├── Subject 4 (Sarf)
│   ├── Lesson 1 (Class 1)
│   └── Lesson 2 (Class 2)
└── Subject 5 (Hadees)
    ├── Lesson 1 (Class 1)
    └── Lesson 2 (Class 2)
```

## Day-Based Schedule

```
Day 1
├── Nahv Class 1 (Lesson 1 of Nahv)
└── Quran Class 1 (Lesson 1 of Quran)

Day 2
├── Fiqh Class 2 (Lesson 2 of Fiqh)
└── Hadees Class 1 (Lesson 1 of Hadees)
```

## Model Changes

### Current Structure
```
Course
  └── Class (year-based: Class 1, Class 2, etc.)
      └── Subject
          └── Session (dated lessons)
```

### New Structure
```
Course (Online Sharia)
  └── Subject (Fiqh, Quran, Nahv, Sarf, Hadees)
      └── Lesson (Class 1, Class 2, Class 3, Class 4)
          └── ClassSession (day-based scheduling with content)
```

## Table Changes

### 1. Course Table (NO CHANGE)
```
courses
├── id (PK)
├── title
├── description
├── teacher_id (FK users)
└── created_at
```

### 2. Subject Table (MODIFIED)
Move from class-level to course-level
```
subjects
├── id (PK)
├── course_id (FK courses) ← CHANGED from class_id
├── name (Fiqh, Quran, Nahv, etc.)
├── description
├── instructor_id (FK users)
├── order_in_course ← RENAMED from order_in_class
└── created_at
```

### 3. Lesson Table (NEW)
Represents a "class" in a subject (Class 1, Class 2, etc.)
```
lessons
├── id (PK)
├── subject_id (FK subjects) ← NEW
├── title (Class 1, Class 2, etc.)
├── description
├── order_in_subject
└── created_at
```

### 4. ClassSession Table (MODIFIED)
Represents day-based scheduling
```
class_sessions
├── id (PK)
├── lesson_id (FK lessons) ← CHANGED from subject_id
├── session_date
├── start_time
├── end_time
├── is_completed
└── created_at
```

### 5. Class Table (DEPRECATED)
Can be removed or kept for backwards compatibility as a view

## Data Relationships

### Course to Subject
- 1 Course has many Subjects
- Example: Course "Online Sharia" has Subjects: Fiqh, Quran, Nahv, Sarf, Hadees

### Subject to Lesson
- 1 Subject has many Lessons
- Example: Subject "Fiqh" has Lessons: Class 1, Class 2, Class 3, Class 4

### Lesson to ClassSession
- 1 Lesson has many ClassSessions (scheduled on different days)
- Example: Fiqh Class 1 is scheduled on:
  - Day 1 from 2:00 PM to 3:00 PM
  - Day 8 from 2:00 PM to 3:00 PM
  - Day 15 from 2:00 PM to 3:00 PM

## Frontend Display

### View 1: Course Overview
```
Online Sharia Course
├── Subjects (5)
│   ├── Fiqh (4 lessons)
│   ├── Quran (3 lessons)
│   ├── Nahv (2 lessons)
│   ├── Sarf (2 lessons)
│   └── Hadees (2 lessons)
└── Day-based Schedule
    ├── Day 1: Nahv Class 1, Quran Class 1
    ├── Day 2: Fiqh Class 2, Hadees Class 1
    └── ...
```

### View 2: Subject Details
```
Fiqh Subject
├── Class 1 (Lesson 1)
│   ├── Scheduled sessions:
│   │   ├── Day 1 (2:00-3:00 PM)
│   │   └── Day 8 (2:00-3:00 PM)
│   ├── Content/Videos
│   ├── Quiz
│   └── Progress
├── Class 2 (Lesson 2)
│   └── ...
└── ...
```

### View 3: Day-Based Schedule
```
Week 1
├── Day 1 (Oct 18)
│   ├── Nahv Class 1 (2:00-3:00 PM)
│   └── Quran Class 1 (3:00-4:00 PM)
├── Day 2 (Oct 19)
│   ├── Fiqh Class 2 (2:00-3:00 PM)
│   └── Hadees Class 1 (3:00-4:00 PM)
└── ...
```

## Migration Steps

1. ✅ Create new `Lesson` table
2. ✅ Migrate `Subject` from class-level to course-level
3. ✅ Migrate `ClassSession` to reference `Lesson` instead of `Subject`
4. ✅ Update enums and schemas
5. ✅ Create sample data
6. ✅ Update frontend components
