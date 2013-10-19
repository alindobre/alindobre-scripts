#! /usr/bin/env python
"""
Lists or deletes the accounts that have not logged since a number of days

Author: Alin Dobre
Copyright (c) since 2007, GECAD Technologies. All rights reserved.
For feedback and/or bugs in this script, please send an e-mail to:
  "AXIGEN Team" <team@axigen.com>
"""
_CVSID='$Id: last-login.py,v 1.3 2009/04/15 07:52:33 alin Exp $'
if __name__=='__main__':
  import sys, time;
  try:
    import cli2;
  except ImportError:
    print >>sys.stderr, 'ERROR: AXIGEN CLI Module could not be imported.';
    print >>sys.stderr, 'Please place cli2.py in one of the following directories:';
    for x in sys.path:
      print >>sys.stderr, '-',x
    sys.exit(1);

  def ilog(fd, message):
    print >>sys.stdout, message;
    if fd:
      print >>fd, message;
      fd.flush();

  def elog(fd, message):
    print >>sys.stderr, message;
    if fd:
      print >>fd, message;
      fd.flush();

  def show_help():
    global noDays, action, cliHost, cliPort
    print >>sys.stderr, """
Basic usage:
  %s [days=<no of days>] [action=list|delete] [domain=<domain>] \\
    [host=<cli host>] [port=<cli port>] [pass=<admin password>] \\
    [debug=<debug level>] [log=<log file>]

  Where, each parameter is:
  days - number of days in the past (default: %s)
  action - list|delete (default: %s)
  domain - domain to search in. if not specified will search in all domains
  log - the filename that the script will log into
  host - CLI host to connect to (default: %s)
  port - CLI port to connect ro (default: %s)
  pass - if specified, will use this password, otherwise will ask for one
  debug - if set to 1 will display all the protocol communication over CLI
  
  """ % ((sys.argv[0]), noDays, action, cliHost, cliPort);

  #defaults
  noDays='100';
  domain=None;
  action='list';
  logFile=None;
  cliHost='127.0.0.1';
  cliPort='7000';
  cliPass=None;
  cliDebug=None;

  for param in sys.argv[1:]:
    if param.startswith('days='):
      noDays=param[5:];
      continue;
    if param.startswith('log='):
      logFile=param[4:];
      continue;
    if param.startswith('action='):
      action=param[7:];
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
    if param.startswith('domain='):
      domain=param[7:];
      continue;
    if param=='help' or param=='--help' or param=='-h':
      show_help();
      sys.exit();
  try:
    fdlog=open(logFile, 'a');
  except:
    if logFile!=None:
      elog(fdlog, "Warning: Could not open log file (%s), or none specified" % logFile);
    fdlog=None;
  ilog(fdlog, '');
  ilog(fdlog, '******** Script started at: %s ***********' % time.ctime(time.time()));
  if not cliPort.isdigit():
    elog(fdlog, "ERROR: CLI port must be a number");
    sys.exit(1);
  if not noDays.isdigit():
    elog(fdlog, "ERROR: Days must be a number");
    sys.exit(1);
  if action!='list' and action!='delete':
    elog(fdlog, "ERROR: Action must be one of 'list' or 'delete'");
    sys.exit(1);
  noDays=int(noDays);
  cliPort=int(cliPort);
  c=cli2.CLI(cliHost, cliPort);
  thenDate=time.time()-noDays*86400;
  sd='all domains';
  if domain:
    sd=domain;
  ilog(fdlog, '** Last login date before: %s (%s days)' % (time.ctime(thenDate), noDays));
  ilog(fdlog, '** CLI Host/Port: %s:%d' % (cliHost, cliPort));
  ilog(fdlog, '** Action to matched accounts: %s' % action);
  ilog(fdlog, '** Domains to search in: %s' % sd);
  ilog(fdlog, '-----------------------------------------------');
  if not cliPass:
    import getpass;
    while not cliPass:
      cliPass=getpass.getpass('Enter CLI Admin password: ');
      if not cliPass:
        print >>sys.stderr, 'Empty passwords are not allowed!';
  if cliDebug=="1":
    cli2.CLI.debug=1;
  c.auth(cliPass, "admin");
  domains=c.get_domains();
  if domain:
    domains=[domain];
  for domain in domains:
    if c.context=='domain':
      c.back();
    try:
      c.update_domain(domain);
    except:
      elog(fdlog, 'ERROR: Cannot enter domain', domain);
      continue;
    accounts=c.get_accounts();
    for account in accounts:
      if c.context=='domain-account':
        c.back();
      try:
        c.update_account(account);
      except:
        elog(fdlog, 'ERROR: Cannot enter account %s@%s' % (account, domain));
        continue;
      reg=c.get_show_registry();
      llc=' '.join(reg["Creation Date"].split()[:-1]);      
      llp=' '.join(reg["POP3 Last Login Date"].split()[:-1]);
      lli=' '.join(reg["IMAP Last Login Date"].split()[:-1]);
      llw=' '.join(reg["WebMail Last Login Date"].split()[:-1]);
      last_login=max(
        cli2.strtime2epoch(llc),
        cli2.strtime2epoch(llp),
        cli2.strtime2epoch(lli),
        cli2.strtime2epoch(llw)
      );
      c.back();
      if last_login<thenDate:
        if action=='list':
          ilog(fdlog, '>> %s@%s - Last login: %s' % (account, domain, time.ctime(last_login)));
        if action=='delete':
          try:
            c.del_account(account);
            ilog(fdlog, '>> Success deleting account %s@%s (Last login: %s)' % (account, domain, time.ctime(last_login)));
          except:
            elog(fdlog, '!! Error deleting account %s@%s (Last login: %s)' % (account, domain, time.ctime(last_login)));
  if fdlog:
    fdlog.close();
