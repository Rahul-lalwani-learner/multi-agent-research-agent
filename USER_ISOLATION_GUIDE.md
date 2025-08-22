# User Isolation Implementation Guide

## Overview

Your research agent project has been updated to support **multi-user isolation**. Each user now has their own isolated data in both the PostgreSQL database and ChromaDB vector store, while maintaining all existing functionality.

## What Changed

### 1. Database Schema Updates
- **Added `user_id` field** to all tables:
  - `papers.user_id` - Associates papers with specific users
  - `chunks.user_id` - Associates text chunks with users  
  - `cluster_results.user_id` - Associates cluster analysis with users
  - `hypotheses.user_id` - Associates generated hypotheses with users
  - `experiment_plans.user_id` - Associates experiment plans with users

### 2. Vector Store Isolation
- **User-specific ChromaDB collections**: Each user gets their own collection named `research_papers_user_{hash}`
- **Automatic filtering**: All vector searches are automatically filtered by user
- **Metadata tagging**: All vector documents include `user_id` in metadata

### 3. User Management System
- **Automatic user ID generation**: Each session gets a unique UUID
- **Username support**: Users can set friendly usernames
- **Session persistence**: User context persists across page refreshes
- **Data statistics**: Users can see their own data counts

## Key Components

### User Manager (`core/user_manager.py`)
- Manages user sessions and provides user isolation
- Generates unique user IDs and collection names
- Handles username management

### Updated Database Models (`core/models.py`)
- All models now include `user_id` field
- Proper indexing for user-based queries
- Maintains referential integrity

### Updated Vector Store (`core/vector_store.py`)
- User-specific collections
- Automatic user filtering in all operations
- Support for multiple concurrent user sessions

### Migration Script (`migrate_user_isolation.py`)
- Safely adds `user_id` columns to existing database
- Assigns existing data to a default user
- Creates proper indexes

## How to Use

### 1. Run Migration (Important!)
Before using the updated system, run the migration script:

```bash
python migrate_user_isolation.py
```

This will:
- Add `user_id` columns to existing tables
- Assign existing data to a default user
- Create necessary indexes

### 2. User Experience

#### New User Interface Elements:
- **User info display** in sidebar showing current user ID/username
- **Username setting** - users can set friendly names
- **Data statistics** - shows user's paper count, chunks, etc.
- **User-specific data clearing** - "Clear My Data" vs "Remove ALL Data"

#### Automatic User Isolation:
- Each browser session gets a unique user ID
- All operations (adding papers, querying, agent workflow) are isolated per user
- No manual user management required

### 3. Developer Usage

#### Getting Current User:
```python
from core.user_manager import user_manager

# Get current user ID
user_id = user_manager.get_current_user_id()

# Get username (if set)
username = user_manager.get_current_username()
```

#### Database Operations:
```python
from core.db_utils import get_user_papers, get_user_stats

# Get papers for current user
papers = get_user_papers(user_id)

# Get user statistics
stats = get_user_stats(user_id)
```

#### Vector Store Operations:
```python
from core.vector_store import vector_store_manager

# All methods now support user_id parameter
retriever = vector_store_manager.get_retriever(user_id=user_id)
results = vector_store_manager.similarity_search("query", user_id=user_id)

# If user_id is None, it uses current user from session
results = vector_store_manager.similarity_search("query")  # Uses current user
```

## Data Isolation Guarantees

### Database Level:
- All queries filtered by `user_id`
- Foreign key relationships maintained within user scope
- Indexes optimized for user-based access patterns

### Vector Store Level:
- Separate ChromaDB collections per user
- Metadata-based filtering as backup
- User-specific document IDs

### Application Level:
- Session-based user context
- Automatic user injection in all operations
- No cross-user data leakage

## Testing User Isolation

### Test with Multiple Browser Sessions:
1. Open app in Chrome: User A will get unique ID
2. Open app in Firefox: User B will get different unique ID  
3. Add papers in each browser - they won't see each other's data
4. Query papers - each user only sees their own results

### Test Data Clearing:
1. Add some papers as User A
2. Click "Clear My Data" - only User A's data is removed
3. User B's data remains intact

## Migration Notes

### Existing Data:
- All existing data will be assigned to a single default user ID
- This preserves existing functionality for current users
- New users will start with empty collections

### Backward Compatibility:
- All existing API endpoints continue to work
- No breaking changes to existing functionality
- Automatic user context injection

## Performance Considerations

### Database:
- Added indexes on `user_id` fields for optimal query performance
- Composite indexes for common query patterns
- No significant performance impact

### Vector Store:
- Separate collections scale better than single large collection
- User-specific filtering reduces search space
- Lazy collection creation (only created when needed)

## Security Notes

### User Isolation:
- Strong isolation between users
- No accidental cross-user access
- Session-based security model

### Data Privacy:
- Each user's data is completely isolated
- No shared state between users
- Clear data ownership model

## Troubleshooting

### Migration Issues:
- Ensure database connection is working
- Check for sufficient permissions to ALTER tables
- Review migration logs for specific errors

### Vector Store Issues:
- ChromaDB collections are created lazily
- Check ChromaDB persistence directory permissions
- Verify embedding service connectivity

### User Session Issues:
- User ID persists in Streamlit session state
- Clear browser cache to reset user session
- Username setting is optional

## Future Enhancements

Potential future improvements:
- User authentication system
- User registration/login
- Data sharing between users
- Admin user management
- User data export/import
- Team collaboration features

## Summary

The user isolation system provides:
✅ **Complete data separation** between users  
✅ **Backward compatibility** with existing functionality  
✅ **Automatic user management** (no manual setup required)  
✅ **Performance optimization** for multi-user scenarios  
✅ **Easy testing and development** workflow  

Each user now has their own private research workspace while maintaining all the powerful features of your multi-agent research assistant!
