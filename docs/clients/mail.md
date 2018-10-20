# mail client

This client can be used to send emails from the specified smtp server.

Using [config manager](https://github.com/Jumpscale/core/blob/master/docs/config/configmanager.md), user needs to specify the following data:

- smtp_server: server address
- smtp_port: server port
- login: user login to the smtp server
- password: password login to the smtp server
- from: sender name

## Usage

```
j.clients.email.send(self, recipients, sender, subject, message, files=None, mimetype=None)
Docstring:
@param recipients: Recipients of the message
@type recipients: mixed, string or list
@param sender: Sender of the email
@type sender: string
@param subject: Subject of the email
@type subject: string
@param message: Body of the email
@type message: string
@param files: List of paths to files to attach
@type files: list of strings
@param mimetype: Type of the body plain, html or None for autodetection
@type mimetype: string
```

## Example

```
j.clients.email.send("kristof@incubaid.com","kristof@incubaid.com","test","test")
```

```
!!!
title = "How To Send Mail"
date = "2017-04-08"
tags = ["howto"]
```

