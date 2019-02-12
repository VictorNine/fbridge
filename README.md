# fbridge
fbridge bridges facebook messenger with any service supported by matterbridge trough the API interface. 

fbMatter is using [fbchat](https://github.com/carpedm20/fbchat/) to connect to facebook.

```
Requirements:
$ pip install requests
$ pip install fbchat
$ pip install toml
```
fbridge will send any message received to “dafaultgateway”. This needs to be in your matterbridge.toml file. You can then sort out the messages you want by added the threadID to config.toml

Matterbridge needs to be restarted any time you want to reconnect this client. There is some issue causing messages to be dropped if not.

I am a GO developer so there is improvements to be made to my python. Pull requests and improvement suggestions are welcome.
