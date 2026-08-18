from dar_individual_keys_datacount.keys_datacount import dar_individual_keys_datacount
from sub_dar_individual_keys_datacount.keys_datacount import sub_dar_individual_keys_datacount

def main():
    print("===Choose an option from the below👇:===")
    print("1.) Process of finding individual keys/columns data table-wise of dar_refined.xlsx")
    print("2.) Process of finding individual keys/columns data table-wise of sub_dar_refined.xlsx")
    
    choice = input("Enter your choice: ")

    match choice:

        case "1":
            dar_individual_keys_datacount()
        
        case "2":
            sub_dar_individual_keys_datacount()
        
        case _:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
