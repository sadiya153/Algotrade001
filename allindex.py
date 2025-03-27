# allIndex.py
import nifty50
import sensex

def main():
    while True:
        print("\nSelect the index to track:")
        print("1. NIFTY 50")
        print("2. SENSEX")
        print("3. Exit")

        choice = input("\nEnter your choice (1/2/3): ").strip()

        if choice == "1":
            nifty50.fetch_nifty50_data()
        elif choice == "2":
            sensex.fetch_sensex_data()
        elif choice == "3":
            print("\nExiting")
            break
        else:
            print("⚠️ Invalid choice! Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
