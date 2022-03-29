# Telegram report system

This is the script, which can send the report in manual or automated (using CI/CD) mode. There are two scripts for different product metrics. Each script has following steps:

* Importing libraries
* Connect to telegram bot
* Connect to database
* Extract the key metrics from data
* Sending report message
* Making and sending the plots.
