import nifty50
import sensex
import finnifty
import banknifty
import bankex

def main():
    while True:
        print("\nSelect an index to fetch live data:")
        print("1. NIFTY 50")
        print("2. SENSEX")
        print("3. FIN NIFTY")
        print("4. BANK NIFTY")
        print("5. Exit")

        choice = input("Enter your choice (1/2/3/4/5): ")

        if choice == "1":
            nifty50.fetch_nifty_data()
        elif choice == "2":
            sensex.fetch_sensex_data()
        elif choice == "3":
            finnifty.fetch_finnifty_data()
        elif choice == "4":
            banknifty.fetch_banknifty_data()
        elif choice == "5":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please select again.")

if __name__ == "__main__":
    main()
