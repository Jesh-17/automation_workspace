from alarm_report.alarm_reports import alarm_reports, merge_alarm_reports, priorities_and_handledbyl2, cleanup_alarm_reports

from wsr.priorities_and_handledbyl2_filling import priorities_and_handledbyl2_filling
from wsr.child_or_parent_corresponding_date import child_or_parent_corresponding_date

#from tickets_separation.alarms_processor import alarms_separation, create_custom_columns_excel, add_duration_alarms_sheet, add_re_fine_tuning_alarms_sheet, add_alarms_required_tickets_sheet
from tickets_separation.alarms_separation import tickets_separation

from wsr.parent_filling_using_ticket_tracker import parent_filling_using_ticket_tracker
from wsr.parent_filling_using_previous_week_alarm_sheet import parent_filling_using_previous_week_alarm_sheet
from wsr.filling_na_for_no_tickets import filling_na_for_no_tickets

from dump_refinement.actual_alarm_dump import actual_alarm_dump




def confirm_before_cleaning():
    print("\n⚠ This process is to clean entire reports folder.")
    proceed = input("Do you want to proceed now? (Yes/No): ").strip().lower()
    return proceed == "yes"



def confirm_monday_execution():
    print("\n⚠ This process is recommended to run on Monday morning since tickets may still be created before then.")
    proceed = input("Do you want to proceed now? (Yes/No): ").strip().lower()
    return proceed == "yes"




def main():
    print("===Choose an option from the below👇:===")
    print("0.) Process of refining the alarm dump of outlook from excel")
    print("1.) Process of getting the alarm reports from AWS portal")
    print("2.) Process of filling priorities and handledbyl2 columns")
    print("3.) 2 + Process of filling data to the alarms(to corresponding dates)")
    print("4.) 3 + Process of filling data to the alarms, if tickets are not available in ticket tracker then using parent data from ticket tracker")
    print("5.) Process of finding the alarms for which tickets to be created")
    print("6.) Process of filling data to the alarms, if tickets are not available in ticket tracker and taking parent data from previous week alarm sheet")
    print("7.) Process of filling data to the alarms via N/A, if no parent data available from the previous week alarm sheet")
    print("8.) Exit")

    choice = input("Enter your choice: ")

    match choice:
        
        case "0":
            actual_alarm_dump()

        case "1":
            if confirm_before_cleaning():
                cleanup_alarm_reports()
                alarm_reports()
                merge_alarm_reports()
                priorities_and_handledbyl2()
                
            else:
                print("Process skipped. Please run this if you really want to clean the reports folder.")

        case "2":
            priorities_and_handledbyl2_filling()

        case "3":
            priorities_and_handledbyl2_filling()
            child_or_parent_corresponding_date()

        case "4":
            if confirm_monday_execution():
                priorities_and_handledbyl2_filling()

                child_or_parent_corresponding_date()

                parent_filling_using_ticket_tracker()
            else:
                print("Process skipped. Please run this on Monday morning.")


        case "5":
            #if confirm_monday_execution():
                #priorities_and_handledbyl2_filling()

                # This fills the created tickets corresponding to child and parent
                #child_or_parent_corresponding_date()
                #parent_filling_using_ticket_tracker()


                # This is actual ticket separation for which tickets needed
                # alarms_separation()
                # create_custom_columns_excel()
                # add_duration_alarms_sheet()
                # add_re_fine_tuning_alarms_sheet()
                # add_alarms_required_tickets_sheet()
            # else:
            #     print("Process skipped. Please run this on Monday morning.")

            tickets_separation()


        case "6":
            if confirm_monday_execution():
                # priorities_and_handledbyl2_filling()
                # child_or_parent_corresponding_date()
                # parent_filling_using_ticket_tracker()
                parent_filling_using_previous_week_alarm_sheet()
            else:
                print("Process skipped. Please run this on Monday morning.")
                
        case "7":
            if confirm_monday_execution():
                # priorities_and_handledbyl2_filling()
                # child_or_parent_corresponding_date()
                # parent_filling_using_ticket_tracker()
                # parent_filling_using_previous_week_alarm_sheet()
                filling_na_for_no_tickets()
            else:
                print("Process skipped. Please run this on Monday morning.")
        
        case "8":
            print("Exiting...")
        case _:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()









# from wsr.priorities_and_handledbyl2_filling import priorities_and_handledbyl2_filling
# from wsr.child_or_parent_corresponding_date import child_or_parent_corresponding_date
# from wsr.parent_filling_using_ticket_tracker import parent_filling_using_ticket_tracker
# from wsr.parent_filling_using_previous_week_alarm_sheet import parent_filling_using_previous_week_alarm_sheet
# from wsr.filling_na_for_no_tickets import filling_na_for_no_tickets


# def main():
#     print("Choose an option:")
#     print("1. Process of filling priorities and handledbyl2 columns")
#     print("2. Process of filling data to the alarms(to corresponding dates)")
#     print("3. Process of filling data to the alarms, if tickets are not avaialble in ticket tracker then using parent data from ticket tracker")
#     print("4. Process of filling data to the alarms, if tickets are not avaialble in ticket tracker and taking parent data from previous week alarm sheet")
#     print("5. Process of filling date to the alarms via N/A, if no parent data available from the previous week alarm sheet")
#     print("6. Exit")

#     choice = input("Enter your choice: ")

#     match choice:
#         case "1":
#             priorities_and_handledbyl2_filling()
#         case "2":
#             child_or_parent_corresponding_date()
#         case "3":
#             parent_filling_using_ticket_tracker()
#         case "4":
#             parent_filling_using_previous_week_alarm_sheet()
#         case "5":
#             filling_na_for_no_tickets()
#         case _:
#             print("Invalid choice. Please try again.")

# if __name__ == "__main__":
#     main()
