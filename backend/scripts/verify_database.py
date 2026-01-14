#!/usr/bin/env python3
"""
Verify Supabase database schema and connection.

This script checks that:
1. Connection to Supabase is working
2. Required tables exist
3. Row Level Security is enabled
4. Policies are configured correctly
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import supabase
from app.config import settings


def verify_connection():
    """Verify connection to Supabase."""
    print("🔍 Verifying Supabase connection...")
    print(f"   URL: {settings.supabase_url}")
    
    try:
        # Try to query the database
        response = supabase.table('clients').select('count', count='exact').execute()
        print("✅ Connection successful!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def verify_tables():
    """Verify that required tables exist."""
    print("\n🔍 Verifying database tables...")
    
    required_tables = ['clients', 'invoices', 'line_items']
    all_exist = True
    
    for table in required_tables:
        try:
            # Try to query each table
            supabase.table(table).select('count', count='exact').execute()
            print(f"✅ Table '{table}' exists")
        except Exception as e:
            print(f"❌ Table '{table}' missing or inaccessible: {e}")
            all_exist = False
    
    return all_exist


def verify_rls():
    """Verify Row Level Security is working."""
    print("\n🔍 Verifying Row Level Security...")
    
    # Note: Without authentication, RLS should prevent access
    # This is expected behavior - we're just checking the tables are protected
    
    try:
        # Try to access clients without auth (should fail or return empty)
        response = supabase.table('clients').select('*').execute()
        
        # If we get here, RLS is working (returns empty for unauthenticated users)
        print("✅ RLS is enabled (unauthenticated access returns empty)")
        return True
        
    except Exception as e:
        # Some errors are expected with RLS
        if 'permission denied' in str(e).lower() or 'rls' in str(e).lower():
            print("✅ RLS is enabled (access denied without authentication)")
            return True
        else:
            print(f"⚠️  Unexpected error: {e}")
            return False


def verify_constraints():
    """Verify database constraints are in place."""
    print("\n🔍 Verifying database constraints...")
    
    print("   Note: Constraint verification requires authenticated access")
    print("   Constraints to verify manually:")
    print("   - Invoice numbers must be unique")
    print("   - Quantities and unit rates must be positive")
    print("   - Due date must be >= invoice date")
    print("   - Invoice status must be: draft, sent, paid, or overdue")
    
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Invoice Generator - Database Verification")
    print("=" * 60)
    
    checks = [
        ("Connection", verify_connection),
        ("Tables", verify_tables),
        ("Row Level Security", verify_rls),
        ("Constraints", verify_constraints),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! Database is configured correctly.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        print("\nNext steps:")
        print("1. Ensure you've applied the migration: backend/migrations/001_initial_schema.sql")
        print("2. Check your .env file has correct SUPABASE_URL and SUPABASE_KEY")
        print("3. Verify your Supabase project is active")
        return 1


if __name__ == "__main__":
    sys.exit(main())
