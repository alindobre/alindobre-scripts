#!/usr/bin/env python


msg_dir="/home/alin/Downloads/Maildir"
gerrit_base_url="ssh://localgerrit"
git_cache_dir="/home/alin/Downloads/git"
repos = {
	"bitbake-devel@lists.openembedded.org": {
		"url": "git://git.openembedded.org/bitbake",
		"prj": "bitbake",
		"br": "devel"
	},
	"openembedded-core@lists.openembedded.org": {
		"url": "git://git.openembedded.org/openembedded-core",
		"prj": "openembedded-core",
		"br": "devel"
	},
	"poky@yoctoproject.org": {
		"url": "git://git.yoctoproject.org/poky",
		"prj": "poky",
		"br": "devel"
	},
	"webhob@yoctoproject.org": {
		"url": "git://git.yoctoproject.org/webhob",
		"prj": "webhob",
		"br": "devel"
	}
}

import time
import sys
import os

msg_quick_name="%.2f.eml"%time.time()
msg_quick_path=os.path.join(msg_dir, msg_quick_name)
if not os.path.isdir(msg_dir):
	os.makedirs(msg_dir)

msg_file=open(msg_quick_path, "w")
msg_str=str()
while True:
	buf=sys.stdin.read()
	if len(buf)==0:
		break
	msg_str+=buf
	msg_file.write(buf)
msg_file.close()
if len(msg_str)==0:
	print >>sys.stderr, "Refusing to create empty files"
	os.remove(msg_quick_path)
	sys.exit(1)

def git_cmd(cmd, stdin=None):
	"""\
	Executes a git command and returns the result and displays error information,
	if case. The function returns a tuple (return code, command stdout, command stderr).
	"""
	# We are using the subprocess.Popen() class to run the command, because it's
	# highly backwards compatible with Python 2.6 and onwards.
	clean_exit=False
	cmd_info=list(cmd)
	if isinstance(stdin, file):
		cmd_info.append("< %s" % stdin.name)
	#print >>sys.stderr, " ".join(cmd_info)

	pgit=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=stdin)

	# To be able to get the command's return code, we have to call the wait()
	# method and wait for the program execution to finish.
	pgit.wait()
	git_stdout=pgit.stdout.readlines()
	git_stderr=pgit.stderr.readlines()

	if pgit.returncode == 0:
		clean_exit=True
	else:
		print >>sys.stderr, "Error: Git command returned non-zero exit code (%d)" % pgit.returncode
		sys.stderr.write("".join(git_stderr))
	if not clean_exit:
		print >>sys.stderr, "Could not run git command. Giving up."
		sys.exit(3)

	return (pgit.returncode, git_stdout, git_stderr)

import subprocess
import email
import email.header

git_cmd(["git", "mailinfo", "%s-msg"%msg_quick_path, "%s-patch"%msg_quick_path], open(msg_quick_path))
if os.stat("%s-patch"%msg_quick_path).st_size == 0:
	os.remove(msg_quick_path)
	os.remove("%s-msg"%msg_quick_path)
	os.remove("%s-patch"%msg_quick_path)
	print >>sys.stderr, "Message doesn't contain a patch."
	sys.exit(0)

msg = email.message_from_string(msg_str)
msg_subj="".join([x[0] for x in email.header.decode_header(msg["subject"])])
msg_refs=list()
if msg["references"] != None:
	msg_refs=[x.strip("<>") for x in msg["references"].split()]
msg_id=msg["message-id"].strip("<>")
msg_list_id=msg["X-BeenThere"]
if msg_list_id==None and len(sys.argv)>1:
	msg_list_id=sys.argv[1]

if msg_list_id == None:
	print >>sys.stderr, "Could not determine list ID. Giving up..."
	sys.exit(4)

msg_id_dir=os.path.join(msg_dir, msg_list_id, msg_id)
#msg_id_file=os.path.join(msg_id_dir, "msg-%s"%msg_quick_name)
msg_id_file=os.path.join(msg_id_dir, "eml")

if os.path.exists(msg_id_dir):
	print >>sys.stderr, "Something went wrong, there shouldn't be an already existent msg id directory"
	sys.exit(2)

os.makedirs(msg_id_dir)
os.rename(msg_quick_path, msg_id_file)
os.rename("%s-msg"%msg_quick_path, os.path.join(msg_id_dir, "git-mailinfo-msg"))
os.rename("%s-patch"%msg_quick_path, os.path.join(msg_id_dir, "git-mailinfo-patch"))

# git remote add --mirror=fetch upstream "git://git.openembedded.org/openembedded-core"
# git remote add --mirror=push downstream ssh://localgerrit/openembedded-core
# git fetch upstream
# git push downstream
git_cache_bare_dir=os.path.join(git_cache_dir, "bare", msg_list_id)
(ret, us_out, serr) = git_cmd(["git", "init", "--bare", git_cache_bare_dir])
print "".join(us_out)
(ret, us_out, serr) = git_cmd(["git", "--git-dir", git_cache_bare_dir, "remote", "add", "--mirror=fetch", "upstream", repos[msg_list_id]["url"]])
print "".join(us_out)
(ret, us_out, serr) = git_cmd(["git", "--git-dir", git_cache_bare_dir, "remote", "add", "--mirror=push", "downstream", "%s/%s" % (gerrit_base_url, repos[msg_list_id]["prj"])])
print "".join(us_out)
(ret, us_out, serr) = git_cmd(["git", "--git-dir", git_cache_bare_dir, "fetch", "upstream"])
print "".join(us_out)
(ret, us_out, serr) = git_cmd(["git", "--git-dir", git_cache_bare_dir, "push", "downstream"])
print "".join(us_out)
#(ret, us_out, serr) = git_cmd(["git", "ls-remote", repos[msg_list_id]["url"]])
#(ret, ds_out, serr) = git_cmd(["git", "ls-remote", "%s/%s" % (gerrit_base_url, repos[msg_list_id]["prj"])])

"""
for ref in msg_refs:
	print >>sys.stderr, "Processing reference: %s" % ref
	if os.path.isdir(os.path.join(msg_dir, msg_list_id, ref)):
		print >>sys.stderr, "%s -> %s" % (msg_id_file, os.path.join(msg_dir, msg_list_id, ref, "ref-%s"%msg_id))
		os.symlink(msg_id_file, os.path.join(msg_dir, msg_list_id, ref, "ref-%s"%msg_id))
	else:
		print >>sys.stderr, "Reference msg id doesn't exist: %s" % ref
"""
