#!/usr/bin/env python
"""\
Python script, that uses DBUS and monitors for available Wi-Fi
AccessPoints's in range and writes down SSID's, Accesspoint MAC address,
encryption yes/no status (optional: supported encryption version,
WEP, WPA etc. too), to local Data Base.

Author: Alin Dobre <alinmd at gmail.com>

The script (or portions of it) can be used, modified and distributed
without any restrictions.
"""
import sys
import dbus
import dbus.mainloop.glib
import gobject
import sqlite3

# Names and paths for the DBus objects
DB_PROP_NAME='org.freedesktop.DBus.Properties'
NM_NAME='org.freedesktop.NetworkManager'
DEV_NAME='org.freedesktop.NetworkManager.Device'
WDEV_NAME='org.freedesktop.NetworkManager.Device.Wireless'
AP_NAME='org.freedesktop.NetworkManager.AccessPoint'
NM_PATH='/org/freedesktop/NetworkManager'

# WiFi device is what we care of, nothing else...
DEV_TYPE_WIFI=2

# Constants for detecting WPA and RSN security flags. Taken from NetworkManager
# 0.9 API documentation.
AP_SEC={
	0x0: ('M_802_11_AP_SEC_NONE', None),
	0x1: ('NM_802_11_AP_SEC_PAIR_WEP40', 'pair_wep40'),
	0x2: ('NM_802_11_AP_SEC_PAIR_WEP104', 'pair_wep104'),
	0x4: ('NM_802_11_AP_SEC_PAIR_TKIP', 'pair_tkip'),
	0x8: ('NM_802_11_AP_SEC_PAIR_CCMP', 'pair_ccmp'),
	0x10: ('NM_802_11_AP_SEC_GROUP_WEP40', 'group_wpe40'),
	0x20: ('NM_802_11_AP_SEC_GROUP_WEP104', 'group_wpe104'),
	0x40: ('NM_802_11_AP_SEC_GROUP_TKIP', 'group_tkip'),
	0x80: ('NM_802_11_AP_SEC_GROUP_CCMP', 'group_ccmp'),
	0x100: ('NM_802_11_AP_SEC_KEY_MGMT_PSK', 'psk'),
	0x200: ('NM_802_11_AP_SEC_KEY_MGMT_802_1X', '802.1x')
}


def db_exec(sql):
	"""\
	Print command and execute it. Used to increase logging
	"""
	print >>sys.stderr, 'SQL:', sql
	cursor.execute(sql)

def db_init():
	"""\
	Perform first tasks related to the database: creates table if not
	existent and returns elements from a previously saved database in the
	form of a dictionary where the key is the DBus path of the AP and the
	values are the rest of the AP properties
	"""
	db_exec('SELECT name FROM sqlite_master WHERE type="table";')
	tables=cursor.fetchall()
	if 'access_points' not in [table[0] for table in tables]:
		db_exec('CREATE TABLE access_points (id TEXT, ssid TEXT, hwaddr TEXT, enc INT, sec TEXT);')
	db_exec('SELECT * from access_points')
	return dict([(k[0], k[1:]) for k in cursor.fetchall()])

def db_ap_remove(ap):
	"""Removes an AP entry from the database
	"""
	db_exec('DELETE FROM access_points WHERE id="%s"' % ap)

def db_ap_add(ap, ssid, hwaddr, enc, sec):
	"""Adds an AP entry into the database
	"""
	db_exec('INSERT INTO access_points VALUES("%s", "%s", "%s", %d, "%s")' % (ap, ssid, hwaddr, enc, sec))

def db_ap_update(ap, ssid, hwaddr, enc, sec):
	"""Updates an AP entry from the database
	"""
	db_exec('UPDATE access_points SET ssid="%s", hwaddr="%s", enc=%d, sec="%s" where id="%s")' % (ssid, hwaddr, enc, sec, ap))

def enc_flags_str(flags):
	"""\
	Return the set of encryption flags, valid for both WPA and RSN values
	"""
	sec=[]
	for flag in AP_SEC:
		if flags & flag and AP_SEC[flag][1]!=None:
			sec.append(AP_SEC[flag][1])
	if not len(sec):
		sec=['None']
	return sec

def sec_flags(flags, wpaflags, rsnflags):
	"""\
	Adds the human readable encryption methods, taking into account the
	privacy, WPA and RSN flags.
	Logic from: http://ostree.gnome.org/work/src/NetworkManager/examples/C/glib/get-ap-info-libnm-glib.c
	"""
	enc=['Encrypted']
	if (not(flags & 0x1)) and (wpaflags != 0x0) and (rsnflags != 0x0):
		enc=['Not encrypted']
	if (flags & 0x1) and (wpaflags != 0x0) and (rsnflags != 0x0):
		enc.append('WEP')
	if wpaflags != 0x0:
		enc.append('WPA')
	if rsnflags != 0x0:
		enc.append('WPA2')
	if wpaflags & 0x200 or rsnflags & 0x200:
		enc.append('Enterprise')
	return '%s, WPA: %s, RSN: %s' % ('/'.join(enc), ', '.join(enc_flags_str(wpaflags)),  ', '.join(enc_flags_str(rsnflags)))

def get_ap_prop(ap):
	"""\
	Gets all the needed properties for an AP. The try/except block is for
	removed APs, which cannot be queried any longer and return error.
	"""
	try:
		ap_proxy=sysbus.get_object(NM_NAME, ap)
		ap_prop_iface=dbus.Interface(ap_proxy, DB_PROP_NAME)
		ap_ssid=''.join(map(chr, ap_prop_iface.Get(AP_NAME, 'Ssid')))
		ap_hwaddr=ap_prop_iface.Get(AP_NAME, 'HwAddress')
		ap_wpaflags=int(ap_prop_iface.Get(AP_NAME, 'WpaFlags'))
		ap_rsnflags=int(ap_prop_iface.Get(AP_NAME, 'RsnFlags'))
		ap_enc=int(ap_prop_iface.Get(AP_NAME, 'Flags'))
		ap_sec=sec_flags(ap_enc, ap_wpaflags, ap_rsnflags)
		return (str(ap), ap_ssid, str(ap_hwaddr), ap_enc, ap_sec)
	except:
		return (str(ap), None, None, None, None)

def ap_added(ap):
	"""\
	Signal method called automatically when an AP is being added, or
	manually during the initialization. It just prints some information and
	udpates the database accordingly.
	"""
	ap_prop=get_ap_prop(ap)
	print 'AP ADD:', ap_prop
	db_ap_add(*ap_prop)

def ap_removed(ap):
	"""\
	Signal method called automatically when an AP is being removed, or
	manually during the initialization. It just prints some information and
	udpates the database accordingly.
	"""
	ap_prop=get_ap_prop(ap)
	print 'AP REM:', ap_prop
	db_ap_remove(ap)


if __name__=='__main__':
	# Connect to access point database. We set isolation_level to None in
	# order to don't care about commits to database and assuming that we
	# only have one instance of this program running
	conn=sqlite3.connect('accesspoints.sqlite', isolation_level=None)
	cursor=conn.cursor()

	# Main DBus loop initialization
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	mainloop=gobject.MainLoop()

	# DBus connection
	sysbus=dbus.SystemBus()

	# The next loop enumarates all the network devices and uses the first
	# one found that is WiFi
	nm_proxy=sysbus.get_object(NM_NAME, NM_PATH)
	nm_iface=dbus.Interface(nm_proxy, NM_NAME)
	wifi_device=None
	for dev in nm_iface.GetDevices():
		dev_proxy=sysbus.get_object(NM_NAME, dev)
		dev_prop_iface=dbus.Interface(dev_proxy, DB_PROP_NAME)
		if (dev_prop_iface.Get(DEV_NAME, 'DeviceType')==DEV_TYPE_WIFI):
			wifi_device=dev
			break

	# Exit with error code 1 if no WiFi device has been found
	if not wifi_device:
		print >>sys.stderr, 'Error: No usable WiFi device found'
		sys.exit(1)

	# Load APs that have been saved in the database from the previous
	# scripts run
	print 'Loading previous APs from database'
	aps=db_init()


	# Start scanning for access points
	print 'Scanning for APs'
	# aps_scan is only used to determine which APs are no longer alive,
	# from the ones in the database
	aps_scan=[]
	wifi_proxy=sysbus.get_object(NM_NAME, wifi_device)
	for ap in wifi_proxy.GetAccessPoints(dbus_interface=WDEV_NAME):
		ap_prop=get_ap_prop(ap)
		print 'AP', ap_prop
		# If the AP appears in the list, but has no properties, we will
		# remove it from our database
		if ap_prop[1:] == (None, None, None):
			print 'REM EMPTY AP', ap_prop
			ap_removed(ap)
			continue
		aps_scan.append(ap)
		if not ap in dict(aps): # add if not existent
			db_ap_add(*ap_prop)
			aps[ap]=ap_prop[1:]
		elif aps[ap] != ap_prop[1:]: # update if not current
			db_ap_update(*ap_prop)
			aps[ap]=ap_prop[1:]

	# Cleanup by enumarating all APs from the database that were not
	# detected in the scan session above
	print 'Cleaning up database for non-existing APs'
	for ap in list(aps):
		if ap not in aps_scan:
			ap_removed(ap)

	# Both aps_scan and aps are no longer needed. Removing them here to
	# avoid future confusions
	del aps_scan
	del aps

	# Register the ap_added and ap_removed calls (defined above) for
	# situation when an AP is being added or removed in the main loop
	wifi_proxy.connect_to_signal('AccessPointAdded', ap_added, dbus_interface=WDEV_NAME)
	wifi_proxy.connect_to_signal('AccessPointRemoved', ap_removed, dbus_interface=WDEV_NAME)

	# Aaaand, we're done. Now only exceptions can get us out of this loop
	print "Entering main loop to monitor AP changes"
	mainloop.run()

