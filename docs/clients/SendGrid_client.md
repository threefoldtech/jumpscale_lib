## Send Grid Client

This library enables the user to send an email using sendgrid API
```
j.clients.sendgrid
```

## How to use it
 - Prepare API Key of sendgrid, this may be done by two ways
    - create environment variable called "SENDGRID_API_KEY" holding the api key value from sendgrid
    - get the api key value and pass it to the function
 - Prepare paramters required for the function
    ```python
        SENDER = "sender_email@example.com"
        RECIPENT = "recipent_email@example.com"
        SUBJECT = "This is my email subject"
        MESSAGE_TYPE = "text/plain"
        MESSAGE = "This is my email body"
    ```

 - call send function with your data while passing api key through environment variable
    ```
        send(SENDER, RECIPENT, SUBJECT, MESSAGE_TYPE, MESSAGE)
    ```
 - call send function with API key
    ```
        API_KEY="This is the value of my API KEY"
        send(SENDER, RECIPENT, SUBJECT, MESSAGE_TYPE, MESSAGE, API_KEY)
    ```
```
!!!
date = "2018-05-20"
tags = []
title = "SendGrid Client"
```

