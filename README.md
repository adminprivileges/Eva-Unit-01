# Eva-Unit-01
A bot i made for work
![Eva Unit-01 cryostasis](https://assets3.thrillist.com/v1/image/2828794/792x536/scale;jpeg_quality=60;progressive.jpg)
## Funtion
Currently the bot can do the following
- Keep track of muster embedding personel status in nested lists and ultimately CSV files which emails the appropriate parties at a set time
- Scrapes the Official navy page for the most updated NAVADMINS

***Note email function will not work until you register [a gmail application](https://developers.google.com/gmail/api/quickstart/python/)*** 
also make sure to go the following to initialize your ezgmail instance, if you choose desktop application when you register your app, do this step on your desktop machine and move the initialization token to your server's folder along with your credentials.json file
```
import ezgmail, os
os.chdir(r'C:\path\to\credentials_json_file')
ezgmail.init()
```
This book helped me with the email part https://learning.oreilly.com/library/view/automate-the-boring/9781098122584/xhtml/ch18.xhtml#ch18lev1sec3
