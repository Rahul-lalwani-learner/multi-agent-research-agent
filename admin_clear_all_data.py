#!/usr/bin/env python3
"""
Administrative script to completely clear all data from the research assistant system.
This script will delete ALL user data from both SQL database and ChromaDB vector store.

WARNING: This action is irreversible and will delete ALL users' data!

Usage:
    python admin_clear_all_data.py [--confirm]
    
Options:
    --confirm    Skip confirmation prompt and proceed with deletion
    --help       Show this help message
"""
import sys
import os
import argparse

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import logger
from core.db_utils import delete_all_data
from core.vector_utils import delete_all_vector_store


def confirm_deletion():
    """Ask user for confirmation before proceeding with deletion."""
    print("\n⚠️  WARNING: DESTRUCTIVE OPERATION ⚠️")
    print("="*50)
    print("This script will permanently delete:")
    print("• ALL papers from ALL users")
    print("• ALL text chunks from ALL users") 
    print("• ALL vector embeddings from ALL users")
    print("• ALL cluster results from ALL users")
    print("• ALL hypotheses from ALL users")
    print("• ALL experiment plans from ALL users")
    print("="*50)
    print("This action is IRREVERSIBLE!")
    print()
    
    response = input("Type 'DELETE ALL DATA' to confirm (or anything else to cancel): ")
    return response.strip() == "DELETE ALL DATA"


def clear_sql_database():
    """Clear all data from SQL database."""
    print("🗑️  Clearing SQL database...")
    try:
        success = delete_all_data()
        if success:
            print("✅ SQL database cleared successfully")
            return True
        else:
            print("❌ Failed to clear SQL database")
            return False
    except Exception as e:
        print(f"❌ Error clearing SQL database: {e}")
        logger.error(f"Admin clear SQL error: {e}")
        return False


def clear_vector_store():
    """Clear all data from ChromaDB vector store."""
    print("🗑️  Clearing ChromaDB vector store...")
    try:
        success = delete_all_vector_store()
        if success:
            print("✅ Vector store cleared successfully")
            return True
        else:
            print("❌ Failed to clear vector store")
            return False
    except Exception as e:
        print(f"❌ Error clearing vector store: {e}")
        logger.error(f"Admin clear vector error: {e}")
        return False


def main():
    """Main function to handle command line arguments and execute clearing."""
    parser = argparse.ArgumentParser(
        description="Administrative script to clear all data from the research assistant system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt and proceed with deletion"
    )
    
    args = parser.parse_args()
    
    print("🔬 Research Assistant - Administrative Data Clearing Tool")
    print("="*60)
    
    # Check if confirmation is needed
    if not args.confirm:
        if not confirm_deletion():
            print("\n❌ Operation cancelled by user")
            sys.exit(0)
    else:
        print("⚠️  Running with --confirm flag, skipping user confirmation")
    
    print("\n🚀 Starting data clearing process...")
    
    # Clear SQL database
    sql_success = clear_sql_database()
    
    # Clear vector store
    vector_success = clear_vector_store()
    
    # Report results
    print("\n" + "="*60)
    print("📊 DATA CLEARING RESULTS:")
    print("="*60)
    
    if sql_success and vector_success:
        print("✅ SUCCESS: All data cleared from both SQL database and vector store")
        print("🎉 The research assistant system has been completely reset")
        logger.info("Admin operation: All data cleared successfully")
        sys.exit(0)
    elif sql_success and not vector_success:
        print("⚠️  PARTIAL SUCCESS: SQL database cleared, but vector store clearing failed")
        print("🔧 You may need to manually clear the ChromaDB data")
        logger.warning("Admin operation: SQL cleared but vector store failed")
        sys.exit(1)
    elif not sql_success and vector_success:
        print("⚠️  PARTIAL SUCCESS: Vector store cleared, but SQL database clearing failed")
        print("🔧 You may need to manually clear the SQL database")
        logger.warning("Admin operation: Vector store cleared but SQL failed")
        sys.exit(1)
    else:
        print("❌ FAILURE: Both SQL database and vector store clearing failed")
        print("🔧 Please check the logs and try again")
        logger.error("Admin operation: Both SQL and vector store clearing failed")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Admin script unexpected error: {e}")
        sys.exit(1)
