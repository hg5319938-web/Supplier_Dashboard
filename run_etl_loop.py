"""
ETL Loop - Runs the ETL process every 15 minutes in an infinite loop.
Keeps the dashboard data updated from the Excel source files.
"""
import time
import os
from datetime import datetime

def run_etl_loop():
    """Run ETL process every 15 minutes."""

    print("=" * 60)
    print("🔄 ETL LOOP STARTED")
    print("=" * 60)
    print("This script will run the ETL process every 15 minutes.")
    print("Press Ctrl+C to stop.")
    print("=" * 60)

    # Import ETL function
    from etl import run_etl

    loop_count = 0
    INTERVAL_MINUTES = 15
    INTERVAL_SECONDS = INTERVAL_MINUTES * 60

    while True:
        loop_count += 1
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"\n{'='*60}")
        print(f"🔄 ITERATION #{loop_count}")
        print(f"⏰ Timestamp: {current_time}")
        print(f"{'='*60}")

        try:
            # Check if data files exist
            if os.path.exists('data/suppliers.xlsx') and \
               os.path.exists('data/orders.xlsx') and \
               os.path.exists('data/receipts.xlsx'):

                # Run ETL
                run_etl()
                print(f"\n✅ ETL completed successfully!")

            else:
                print("\n⚠️  Warning: Data files not found!")
                print("   Please run `python generate_data.py` first.")
                print("   Skipping ETL iteration...")

        except Exception as e:
            print(f"\n❌ Error during ETL: {str(e)}")
            print("   Will retry in 15 minutes...")

        print(f"\n💤 Next ETL run in {INTERVAL_MINUTES} minutes...")
        print(f"   (Press Ctrl+C to stop)")

        # Wait for next iteration
        time.sleep(INTERVAL_SECONDS)

if __name__ == '__main__':
    try:
        run_etl_loop()
    except KeyboardInterrupt:
        print("\n\n🛑 ETL Loop stopped by user.")
        print("   Dashboard will continue to display last updated data.")
