# HCL DHL Hackathon Bot Overview
DHL Bot will offer assistive services like Tracking package, Shipping , Get Quote.
+ Tracking Service offers to track parcel for a user. It will inform user about incoming and outgoing package. User can enter tracking# and bot offers status of package.
+ Shipping service offers pickup and drop-off package service. Bot will ask few questions like pickup address , pickup date and time and drop-off address and drop off date and time .
+ Get Quote service offers estimated charges based on package size and distance.
+ We choose Serverless Architecture to build bot.
+ We choose AWS services to build bot because it offers
    - wide variety of services like AI, Machine Learning, Big Data, Security , Serverless, Infrastructure as a code, Devops and Voice Services  etc.
    - Pay per use .
    - Implement POC is very easy
    - Implement can achieve in days
    - Can deploy on Facebook Messenger, Slack, Tivoli and integrate with DHL website
+ We’re trying to build very basic service however, we can integrate lot of features like payments, location , insurance etc.

## HCL DHL Hackathon Bot Demo Link
[Demo Link](	https://dhl-pipeline-1oylq1kfcgpix-webappbucket-14g285dcv3ey5.s3.amazonaws.com/index.html)

## HCL DHL Hackathon Technology Stack
![Technical Stack](https://github.com/kanthedgaurav/HCL_DHL_Bot/blob/master/img/Technical%20Stack.jpg)

## HCL DHL Hackathon Architecture
##### User can starts bot by typing or speaking words like "Hi", "Hello" , "DHL" and "Hello DHL" and DhlService intents will send welcome message .
![Architecture](https://github.com/kanthedgaurav/HCL_DHL_Bot/blob/master/img/LLA.jpg)
1. When user initiate Get Quote Service , AWS Lex takes pickup city , drop off city and box type and calls lambda function "GetQuoteServiceCodeHook" . it will calculate price based on inputs.
2. When user initiate Shipping Service , AWS Lex takes pickup city , drop off city , pick up date and drop off date and calls lambda function "ShippingServiceCodeHook" .
3. ShippingService lamada function takes inputs and make entry on Dynamo Db Booking table and generate tracking id .
4. Tracking id shares with user via email using AWS SES service.
5. When user initiate Tracking Service , AWS Lex takes tracking# and calls lamada function "TrackingServiceCodeHook" .
6. "TrackingServiceCodehook" lambda function takes input and query on Dynamo Db Tracking table and if entry finds on table, it generates  json with to, from and status items . Lex takes these items and display on bot.

## HCL DHL Hackathon Wire Frames

##### Tracking

![Tracking](https://github.com/kanthedgaurav/HCL_DHL_Bot/blob/master/img/Tracking.jpg)

##### Shipping

![Shipping](https://github.com/kanthedgaurav/HCL_DHL_Bot/blob/master/img/Shipping.jpg)

##### Get Quote

![Get Quote](https://github.com/kanthedgaurav/HCL_DHL_Bot/blob/master/img/Get%20Quote.jpg)
