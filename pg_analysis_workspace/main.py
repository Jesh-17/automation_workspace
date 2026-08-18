from pg_individual_keys_datacount.keys_datacount import pg_individual_keys_datacount

def main():
    print("===Choose an option from the below👇:===")
    print("1.) Process of finding individual keys/columns data table-wise of sub_pg_refined.xlsx")
    # print("3.) Process of finding individual topkeys sub-data table-wise")
    # print("4.) Process of finding logs count using topkeys sub-data")

    choice = input("Enter your choice: ")

    match choice:

        case "1":
            pg_individual_keys_datacount()
        
        case _:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
