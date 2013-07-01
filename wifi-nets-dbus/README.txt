Python script, that uses DBUS and monitors for available Wi-Fi
AccessPoints in range and writes down SSIDs, Accesspoint MAC address,
encryption yes/no status (optional: supported encryption version,
WEP, WPA etc. too), to local data base.

Author: Alin Dobre <alinmd at gmail.com>

The script (or portions of it) can be used, modified and distributed
without any restrictions.

This README file contains some more information about this script, background
and how it has been coded.

Prior to starting this script I knew about DBus, how it functions, what is it
needed for, I also knew that it had a library for Python, but have never used
it. Searching the web for "dbus python" revealed the official page of the
dbus-python package usage tutorial.

After some first tryouts following the examples from the tutorial, I have
started the script by enumerating the devices from the computer. Then, I needed
help from the second documentation source, NetworkManager API, current is v0.9.
Another chunk of tryouts, since the API documentation revealed a lot of new
methods. So, I have started to test few of these methods, to make sure I'm
calling the right ones, for some of them the documentation being a little bit
light.

So, now the devices are being enumerated, the scripts exits with non-zero if no
WiFi device is being found on the system, next logical step would be to scan
for APs. Also following the NetworkManager API, found the correct method to
query for the APs and obtained the list. Getting each AP properties was just
one step ahead.

Since the script was supposed to also monitor, I have registered the AP
addition and removal signals (Googled for it, even though there was some
documentation, it was not explanatory enough) and with the help of the Glib
mainloop, now the script just waits, monitors and prints out data when an AP is
being removed or added to the list. Leaving the script for few hours to run,
revealed some bugs, which I have fixed meanwhile.

I have previously worked with SQlite databases, so the Python online help
reminded me how to use them. I have added the database initialization steps
(creating a table if it doesn't exist or reading an already existing database).
The rest of database operations were not that complex to be completed.

The optional part about displaying information about security and encryption
for each AP has been finished as the last functional step of this script, since
it was having the lowest priority. For completing this task, since I didn't
know the combination of flags that were translating into human readable forms
like WEP or WPA2, searching the Internet revealed a sample C program for
NetworkManager, URL is being specified as a comment into the script file. So,
one of the assumptions were that the script contained correct logic.

Last steps for completing the script were adding comments and regrouping some
blocks. Normally, this step is recurrent and happens more than once during the
lifetime of a script, but since this was a one time script, I have chosen to do
it at the end.

Since the code has not been tested in complex environments, it contains lots of
assumptions and uncatched code. However, since its complexity it's not high, I
expect it to run without any intervention in most environments.

Script invocation:
	python wifi-nets.py

The script will output some debug information about the steps performed:
- All SQL statements are displayed
	Example: SQL: DELETE FROM access_points WHERE id="/org/freedesktop/NetworkManager/AccessPoint/402"
- All AP properties are displayed as original data, a tuple, not formatted
	Example: ('/org/freedesktop/NetworkManager/AccessPoint/428',
		'cristinica', 'D8:5D:4C:9E:25:40', 1, 'Encrypted/WEP/WPA/WPA2, WPA: pair_ccmp,
		group_ccmp, psk, RSN: pair_ccmp, group_ccmp, psk')
- During scan, all APs are being prefixed with "AP"
	Example: AP ('/org/freedesktop/NetworkManager/AccessPoint/421',
		'cuibusoruL', '08:10:74:99:B2:4A', 1, 'Encrypted/WPA2, WPA: None, RSN:
		pair_ccmp, group_ccmp, psk')
- Each time an AP is being added to the database, it is prefixed with "AP ADD"
	Example: AP ADD: ('/org/freedesktop/NetworkManager/AccessPoint/428', ...
- Each time an AP is being removed from the database, it is prefixed with "AP REM"
	Example: AP REM: ('/org/freedesktop/NetworkManager/AccessPoint/425' ...
- Zombie APs with no properties (None) are being deleted from the database
	Example: REM EMPTY AP ('/org/freedesktop/NetworkManager/AccessPoint/377', None, None, None)

Database contains a single table called "access_points" with the following columns:
- id TEXT is the DBus path of the AP (example: /org/freedesktop/NetworkManager/AccessPoint/427)
- ssid TEXT is the SSID of the AP, as string
- hwaddr TEXT is the hardware/MAC address of the AP (example: D8:5D:4C:9E:25:40)
- enc INT is 1 if the AP supports encryption, 0 otherwise
- sec TEXT is a string containing the security features exposed by the AP
  (example: "Encrypted/WEP/WPA/WPA2, WPA: pair_ccmp, group_ccmp, psk, RSN:
  pair_ccmp, group_ccmp, psk")

Environment used to create and test the script:
- Ubuntu 12.04
- Python 2.7
