#!/usr/bin/env python3
"""
Quick development script to reset the research assistant system.
This is a simplified version of admin_clear_all_data.py for development use.

WARNING: This will delete ALL data without confirmation!
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db_utils import delete_all_data
from core.vector_utils import delete_all_vector_store

def main():
    print("🔄 Development Reset: Clearing all data...")
    
    # Clear SQL database
    sql_ok = delete_all_data()
    
    # Clear vector store  
    vector_ok = delete_all_vector_store()
    
    if sql_ok and vector_ok:
        print("✅ All data cleared successfully!")
    elif sql_ok:
        print("⚠️  SQL cleared, vector store failed")
    elif vector_ok:
        print("⚠️  Vector store cleared, SQL failed") 
    else:
        print("❌ Failed to clear data")
        sys.exit(1)

if __name__ == "__main__":
    main()
