#! /usr/bin/env python
"""
Script that uses the CLI module to display all accounts within a domain, a list
of domains, or all domains.
"""
"""
Author: Alin Dobre
Copyright (c) since 2007, GECAD Technologies. All rights reserved.
For feedback and/or bugs in this script, please send an e-mail to:
  "AXIGEN Team" <team@axigen.com>
"""
_CVSID='$Id: list-accounts.py,v 1.3 2010/05/12 11:27:26 alin Exp $'
if __name__=='__main__':
  import sys;
  try:
    import cli2;
  except ImportError:
    print >>sys.stderr, 'ERROR: AXIGEN CLI Module could not be imported.';
    print >>sys.stderr, 'Please place cli2.py in one of the following directories:';
    for x in sys.path:
      print >>sys.stderr, '-',x
    sys.exit(1);

  def show_help():
    print >>sys.stderr, """
Basic usage:
  %s file=<accounts file> [host=<cli host>] \\
    [port=<cli port>] [debug=<debug level>] \\
    [pass=<admin password>] [domains=domain1[,domain2[,...]]]

  Where, each parameter is:
  file     - the filename to which the account names will saved, one per line
  host     - CLI host to connect to; default: localhost
  port     - CLI port to connect ro; default: 7000
  debug    - if set to 1 will display all the protocol communication over CLI
  pass     - if specified, will use this password, otherwise will ask for one
  domains  - specifies the domain or list of domains for which to query for
            accounts
  names    - will also list the firstName and lastName account attributes;
            default: 0 (true means anything other than 0)
  aliases  - will also list the aliases for each account
  registry - if equal to 1 will enable retrieval of attributes from the "SHOW REGISTRYINFORMATION" command as follows:
             	id   - Internal ID
        	cd   - Creation Date
      		md   - Modification Date
      		plld - POP3 Last Login Date
      		plli - POP3 Last Login IP
      		illd - IMAP Last Login Date
      		illi - IMAP Last Login IP
      		wlld - WebMail Last Login Date
      		wlli - WebMail Last Login IP
      		imc  - Internal Mbox Container ID
      		cv   - Configuration Version
      		msv  - Mbox Storage Version
      		ali  - Associated LDAP ID
      		ald  - Associated LDAP DN
      		cs   - Configuration Status
      		ms   - Mbox size
      		msc  - Mbox message count
      		mfc  - Mbox folder count
      		mss  - Mbox Storage Status

  Examples of usage
  - save all accounts from all domains:
    %s file=myaccounts.txt host=192.168.102.24 port=7001

  - save Creation Date, Mbox size and IMAP Last Login Date:
    %s file=myaccounts.txt registry=1 cd=1 ms=1 illd=1

  - save accounts from example1.org and example2.org domains with first and
    last names:
    %s file=a1.txt domains=example1.org,example2.org names=1
  """ % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0]);

  #defaults
  acctFile=None;
  cliHost=None;
  cliPort=None;
  cliPass=None;
  cliDebug=None;
  domainsList=None;
  listNames="0";
  listAliases="0";
  listRegistry="0";
  listid="0";
  listcd="0";
  listmd="0";
  listplld="0";
  listplli="0"; #POP3 Last Login IP
  listilld="0"; #IMAP Last Login Date
  listilli="0"; #IMAP Last Login IP
  listwlld="0"; #WebMail Last Login Date
  listwlli="0"; #WebMail Last Login IP
  listimc="0"; #Internal Mbox Container ID
  listcv="0"; #Configuration Version
  listmsv="0"; #Mbox Storage Version
  listali="0"; #Associated LDAP ID
  listald="0"; #Associated LDAP DN
  listcs="0"; #Configuration Status
  listms="0"; #Mbox size
  listmsc="0"; #Mbox message count
  listmfc="0"; #Mbox folder count
  listmss="0"; #Mbox Storage Status

  
  
  
  
  
  for param in sys.argv[1:]:
    if param.startswith('file='):
      acctFile=param[5:];
      continue;
    if param.startswith('host='):
      cliHost=param[5:];
      continue;
    if param.startswith('port='):
      cliPort=param[5:];
      continue;
    if param.startswith('pass='):
      cliPass=param[5:];
      continue;
    if param.startswith('debug='):
      cliDebug=param[6:];
      continue;
    if param.startswith('domains='):
      domainsList=param[8:];
      continue;
    if param.startswith('names='):
      listNames=param[6:];
      continue;
    if param.startswith('aliases='):
      listAliases=param[7:];
      continue;
    if param.startswith('registry='):
      listRegistry=param[8:];
      continue; 
    if param.startswith('id='):
      listid=param[9:];
      continue;
    if param.startswith('cd='):
      listcd=param[10:];
      continue;
    if param.startswith('md='):
      listmd=param[11:];
      continue;
    if param.startswith('plld='):
      listplld=param[12:];
      continue;
    if param.startswith('plli='):
      listplli=param[13:];
      continue;
    if param.startswith('illd='):
      listilld=param[14:];
      continue;
    if param.startswith('illi='):
      listilli=param[15:];
      continue;
    if param.startswith('wlld='):
      listwlld=param[16:];
      continue;
    if param.startswith('wlli='):
      listwlli=param[17:];
      continue;
    if param.startswith('imc='):
      listimc=param[18:];
      continue;
    if param.startswith('cv='):
      listcv=param[19:];
      continue;
    if param.startswith('msv='):
      listmsv=param[20:];
      continue;
    if param.startswith('ali='):
      listali=param[21:];
      continue;
    if param.startswith('ald='):
      listald=param[22:];
      continue;
    if param.startswith('cs='):
      listcs=param[23:];
      continue;
    if param.startswith('ms='):
      listms=param[24:];
      continue;
    if param.startswith('msc='):
      listmsc=param[25:];
      continue;
    if param.startswith('mfc='):
      listmfc=param[26:];
      continue;
    if param.startswith('mss='):
      listmss=param[27:];
      continue;

  if listNames!="0":
    listNames=True;
  else:
    listNames=False;
  if listAliases!="0":
    listAliases=True;
  else:
    listAliases=False;
  if listRegistry!="0":
    listRegistry=True;
  else:
    listRegistry=False;
  if listid!="0":
    listid=True;
  else:
    listid=False;
  if listcd!="0":
    listcd=True;
  else:
    listcd=False;
  if listmd!="0":
    listmd=True;
  else:
    listmd=False;
  if listplld!="0":
    listplld=True;
  else:
    listplld=False;
  if listplli!="0":
    listplli=True;
  else:
    listplli=False;
  if listilld!="0":
    listilld=True;
  else:
    listilld=False;
  if listilli!="0":
    listilli=True;
  else:
    listilli=False;
  if listwlld!="0":
    listwlld=True;
  else:
    listwlld=False;
  if listwlli!="0":
    listwlli=True;
  else:
    listwlli=False;
  if listimc!="0":
    listimc=True;
  else:
    listimc=False;
  if listcv!="0":
    listcv=True;
  else:
    listcv=False;
  if listmsv!="0":
    listmsv=True;
  else:
    listmsv=False;
  if listali!="0":
    listali=True;
  else:
    listali=False;
  if listald!="0":
    listald=True;
  else:
    listald=False;
  if listcs!="0":
    listcs=True;
  else:
    listcs=False;
  if listms!="0":
    listms=True;
  else:
    listms=False;
  if listmsc!="0":
    listmsc=True;
  else:
    listmsc=False;
  if listmfc!="0":
    listmfc=True;
  else:
    listmfc=False;
  if listmss!="0":
    listmss=True;
  else:
    listmss=False;


  if cliHost==None:
    cliHost="127.0.0.1";
  if cliPort==None:
    cliPort="7000";
  if not cliPort.isdigit():
    print >>sys.stderr, "Port must be a number";
    sys.exit(1);
  cliPort=int(cliPort);
  if not acctFile:
    print >>sys.stderr, "Accounts file not specified";
    show_help();
    sys.exit(1);
  fd=open(acctFile, 'w');
  c=cli2.CLI(cliHost, cliPort);
  if not cliPass:
    import getpass;
    while not cliPass:
      cliPass=getpass.getpass('Enter CLI Admin password: ');
      if not cliPass:
        print >>sys.stderr, 'Empty passwords are not allowed!';
  if cliDebug=="1":
    cli2.CLI.debug=1;
  c.auth(cliPass, "admin");

  if not domainsList:
    myDomainsList=c.getDomainsList();
  else:
    myDomainsList=domainsList.split(',');
  for myDomain in myDomainsList:
    if not myDomain: # empty domain
      continue;
    for myAccount in c.getAccountsList(myDomain):
      myAliasStr='';
      id=''; #Internal ID
      cd=''; #Creation Date
      md=''; #Modification Date
      plld=''; #POP3 Last Login Date
      plli=''; #POP3 Last Login IP
      illd=''; #IMAP Last Login Date 
      illi=''; #IMAP Last Login IP
      wlld=''; #WebMail Last Login Date
      wlli=''; #WebMail Last Login IP
      imc=''; #Internal Mbox Container ID
      cv=''; #Configuration Version
      msv=''; #Mbox Storage Version
      ali=''; #Associated LDAP ID
      ald=''; #Associated LDAP DN
      cs=''; #Configuration Status
      ms=''; #Mbox size
      msc=''; #Mbox message count
      mfc=''; #Mbox folder count
      mss=''; #Mbox Storage Status
      infoStr='';
      if listNames:
        myInfo=c.getAccountData(myAccount, myDomain);
        infoStr='\t%s\t%s' % (myInfo['firstName'], myInfo['lastName']);
      if listAliases:
        myAlias=c.getAccountAliases(myAccount, myDomain);
	myAliasStr='\t%s' % myAlias;
      if listRegistry:
        myRegistry=c.getAccountRegistry(myAccount, myDomain);
        if listid:
	  id='\n\tInternal ID: %s' % myRegistry['Internal ID'];
        if listcd:
	  cd='\n\tCreation Date: %s' % myRegistry['Creation Date'];
        if listmd:
	  md='\n\tModification Date: %s' % myRegistry['Modification Date'];
        if listplld:
	  plld='\n\tPOP3 Last Login Date: %s' % myRegistry['POP3 Last Login Date'];
        if listplli:
	  plli='\n\tPOP3 Last Login IP: %s' % myRegistry['POP3 Last Login IP'];
        if listilld:
	  illd='\n\tIMAP Last Login Date: %s' % myRegistry['IMAP Last Login Date'];
        if listilli:
	  illi='\n\tIMAP Last Login IP: %s' % myRegistry['IMAP Last Login IP'];
        if listwlld:
	  wlld='\n\tWebMail Last Login Date: %s' % myRegistry['WebMail Last Login Date'];
        if listwlli:
	  wlli='\n\tWebMail Last Login IP: %s' % myRegistry['WebMail Last Login IP'];
        if listimc:
	  imc='\n\tInternal Mbox Container ID: %s' % myRegistry['Internal Mbox Container ID'];
        if listcv:
	  cv='\n\tConfiguration Version: %s' % myRegistry['Configuration Version'];
        if listmsv:
	  msv='\n\tMbox Storage Version: %s' % myRegistry['Mbox Storage Version'];
        if listali:
	  ali='\n\tAssociated LDAP ID: %s' % myRegistry['Associated LDAP ID'];
        if listald:
	  ald='\n\tAssociated LDAP DN: %s' % myRegistry['Associated LDAP DN'];
        if listcs:
	  cs='\n\tConfiguration Status: %s' % myRegistry['Configuration Status'];
        if listms:
	  ms='\n\tMbox size: %s' % myRegistry['Mbox size'];
        if listmsc:
	  msc='\n\tMbox message count: %s' % myRegistry['Mbox message count'];
        if listmfc:
	  mfc='\n\tMbox folder count: %s' % myRegistry['Mbox folder count'];
        if listmss:
	  mss='\n\tMbox Storage Status: %s' % myRegistry['Mbox Storage Status'];
      print >>fd, "%s@%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s" % (myAccount, myDomain, infoStr, myAliasStr, id, cd, md, plld, plli, illd, illi, wlld, wlli, imc, cv, msv, ali, ald, cs, ms, msc, mfc, mss);
  fd.close();
