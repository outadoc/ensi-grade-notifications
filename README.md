ENSICAEN Grade Notifier Tool
============================

Who is this for?
----------------
This project is meant for ENSICAEN students especially, but some code could 
probably be reused if your school uses similar technologies.

What does this do?
------------------
The main Python script in this repo will fetch your most recent grades from the
ENT, download them, and notify you of any grades that were recently added, removed,
or modified.

How am I notified?
------------------
The script just calls the Maker API so that it can be integrated into IFTTT, so
you have a **large** choice of notification methods available.

How do I set it up?
-------------------
### Prerequisites

```bash
git clone git@github.com:outadoc/ensi-grade-notifications.git
```

Install the dependencies: `python3` is required.

```bash
pip3 install requests beautifulsoup4
```

### IFTTT
Create an IFTTT account and activate the Maker channel. You will be given an API
key; note it down.

Then, create three applets (or just the ones you care about). 
Here are examples using the Pushbullet channel.

- [Applet for new grades](https://ifttt.com/applets/48979252d-recevoir-une-notification-en-cas-de-nouvelle-note)
- [Applet for deleted grades](https://ifttt.com/applets/49019238d-recevoir-une-notification-en-cas-de-suppression-de-note)
- [Applet for modified grades](https://ifttt.com/applets/49019305d-recevoir-une-notification-en-cas-de-modification-d-une-note)

Here is the meaning of each parameter for each event:

| Event name          | Meaning               | Value1      | Value2         | Value3    |
|---------------------|-----------------------|-------------|----------------|-----------|
| `ent_new_grade`     | A new grade was added | Module name | Module grade   |     -     |
| `ent_deleted_grade` | A grade was removed   | Module name |        -       |     -     |
| `ent_edited_grade`  | A grade was modified  | Module name | Previous grade | New grade |

### Configuration & execution
Then, for the script to work, you will have to set the required environment
variables before executing it. The username and password are the ones you
normally use at ENSICAEN.

```bash
export ENT_USERNAME=candellier
export ENT_PASSWORD=wowthatsasupersecurepasswordlol
export MAKER_API_KEY=abcdefg1234hi_hjkl-4-z

./ent_grades_batch.py
```

You can put that in a script and have it run periodically using `cron`.
