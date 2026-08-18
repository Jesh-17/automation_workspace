from alarm_reports import alarm_reports, merge_alarm_reports, priorities_and_handledbyl2_filling, cleanup_alarm_reports

def confirm_before_cleaning():
    print("\n⚠ This process is to clean entire reports folder.")
    proceed = input("Do you want to proceed now? (Yes/No): ").strip().lower()
    return proceed == "yes"

def main():
    print("===Choose an option from the below👇:===")
    print("0.) Process of getting the alarm reports from AWS portal")
    print("1.) Exit")

    choice = input("Enter your choice: ")

    match choice:

        case "0":

            if confirm_before_cleaning():
                cleanup_alarm_reports()
                alarm_reports()
                merge_alarm_reports()
                priorities_and_handledbyl2_filling()
                
            else:
                print("Process skipped. Please run this if you really want to clean the reports folder.")


        case "1":
            print("Exiting...")

        case _:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":

    main()
