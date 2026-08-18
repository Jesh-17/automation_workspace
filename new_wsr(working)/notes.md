(Week->10 to 16 Nov)
case-1: if same dates are in that week under ticket tracker and parent ticket is also in that week

ex: 10-Nov-2025       PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request  (here no need to use parent since on 11th child ticket range given from 10th to 11th so that data you can use)

    
    11-Nov-2025 4:12	 PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request  DIGSUPPORT-17147 
                         Pradeep Damera	L2 Team	Completed/Closed	Closed          (child: given range while creating ticket in jira b/w 10 to 11)   so fill this with corresponding date

    11-Nov-2025 5:26	PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|QueryTimeoutException DIGSUPPORT-17150
                         Pradeep Damera	L3 Team	Completed/Closed	Pending         (parent)  use this on monday, if and only if no child tickets are not there for the dates  (if this same alarm occured.)

    15-Nov-2025       PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request  (here use parent if no ticket is created)


case-2: if different dates are in that week under ticket tracker and parent ticket is also in that week

ex: 10-Nov-2025       PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request  (here no need to use parent since on 11th child ticket range given from 10th to 11th so that data you can use)

    
    11-Nov-2025 4:12	 PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request  DIGSUPPORT-17147 
                         Pradeep Damera	L2 Team	Completed/Closed	Closed          (child: given range while creating ticket in jira b/w 10 to 11)   so fill this with corresponding date

    12-Nov-2025 5:26	PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|QueryTimeoutException DIGSUPPORT-17150
                         Pradeep Damera	L3 Team	Completed/Closed	Pending         (parent)  fill for corresponding date and also use this on monday, if and only if no child tickets are not there for the dates  (if this same alarm occured.)

    15-Nov-2025       PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request  (here use parent if no ticket is created)


case-3:if same dates are in that week under ticket tracker but parent ticket is in previous week

ex: 0.  10-Nov-2025       PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request  (here use parent)

    1. 11-Nov-2025 4:12	 PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request  DIGSUPPORT-17147 
                         Pradeep Damera	L2 Team	Completed/Closed	Closed    (child)   so fill this with corresponding date

    2.  3-Nov-2025 5:26	PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|QueryTimeoutException DIGSUPPORT-17150
                         Pradeep Damera	L3 Team	Completed/Closed	Pending   (parent)  use this on monday, if and only if no child tickets are not there for dates (if this same alarm occured.)

Note: parent tickets are like  "L3 team   pending-->escalated to l3 team  pending with l3 team",  "app support team   pending-->escalated to app support team  pending with app support team"
      child tickets are like "L2 team  closed ---> Acknowledged by l2 team  closed
                             "L2 team  pending---> Don't fill these since they are working later we can fill it (Simply skip these)

Note: if no parent tickets then give N/A








(WSR-->Mon-Sunday)
On Nov 3rd (Monday)--> previous 2nd date data pulling (sunday)
On Nov 4th (Tuesday)-->previous 3rd date data pulling (Monday)
On Nov 5th (Wednesday)-->previous 4th date data pulling (Tuesday)
On Nov 6th (Thursday)-->previous 5th date data pulling (Wednesday)
On Nov 7th (Friday)-->previous 6th date data pulling   (Thursday)
On Nov 8th (Saturday)-->previous 7th date data pulling  (Friday)
On Nov 9th (Sunday)-->previous 8th date data pulling    (Saturday)
---
On Nov 10th (Monday)-->previous 9th date data pulling
On Nov 11th (Tuesday)-->previous 10th date data pulling
On Nov 12th (Wednesday)-->previous 11th date data pulling
On Nov 13th (Thursday)-->previous 12th date data pulling
On Nov 14th (Friday)-->previous 13th date data pulling
On Nov 15th (Saturday)-->previous 14th date data pulling
On Nov 16th (Sunday)-->previous 15th date data pulling




---

1. I have `day_wise_ticket_tracker_list.xlsx` and it is having columns `SL No.	  Ticket Assigned Date/Time	 AlarmDescription 	Ticket Categorization    JIRA Ticket No.	  Response Date/Time	  Actual Response Time	  Ticket Type	 Application	  Priority	Ticket Received/Raised By	Ticket Assigned To	Ticket Analysis By L2	 Ticket Status	   Resolution Comments	     Resolution/Analysis Date/Time	 Actual Resolution/Analysis Time 	SLA Met - Response Time	      SLA Met - Resolution/Analysis Time	Closed By L2 Team`. In this consider columns `Ticket Assigned Date/Time     AlarmDescription     JIRA Ticket No.     Ticket Assigned To      Ticket Status`


   Note: Under `Ticket Assigned Date/Time` column date would be there ex: 10-Nov-2025 4:12
         Under `AlarmDescription` column alarm name would be there but that name consider till first pipe symbol `|` before. ex: PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request
         Under `JIRA Ticket No.` column ticket id of that particular would be there ex: DIGSUPPORT-17147
         Under `Ticket Assigned To` column teams would be there ex: L2 Team, AppSupport Team, L3 Team
         Under `Ticket Status` column status would be there ex: Closed, Pending


2. I have `day_wise_tiggered_alarms_list.xlsx` and it is having columns `S.No	Date	Time	AlarmDescription	Priority	HandledbyL2	EscalatedtoL3/AppSupportteam	Ticketnumber	Status` In this columns to be filled are `EscalatedtoL3/AppSupportteam	Ticketnumber	Status`
     
   Note: How to fill the columns in this file
   case: First check `day_wise_ticket_tracker_list.xlsx` if here column `Ticket Assigned Date/Time` having date ex: 10-Nov-2025 4:12  matches with the date in `Date` ex: 11/10/2025 column of `day_wise_tiggered_alarms_list.xlsx` and also if here `AlarmDescription` column of `day_wise_ticket_tracker_list.xlsx` matches with the `AlarmDescription` of `day_wise_tiggered_alarms_list.xlsx` and if under `Ticket Assigned To` column of `day_wise_ticket_tracker_list.xlsx` is having the value "L2 Team" and also `Ticket Status` column of `day_wise_ticket_tracker_list.xlsx` is having the value "Closed" this is called child and also check under the same date if under `Ticket Assigned To` column of `day_wise_ticket_tracker_list.xlsx` is having the value "AppSupport team" and also `Ticket Status` column of `day_wise_ticket_tracker_list.xlsx` is having the value "Pending" this is called parent and also check under the same date if under `Ticket Assigned To` column of `day_wise_ticket_tracker_list.xlsx` is having the value "L3 Team" and also `Ticket Status` column of `day_wise_ticket_tracker_list.xlsx` is having the value "Pending" this is also called parent. Then you should consider like below while filling columns `EscalatedtoL3/AppSupportteam	Ticketnumber	Status`

   1. On same date if child exists then no need of checking parents simply you can fill with child date i.e  fill the columns of
`day_wise_tiggered_alarms_list.xlsx` like below
             `JIRA Ticket No.` of `day_wise_ticket_tracker_list.xlsx` value must give to the `Ticketnumber` of `day_wise_tiggered_alarms_list.xlsx`
             `EscalatedtoL3/AppSupportteam` column of `day_wise_tiggered_alarms_list.xlsx` must be fill by "Acknowledged by L2 Team"
             `Status` column  of `day_wise_tiggered_alarms_list.xlsx` must be fill by "Closed" 
   2. On same date if child does not exists then you need to check parent exists or not if exists simply you can fill with parent(AppSupport team) date i.e  fill the columns of
`day_wise_tiggered_alarms_list.xlsx` like below
             `JIRA Ticket No.` of `day_wise_ticket_tracker_list.xlsx` value must give to the `Ticketnumber` of `day_wise_tiggered_alarms_list.xlsx`
             `EscalatedtoL3/AppSupportteam` column of `day_wise_tiggered_alarms_list.xlsx` must be fill by "Escalated to AppSupport team"
             `Status` column  of `day_wise_tiggered_alarms_list.xlsx` must be fill by "Pending with AppSupport team"

   3. On same date if child does not exists then you need to check parent exists or not if exists simply you can fill with parent(L3 team) date i.e  fill the columns of
`day_wise_tiggered_alarms_list.xlsx` like below
             `JIRA Ticket No.` of `day_wise_ticket_tracker_list.xlsx` value must give to the `Ticketnumber` of `day_wise_tiggered_alarms_list.xlsx`
             `EscalatedtoL3/AppSupportteam` column of `day_wise_tiggered_alarms_list.xlsx` must be fill by "Escalated to L3 team"
             `Status` column  of `day_wise_tiggered_alarms_list.xlsx` must be fill by "Pending with L3 team"
     

Now give a python script for this from main only child_or_parent_corresponding_date() function call. give in a switch case since in the future I will add lot of functions


----
Parent data filling by check the ticket tracker

1. I have `child_or_parent_corresponding_date_day_wise_tiggered_alarms_list.xlsx` it is having the columns `S.No	Date	Time	AlarmDescription	Priority	HandledbyL2	EscalatedtoL3/AppSupportteam	Ticketnumber	Status` Here we need to consider `AlarmDescription` column it is having alarm name and you should consider columns of this alarm are `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` filled or not. if those columns are not filled then you should check with the same alarm name any parent is there are not. If parent is there means then you can fill the parents data for that alarm. if two parents are there means then you should consider the latest parent data.

How we can identify the parent in that  `child_or_parent_corresponding_date_day_wise_tiggered_alarms_list.xlsx`?

check the `AlarmDescription` column and also `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` if here `EscalatedtoL3/AppSupportteam` having data "Escalated to AppSupport team" and `Status` having data "Pending with AppSupport team" then it is act as parent. And also check the `AlarmDescription` column and also `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` if here `EscalatedtoL3/AppSupportteam` having data "Escalated to L3 team" and `Status` having data "Pending with L3 team" this also act as parent. So like wise you need to compare the alarm if name matches you can utilize the parent data for that alarm.


Now give a python script for parent_filling_using_ticket_tracker() only call from main fucntion



New process:

1. I have `day_wise_ticket_tracker_list.xlsx` it is having the columns are `SL No.	 Ticket Assigned Date/Time 	AlarmDescription 	Ticket Categorization	JIRA Ticket No.	Response Date/Time	Actual Response Time	    Ticket Type	    Application	     Priority	   Ticket Received/Raised By	   Ticket Assigned To	   Ticket Analysis By L2	  Ticket Status	  Resolution Comments	   Resolution/Analysis Date/Time	     Actual Resolution/Analysis Time	   SLA Met - Response Time    	SLA Met - Resolution/Analysis Time	   Closed By L2 Team`. 

Note: Under `Ticket Assigned Date/Time` column date would be there ex: 10-Nov-2025 4:12
         Under `AlarmDescription` column alarm name would be there but that name consider till first pipe symbol `|` before. ex: PaymentGateway-prod-AsyncPayments-Microservice-Exceptions|400|Invalid Request
         Under `JIRA Ticket No.` column ticket id of that particular would be there ex: DIGSUPPORT-17147
         Under `Ticket Assigned To` column teams would be there ex: L2 Team, AppSupport Team, L3 Team
         Under `Ticket Status` column status would be there ex: Closed, Pending

Now, alarm name column `AlarmDescription` of `child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx` matches with the alarm name column `AlarmDescription`  of `day_wise_ticket_tracker_list.xlsx` but consider till first pipe symbol `|` before here. then Later you should consider the latest date column `Ticket Assigned Date/Time` of that alarm  of  `day_wise_ticket_tracker_list.xlsx`. But in that latest date only consider the parent data. Then what is parent data.

if `Ticket Assigned To` is having value "AppSupport team" and also `Ticket Status` is having value "Pending" then it is parent, 
if `Ticket Assigned To` is having value "L3 team" and also `Ticket Status` is having value "Pending" then it is also parent

Note: if no parent data then consider next previous latest data and follow the same process like above to get the parent data.


2. I have `child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx` it is having the columns `S.No	Date	Time	AlarmDescription	Priority	 HandledbyL2	EscalatedtoL3/AppSupportteam	Ticketnumber	Status` Here we need to consider `AlarmDescription` column it is having alarm name and if this alarm having columns are `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` not filled then you should fill columns of this alarm. if these columns are filled then don't do anything. if these columns are not filled then how to fill?

  a) if `Ticket Assigned To` is having value "AppSupport team" and also `Ticket Status` is having value "Pending" then `EscalatedtoL3/AppSupportteam` column of `child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx` have "Escalated to AppSupport team" also `Status` column of `child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx` have "Pending with AppSupport team" and `Ticketnumber` column get value from `JIRA Ticket No.` of that alarm

  b) if `Ticket Assigned To` is having value "L3 team" and also `Ticket Status` is having value "Pending" then `EscalatedtoL3/AppSupportteam` column of `child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx` have "Escalated to L3 team" also `Status` column of `child_or_parent_corresponding_date_filled_in_this_day_wise_tiggered_alarms_list.xlsx` have "Pending with L3 team" and `Ticketnumber` column get value from `JIRA Ticket No.` of that alarm

  

----

Parent data filling by check the previous week alarm received sheet

1. I have `parent_filling_using_ticket_tracker_day_wise_tiggered_alarms_list.xlsx` it is having the columns `S.No	Date	Time	AlarmDescription	Priority	HandledbyL2	EscalatedtoL3/AppSupportteam	Ticketnumber	Status` Here we need to consider `AlarmDescription` column it is having alarm name and you should consider columns of this alarm are `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` filled or not. if those columns are not filled then you should check in the `previous_week_day_wise_tiggered_alarms_list.xlsx` with the same alarm name any parent is there are not. If parent is there means then you can fill the parents data for that alarm. if two parents are there means then you should consider the latest parent data.

How we can identify the parent in that  `previous_week_day_wise_tiggered_alarms_list.xlsx`?

check the `AlarmDescription` column and also `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` if here `EscalatedtoL3/AppSupportteam` having data "Escalated to AppSupport team" and `Status` having data "Pending with AppSupport team" then it is act as parent. And also check the `AlarmDescription` column and also `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` if here `EscalatedtoL3/AppSupportteam` having data "Escalated to L3 team" and `Status` having data "Pending with L3 team" this also act as parent. So like wise you need to compare the alarm if name matches you can utilize the parent data for that alarm.


Now give a python script for parent_filling_using_previous_week_alarm_sheet() only call from main function



new process:
1. I have `parent_filling_using_ticket_tracker_day_wise_tiggered_alarms_list.xlsx` it is having the columns `S.No	Date	Time	AlarmDescription	Priority	HandledbyL2	EscalatedtoL3/AppSupportteam	Ticketnumber	Status` Here we need to consider `AlarmDescription` column it is having alarm name and you should consider columns of this alarm are `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` filled or not. if those columns are not filled then you should check in the `previous_week_day_wise_tiggered_alarms_list.xlsx` it is also having columns `S.No	Date	Time	AlarmDescription	Priority	HandledbyL2	EscalatedtoL3/AppSupportteam	Ticketnumber	Status` Here also we need to consider `AlarmDescription` column of `previous_week_day_wise_tiggered_alarms_list.xlsx`  it should having that alarm name and you should consider columns of that same alarm are `EscalatedtoL3/AppSupportteam	 Ticketnumber	Status` and with the same alarm name any child or parent for the latest Date is there are not. first priority: If child is there means then you can fill the child data for that alarm via considering latest `Date` if no child for that date check previous latest date and so on. second priority: if no child found then consider parents, if parents are there means then you should consider the latest parent date data and if not so on check previous latest dates also.

How we can identify the child and parent in that  `previous_week_day_wise_tiggered_alarms_list.xlsx`?

a) check the `AlarmDescription` column and also `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` if here `EscalatedtoL3/AppSupportteam` having data "Acknowledged by L2 Team" and `Status` having data "Closed" then it is act as child.

b) check the `AlarmDescription` column and also `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` if here `EscalatedtoL3/AppSupportteam` having data "Escalated to AppSupport team" and `Status` having data "Pending with AppSupport team" then it is act as parent. And also check the `AlarmDescription` column and also `EscalatedtoL3/AppSupportteam	Ticketnumber	Status` if here `EscalatedtoL3/AppSupportteam` having data "Escalated to L3 team" and `Status` having data "Pending with L3 team" this also act as parent. So like wise you need to compare the alarm if name matches you can utilize the child data first later only consider parent for that alarm.


Now Make sure it won't skip or miss any alarm , give a python script for parent_filling_using_previous_week_alarm_sheet() only call from main function and everything should be present in parent_filling_using_previous_week_alarm_sheet()
----
Priorities and handledbyl2 columns filling

1. I have `day_wise_tiggered_alarms_list.xlsx` it is having the columns `S.No	Date	Time	AlarmDescription	Priority	HandledbyL2	EscalatedtoL3/AppSupportteam	Ticketnumber	Status` from this we need to consider the columns to fill are `Priority	   HandledbyL2` then how we need to fill these columns?
  
   Note: For all alarms `HandledbyL2` column is always give "Yes"
   check `all_alarms_list.xlsx` it is having the columns `S.No	  AlarmDescription	Priority` From this compare the alarm name  and corresponding priority. Based on this we can fill the column `Priority` of `day_wise_tiggered_alarms_list.xlsx`  Note: Only fill when two are empty

Now give a python script for priorities_and_handledbyl2_filling() only call from main function
----











---
Note:

1. if L2 Team   Pending---> then it means L2 is current working that time won't consider. later once it is closed then only we should consider and fill.
2. check the ticket created(Child mainly) of that particular alarm everyday in jira like what range they given while creating this ticket if that range covering the previous dates of the same particular alarm. then you can use this child data for the previous dates of the particualr alarm. 
ex: on 3rd x alarm triggered but ticket not created
    on 5th same x alarm triggerd but ticket is created Note: while creating the ticket in jira given as range in comments like 3rd to 5th hence this 5th date ticket data can be utilized for dates from 3 to 5 for the same x alarm.

    - if no ticket is created for the 3rd and also no date range is covering for 3rd then parent ticket coming to picture it should be run on monday morning.
       - check under ticket tracker any parent ticket is there or not with same alarm name. if so fill 3rd date with that data.
       - check under ticket tracker if no parent ticket is there then check the previous week parent data for the same alarm name. if so fill 3rd date with that parent data.
       - In previous week also parent tiket for the same alarm not there means then give N/A for `Ticketnumber` and Acknowledged by L2 Team for `EscalatedtoL3/AppSupportteam` and Closed for `Status`



----------------------------------------------
(From ticket tracker  while summary filling)
Priority-->P1-->Critical
Priority-->P2-->High
Priority-->P3-->Major
Priority-->P4-->Minor
--
WSR PPT:  (From ticket tracker)
Appsupport team:         Created   closed
  P1:Ticket assigned     
  P2:Ticket assigned 
  P3:Ticket assigned        8        8
  P4:Ticket assigned 

L3 team:                 Created   closed
  P1:Ticket assigned     
  P2:Ticket assigned 
  P3:Ticket assigned        8        8
  P4:Ticket assigned 

L2 team:                 Created   closed
  P1:Ticket assigned     
  P2:Ticket assigned 
  P3:Ticket assigned        10        10
  P4:Ticket assigned 


(From alarm received sheet)
Alarm Priority      Alarm count
Critial     (P1)       53
High        (P2)       582
Major/Medium(P3)       439
Minor/Low   (P4)       200
Grand total:  53+582+439+200=1274
------------------------------------------------
Note:
(While filling the parent ticket tracker)
PaymentGateway-prod-Orders-Microservice-Exceptions-->PaymentGateway-prod-API-5XXErrors ---> give this data


PaymentGateway-prod-Payment-Token-Microservice-Exceptions  -- Minor      but High or Critical
tigo-cognito-prod-master-Monitoring-6I7LSTA3KZJH-DARApiGateway5XXErrorAlarm-13T4WI2OP8WG1|HE-OTP-LOGIN:ERR79 --  High   but Major
-------------------------------------------------




# Dsr
1. created msr:
      - From: start date
      - To: next date
2. updated msr:
      - From: start date
      - To: next date
3. resolved msr:
      - From: start date
      - To: next date
4. club all these in one sheet and later select all and remove the duplicates(by checking all). And later under `reporter` select our team names(ex: (senthilkumar1, SiddheshK4, pradeepd1, tetalik, maheshp6, veneshg, mob-support, manojk25, honeyp, AnandM4, nihaln, HeerabJ, DharanyaS)), later remove the duplicates by slecting the column based on jira ticket number issue key and under add ticket tracker tickets (To remove duplicates of it in excel go to data->Top right `Text to Columns` beside duplicate button would be there-->select one which column based we need to remove)
5. Later highlight the tickets which are present in ticket tracker.
6. Later other than those highlighted ..remaining tickets we need to check in jira like wheather to add these tickets in tracker or not.

# Wsr and msr
1. created msr:
      - From: start date
      - To: next date
2. updated msr:
      - From: start date
      - To: upto the date
3. resolved msr:
      - From: start date
      - To: upto the date
4. club all these in one sheet and later select all and remove the duplicates(by checking all). And later under `reporter` select our team names(ex: (senthilkumar1, SiddheshK4, pradeepd1, tetalik, maheshp6, veneshg, mob-support, manojk25, honeyp, AnandM4, nihaln, HeerabJ, DharanyaS)), later remove the duplicates by slecting the column based on jira ticket number issue key  and under add ticket tracker tickets (To remove duplicates of it in excel go to data->Top right `Text to Columns` beside duplicate button would be there-->select one which column based we need to remove)
5. Later highlight the tickets which are present in ticket tracker.
6. Later other than those highlighted ..remaining tickets we need to check in jira like wheather to add these tickets in tracker or not.







































































```pwsh
while ($true)
{
$wshell = new-object -ComObject wscript.shell
$wshell.sendkeys("{f2}")
Start-Sleep -Seconds 20
}

```


                  
 