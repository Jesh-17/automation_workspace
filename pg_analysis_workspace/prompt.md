I have `logs-insights-results(nov1-nov30).xlsx` it is having the columns `Date	Message	Count` under column `Message` it is having this kind of structure ex:


```json
"{""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Invalid Request\"",\""userMessage\"":\""Token is associated with active enrollment, cannot delete the token\"",\""errorDetail\"":\""Requested payment token cannot be deleted as it is already associated with an active enrolment\"",\""externalErrorCode\"":null}]"",""applicationName"":null,""applicationContext"":null,""listOfException"":null,""environment"":null}: com.mobiquity.millicom.commons.exception.PaymentGatewayException
com.mobiquity.millicom.commons.exception.PaymentGatewayException: {""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Invalid Request\"",\""userMessage\"":\""Token is associated with active enrollment, cannot delete the token\"",\""errorDetail\"":\""Requested payment token cannot be deleted as it is already associated with an active enrolment\"",\""externalErrorCode\"":null}]"",""applicationName"":null,""applicationContext"":null,""listOfException"":null,""environment"":null}
 at com.mobiquity.millicom.commons.wrappers.ErrorResponseComponent.handleExceptions(ErrorResponseComponent.java:70)
 at com.mobiquity.millicom.handler.LambdaHandler.handleRequest(LambdaHandler.java:50)
 at sun.reflect.GeneratedMethodAccessor81.invoke(Unknown Source)
 at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
 at java.lang.reflect.Method.invoke(Method.java:498)

"
```
And also i can give entire order syntax of structure of all logs ex: "{""httpStatusCode"":*,""body"":*,""errors"":""[{\""httpStatusCode\"":*,\""code\"":*,\""description\"":\""*\"",\""userMessage\"":\""*\"",\""errorDetail\"":\""*\"",\""externalErrorCode\"":\""*\""}*]"",""applicationName"":*,""applicationContext"":*,""listOfException"":*,""environment"":*}:*" as Httpstatuscode, body, httpstatuscode, code, description, usermessage, errorDetail, externalErrorCode, errors_next_json, applicationName, applicationContext, listOfException, environment, ExceptionClass_Json_Packages

I want new excel name `pg_parsed.xlsx` it should have columns `Date	Message	Count <Remaining columns i can provide the keys in a order such that based on those give its corresponidng values under it>`
ex: `Date	Message	Count Httpstatuscode, body, httpstatuscode, code, description, usermessage, errorDetail, externalErrorCode, errors_next_json, applicationName, applicationContext, listOfException, environment, ExceptionClass_Json_Packages`





"{""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Invalid Request\"",\""userMessage\"":\""OrderId is already verified\"",\""errorDetail\"":\""Transaction is already verified\"",\""externalErrorCode\"":null}]"",""applicationName"":null}: com.mobiquity.millicom.commons.exception.PaymentGatewayException
com.mobiquity.millicom.commons.exception.PaymentGatewayException: {""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Invalid Request\"",\""userMessage\"":\""OrderId is already verified\"",\""errorDetail\"":\""Transaction is already verified\"",\""externalErrorCode\"":null}]"",""applicationName"":null}
 at com.mobiquity.millicom.commons.wrappers.ErrorResponse.handleExceptions(ErrorResponse.java:53)
 at com.mobiquity.millicom.handler.LambdaHandler.handleRequest(LambdaHandler.java:41)
 at sun.reflect.GeneratedMethodAccessor125.invoke(Unknown Source)
 at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
 at java.lang.reflect.Method.invoke(Method.java:498)

"




"{""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":500,\""code\"":500,\""description\"":\""Internal Server Error - Please try again later\"",\""userMessage\"":\""Internal Server Error - Please try again later\"",\""errorDetail\"":\""Internal Server Error - Please try again later\"",\""externalErrorCode\"":\""20-09A\""},{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Invalid Request\"",\""userMessage\"":\""Payment Token not found\"",\""errorDetail\"":\""Payment Token not found\"",\""externalErrorCode\"":null}]"",""applicationName"":""billing-mobile-invoice-nequi-prd-co""}: com.mobiquity.millicom.commons.exception.PaymentGatewayException
com.mobiquity.millicom.commons.exception.PaymentGatewayException: {""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":500,\""code\"":500,\""description\"":\""Internal Server Error - Please try again later\"",\""userMessage\"":\""Internal Server Error - Please try again later\"",\""errorDetail\"":\""Internal Server Error - Please try again later\"",\""externalErrorCode\"":\""20-09A\""},{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Invalid Request\"",\""userMessage\"":\""Payment Token not found\"",\""errorDetail\"":\""Payment Token not found\"",\""externalErrorCode\"":null}]"",""applicationName"":""billing-mobile-invoice-nequi-prd-co""}
 at com.mobiquity.millicom.commons.wrappers.ErrorResponse.handleExceptions(ErrorResponse.java:53)
 at com.mobiquity.millicom.handler.LambdaHandler.handleRequest(LambdaHandler.java:41)
 at sun.reflect.GeneratedMethodAccessor128.invoke(Unknown Source)
 at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
 at java.lang.reflect.Method.invoke(Method.java:498)

"



"{""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Missing or Invalid Payment Currency Code\"",\""userMessage\"":\""Missing or Invalid Payment Currency Code\"",\""errorDetail\"":\""Missing or Invalid Payment Currency Code\"",\""externalErrorCode\"":null},{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Missing or Invalid Application Name\"",\""userMessage\"":\""Missing or Invalid Application Name\"",\""errorDetail\"":\""Missing or Invalid Application Name\"",\""externalErrorCode\"":null}]"",""applicationName"":""""}: com.mobiquity.millicom.commons.exception.PaymentGatewayException
com.mobiquity.millicom.commons.exception.PaymentGatewayException: {""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Missing or Invalid Payment Currency Code\"",\""userMessage\"":\""Missing or Invalid Payment Currency Code\"",\""errorDetail\"":\""Missing or Invalid Payment Currency Code\"",\""externalErrorCode\"":null},{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Missing or Invalid Application Name\"",\""userMessage\"":\""Missing or Invalid Application Name\"",\""errorDetail\"":\""Missing or Invalid Application Name\"",\""externalErrorCode\"":null}]"",""applicationName"":""""}
 at com.mobiquity.millicom.commons.wrappers.ErrorResponse.handleExceptions(ErrorResponse.java:53)
 at com.mobiquity.millicom.handler.LambdaHandler.handleRequest(LambdaHandler.java:41)
 at sun.reflect.GeneratedMethodAccessor127.invoke(Unknown Source)
 at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
 at java.lang.reflect.Method.invoke(Method.java:498)

"





I have `logs-insights-results.xlsx` it is having the columns are `Date	Message	 Count` Now under Message it is having the values like below
ex: "{""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Missing or Invalid Payment Currency Code\"",\""userMessage\"":\""Missing or Invalid Payment Currency Code\"",\""errorDetail\"":\""Missing or Invalid Payment Currency Code\"",\""externalErrorCode\"":null},{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Missing or Invalid Application Name\"",\""userMessage\"":\""Missing or Invalid Application Name\"",\""errorDetail\"":\""Missing or Invalid Application Name\"",\""externalErrorCode\"":null}]"",""applicationName"":""""}: com.mobiquity.millicom.commons.exception.PaymentGatewayException
com.mobiquity.millicom.commons.exception.PaymentGatewayException: {""httpStatusCode"":400,""body"":""null"",""errors"":""[{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Missing or Invalid Payment Currency Code\"",\""userMessage\"":\""Missing or Invalid Payment Currency Code\"",\""errorDetail\"":\""Missing or Invalid Payment Currency Code\"",\""externalErrorCode\"":null},{\""httpStatusCode\"":400,\""code\"":400,\""description\"":\""Missing or Invalid Application Name\"",\""userMessage\"":\""Missing or Invalid Application Name\"",\""errorDetail\"":\""Missing or Invalid Application Name\"",\""externalErrorCode\"":null}]"",""applicationName"":""""}
 at com.mobiquity.millicom.commons.wrappers.ErrorResponse.handleExceptions(ErrorResponse.java:53)
 at com.mobiquity.millicom.handler.LambdaHandler.handleRequest(LambdaHandler.java:41)
 at sun.reflect.GeneratedMethodAccessor127.invoke(Unknown Source)
 at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
 at java.lang.reflect.Method.invoke(Method.java:498)

"

the syntax would be: 

{""key"":value,....,""key"":value,""key"":""[{\""subkey\"":subkeyvalue,.....,\""subkey\"":subkeyvalue},{\""subkey\"":subkeyvalue,.....,\""subkey\"":subkeyvalue},....,{\""subkey\"":subkeyvalue,.....,\""subkey\"":subkeyvalue}]"",""key"":value,...,""key"":value}: <stack_trace>

Now i want new excel sheet called `pg_refined.xlsx` it should have columns `Date	Message	 Count  <key  key.subkey  key.subkey.subsubkey .........stack_trace>   Note under their values and make sure it won't skip any key and values and fill order wise so that under column it fill correct values and no missmatch values. So give the perfect python script


---------------------------------------

I have `pg_refined.xlsx` it is having the columns are `Date	  Message	Count	httpStatusCode	    body	errors.0.httpStatusCode 	errors.0.code	errors.0.description	errors.0.userMessage	errors.0.errorDetail	errors.0.externalErrorCode	 applicationName	errors.1.httpStatusCode	   errors.1.code	errors.1.description	errors.1.userMessage	errors.1.errorDetail	errors.1.externalErrorCode	    body.orderId	body.transactionId	body.operationPerformed	 body.paymentApproved	stack_trace`  Now i want new excel sheet name `sub_pg_refined.xlsx` it should have the all the columns in the order wise what input file is having but what columns i am giving in the terminal those should be clubbed and remaining as it is. For this ask the user in the terminal for which columns data you want to club. the clubing should be done in a order. 
ex: 
User given columns in the termianl: errors.0.httpStatusCode 	errors.0.code	errors.0.description	errors.0.userMessage	errors.0.errorDetail	errors.0.externalErrorCode   errors.1.httpStatusCode	   errors.1.code	errors.1.description	errors.1.userMessage	errors.1.errorDetail	errors.1.externalErrorCode

then, the columns would be:
`Date	  Message	Count	httpStatusCode	    body     errors.0.httpStatusCode|errors.1.httpStatusCode    errors.0.code|errors.1.code    errors.0.description|errors.1.description     errors.0.userMessage|errors.1.userMessage     errors.0.errorDetail|errors.1.errorDetail     errors.0.externalErrorCode|errors.1.externalErrorCode     applicationName     body.orderId	   body.transactionId	body.operationPerformed	 body.paymentApproved	stack_trace`  Note: pipe before 1st corresponding value and pipe after corresponding value and so on....if multipe are there. give the perfect python script.

-------
I have `./sub_pg_refined.xlsx` it is having the columns are `Date	Message	   Count	httpStatusCode	body	errors.0.httpStatusCode | errors.1.httpStatusCode	       errors.0.code | errors.1.code	    errors.0.description | errors.1.description	        errors.0.userMessage | errors.1.userMessage   	errors.0.errorDetail | errors.1.errorDetail	     errors.0.externalErrorCode | errors.1.externalErrorCode	applicationName	        body.orderId	body.transactionId	     body.operationPerformed	body.paymentApproved	stack_trace`.

Now `Date` column is optional if user gives then take otherwise no need, `Count` column not at all consider of input file. Now I want a new excel called `./pg_each_counts.xlsx` and follow the same order how i give the input columns combination and put under a sheet called `required_columns` and put the `Count` column in the end and give the `Grand Total` under `Count` column in the end of the `Count` column by calucalting all. So simply I can say ask the user in terminal for which combination of columns you want. Based on these columns give the Count from desc to asc. `Count` column in the end of that combination
ex: `Date	Message  httpStatusCode	 body .....Count`. if suppose columns with | symbol present ex: `errors.0.httpStatusCode | errors.1.httpStatusCode` then only consider the filtering since that column name is having keywords called httpStatusCode at any place.

ex: errors.0.httpStatusCode | errors.1.httpStatusCode	    errors.0.code | errors.1.code	    errors.0.description | errors.1.description	      errors.0.userMessage | errors.1.userMessage	       errors.0.errorDetail | errors.1.errorDetail	        errors.0.externalErrorCode | errors.1.externalErrorCode

500 | 400	    500 | 400	   Internal Server Error - Please try again later | Invalid Request	        Internal Server Error - Please try again later | Payment Token not found	      Internal Server Error - Please try again later | Payment Token not found	     20-09A | null

Here above example 500 comes under 5xx--> 500  under that the columns would `Date	Message	  httpStatusCode	body   errors.0.httpStatusCode  errors.0.code  errors.0.description errors.0.userMessage  errors.0.errorDetail  errors.0.externalErrorCode` under those | before values simialrly 400 for comes under 4xx--> 400  `Date	Message	  httpStatusCode	body   errors.1.httpStatusCode  errors.1.code  errors.1.description errors.1.userMessage  errors.1.errorDetail  errors.1.externalErrorCode`  above those | after values like that so on.... 

so, if under that column `errors.0.httpStatusCode | errors.1.httpStatusCode` values start with 0 then under the sheet would `0xx_counts` related,  if under that values start with 4 then under the sheet would `4xx_counts` related,if under that values start with 5 then under the sheet would `5xx_counts` related. So give the perfect python script.






