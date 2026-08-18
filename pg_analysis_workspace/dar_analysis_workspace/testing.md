```json
"error: POST:/v4/trusted/auth/magic-links:trace:creationChannel:oneappweb, creationChannelType:agent, agentId:drupalexpress, apiKey:****SogGAa : async-service:syncAccountsByBillingAccount: error occurred while synching accounts by billing account:5004669:error:{\"statusCode\":500,\"headers\":{},\"body\":{\"success\":false,\"body\":null,\"status\":[{\"code\":\"EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-INTERNAL-SERVER-ERROR\",\"description\":\"Billing system get accounts api returned internal server error\",\"userMessage\":\"Billing system get accounts api returned internal server error\",\"errorDetails\":\"Billing system get accounts api returned internal server error\"}]}}\n"

```

error: POST:/v4/trusted/auth/magic-links:trace:creationChannel:oneappweb, creationChannelType:agent, agentId:drupalexpress, apiKey:****SogGAa :
async-service:syncAccountsByBillingAccount: error occurred while synching accounts by billing account:5004669:error:{\"statusCode\":500,\"headers\":{},\"body\":{\"success\":false,\"body\":null,\"status\":[{\"code\":\"EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-INTERNAL-SERVER-ERROR\",\"description\":\"Billing system get accounts api returned internal server error\",\"userMessage\":\"Billing system get accounts api returned internal server error\",\"errorDetails\":\"Billing system get accounts api returned internal server error\"}]}}\n"



key: *, key:value, key:value, key:value :
key: *:*:*:{\"toptopkey\":toptopvalue,\"toptopkey\":toptopvalue,\"toptopkey\":{\"topkey\":topvalue,\"topkey\":topvalue,\"topkey\":[{\"key\":\"value\",\"key\":\"value\",\"key\":\"value\",\"key\":\"value\"}]}}\n"





error: POST:/v4/trusted/auth/magic-links:trace:creationChannel:oneappweb, creationChannelType:agent, agentId:drupalexpress, apiKey:****SogGAa :
async-service:syncAccountsByBillingAccount: error occurred while synching accounts by billing account:5004669:error:{\"statusCode\":500,\"headers\":{},\"body\":{\"success\":false,\"body\":null,\"status\":[{\"code\":\"EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-INTERNAL-SERVER-ERROR\",\"description\":\"Billing system get accounts api returned internal server error\",\"userMessage\":\"Billing system get accounts api returned internal server error\",\"errorDetails\":\"Billing system get accounts api returned internal server error\"}]}}\n"



I have `logs-insights-results(nov1-nov30).xlsx` it is having the columns `Date	Message	Count
` Now Under column `Message` having the values like ex: "error: POST:/v4/trusted/auth/magic-links:trace:creationChannel:oneappweb, creationChannelType:agent, agentId:drupalexpress, apiKey:****SogGAa : async-service:syncAccountsByBillingAccount: error occurred while synching accounts by billing account:5004669:error:{""statusCode"":500,""headers"":{},""body"":{""success"":false,""body"":null,""status"":[{""code"":""EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-INTERNAL-SERVER-ERROR"",""description"":""Billing system get accounts api returned internal server error"",""userMessage"":""Billing system get accounts api returned internal server error"",""errorDetails"":""Billing system get accounts api returned internal server error""}]}}
" So their syntax would be ex: "<..............., key:value, key:value, key:value> : <......{...., key:value, key:value, key:value> : <.......> : .........."  Here consider as data `..........` till you find `, ` for this column name `1st_required` under that data value. key is the column name under that value, and later separator ` : ` later if you see `....` till you find first `{` before  for this column name `2nd_required` under that data value. Later including `{....` till end for the column name `3rd_required` under thatv data value. Note: these all should be in order. So it won't effect rows and columns corresponding data.

 So i want separate excel name `dar_refined.xlsx` under I want columns `Date Count 1st_required... key .........`  So give the prefect python script

"<..............., key:value, key:value, key:value> : <......{...., key:value, key:value, key:value> : <.......> : .........."  Here consider as data `..........` till you find `, ` for this column name `1st_required` under that data value. key is the column name under that value, and later separator ` : ` later if you see `....` till you find first `{` before  for this column name `2nd_required` under that data value. Later including `{....` till end for the column name `3rd_required` under thatv data value. Note: these all should be in order. So it won't effect rows and columns corresponding data.



Now I have `dar_refined.xlsx` it is having the columns are `<Date>	<Count> .....<3rd_required>......` and Under column `3rd_required` we are having the values ex: {"statusCode":500,"headers":{},"body":{"success":false,"body":null,"status":[{"code":"EXTERNAL-APIS:BILLING-SYSTEM-GET-ACCOUNTS-API-RETURNED-INTERNAL-SERVER-ERROR","description":"Billing system get accounts api returned internal server error","userMessage":"Billing system get accounts api returned internal server error","errorDetails":"Billing system get accounts api returned internal server error"}]}}

i.e the syntax would be: {\"key\":value,..........,\"key\":value,\"key\":{\"subkey\":subvalue,.............\"subkey\":subvalue,\"subkey\":[{\"subsubkey\":\"subsubvalue\",....................\"subsubkey\":\"subsubvalue\",\"subsubkey\":\"subsubvalue\",\"subsubkey\":\"subsubvalue\",...........}]}}

Now i want new excel name called `sub_dar_refined.xlsx` it should have the columns `<Date> <Count>  <key> .... <key.subkey>...<key.subkey.subsubkey>.....` until you get the values. So under that columns values. Note: Don't miss anything dig into it. And also don't miss any row. make sure all columns should be order wise so that it won't effect the other columns correct data. Here `Date` column is optional if there means give. So give the python script

the syntax would be: 

{\"key\":value,..........,\"key\":value,\"key\":{\"subkey\":subvalue,.............\"subkey\":subvalue,\"subkey\":[{\"subsubkey\":\"subsubvalue\",....................\"subsubkey\":\"subsubvalue\",\"subsubkey\":\"subsubvalue\",\"subsubkey\":\"subsubvalue\",...........}]}}

or

{"key":value,..........,"key":value,"key":{"subkey":subvalue,............."subkey":subvalue,"subkey":[{"subsubkey":"subsubvalue",...................."subsubkey":"subsubvalue","subsubkey":"subsubvalue","subsubkey":"subsubvalue",...........}]}}

or

{"key":value,.......,"key":"value",.............}













I have `sub_dar_refined.xlsx` it is having the columns `Date	Count	statusCode	headers	body.success	body.body	body.status.code	body.status.description	body.status.errorDetails ............`. So ask the user in the terminal itself provide the required columns. if in the provided columns has `statusCode`
