#!/usr/bin/env python

import time
import sys
import os
import shutil
import subprocess
import email
import email.header


msg_dir="/home/alin/Downloads/Maildir"
gerrit_base_url="ssh://localgerrit"
git_cache_dir="/home/alin/Downloads/git"
repos = {
	"bitbake-devel@lists.openembedded.org": {
		"url": "git://git.openembedded.org/bitbake",
		"prj": "bitbake",
		"br": "master"
	},
	"openembedded-core@lists.openembedded.org": {
		"url": "git://git.openembedded.org/openembedded-core",
		"prj": "openembedded-core",
		"br": "master"
	},
	"poky@yoctoproject.org": {
		"url": "git://git.yoctoproject.org/poky",
		"prj": "poky",
		"br": "master"
	},
	"webhob@yoctoproject.org": {
		"url": "git://git.yoctoproject.org/webhob",
		"prj": "webhob",
		"br": "master"
	}
}

class G():
	expect_nonzero_return=False
	proc=None
	bare=None
	stdout=None
	stderr=None
	stdin=None
	ret=None

	def __init__(self, bare=None, wd=os.getcwd(), init=False):
		self.wd=wd
		print "Git working directory: %s" % self.wd
		if init:
			if bare:
				self.xw("init --bare %s"%bare)
				print self.stdout
			else:
				self.xw("init %s"%self.wd)
				print self.stdout
		self.bare=bare
		if self.bare:
			print >>sys.stderr, "Git bare repository in %s"%self.bare

	def _gitcmd(self, cmd, wd=True):
		cwd=None
		if wd:
			cwd=self.wd
		g_cmd=["git"]
		if self.bare:
			g_cmd.extend(["--git-dir", self.bare])
		if isinstance(cmd, list):
			g_cmd.extend(cmd)
		elif isinstance(cmd, str):
			scmd=cmd.split()
			if len(scmd)==1:
				g_cmd.append(cmd)
			else:
				g_cmd.extend(scmd)
		cmd_info=list(g_cmd)
		if isinstance(self.stdin, file):
			cmd_info.append("< %s" % self.stdin.name)
		print >>sys.stderr, "--$", " ".join(cmd_info)
		self.proc=subprocess.Popen(g_cmd, stdin=self.stdin, stdout=subprocess.PIPE, cwd=cwd)
		(self.stdout, self.stderr)=self.proc.communicate()
		self.ret=self.proc.returncode

	def _check(self):
		if self.ret != 0 and not self.expect_nonzero_return:
			print >>sys.stderr, "Error: Git command returned non-zero exit code (%d)" % self.ret
			sys.exit(3)

	def x(self, cmd):
		self._gitcmd(cmd, wd=True)
		self._check()

	def xw(self, cmd):
		self._gitcmd(cmd, wd=False)
		self._check()

	def xe(self, cmd):
		self._gitcmd(cmd, wd=True)

	def remote(self, remote_name, remote_url, remote_type):
		self.xe("config --get remote.%s.url"%remote_name)
		if self.stdout.strip() != remote_url and self.ret == 0:
			self.x("remote remove upstream")
		if self.ret != 0 or (self.stdout.strip() != remote_url and self.ret == 0):
			self.x("remote add --mirror=%s %s %s" % (remote_type, remote_name, remote_url))

	def clone(self, url, branch, reference, origin, checkout_dir):
		self.clone_url=url
		self.clone_branch=branch
		self.clone_reference=reference
		self.clone_origin=origin
		self.clone_dir=checkout_dir
		self.xw(["clone", url, "--branch", branch, "--reference", reference, "--origin", origin, checkout_dir])

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

git=G()
git.stdin=open(msg_quick_path)
git.x("mailinfo %s-msg %s-patch"%(msg_quick_path,msg_quick_path))
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
msg_id_file=os.path.join(msg_id_dir, "eml")

if os.path.exists(msg_id_dir):
	print >>sys.stderr, "Something went wrong, already existent msg id directory:", msg_id_dir
	sys.exit(2)

os.makedirs(msg_id_dir)
os.rename(msg_quick_path, msg_id_file)
os.rename("%s-msg"%msg_quick_path, os.path.join(msg_id_dir, "git-mailinfo-msg"))
os.rename("%s-patch"%msg_quick_path, os.path.join(msg_id_dir, "git-mailinfo-patch"))

git_cache_bare_dir=os.path.join(git_cache_dir, "bare", msg_list_id)
git=G(bare=git_cache_bare_dir, wd=git_cache_bare_dir, init=True)

git.remote("upstream", repos[msg_list_id]["url"], "fetch")
git.remote("downstream", "%s/%s" % (gerrit_base_url, repos[msg_list_id]["prj"]), "push")
git.x("fetch upstream")
git.x("push downstream")

git_cache_checkout_dir=os.path.join(git_cache_dir, "checkout", msg_list_id)
git=G(wd=git_cache_checkout_dir)
if not os.path.isdir(git_cache_checkout_dir):
	git.clone(repos[msg_list_id]["url"], repos[msg_list_id]["br"], git_cache_bare_dir, "upstream", git_cache_checkout_dir)
git.xe("config --get remote.upstream.url")
if git.stdout.strip() != repos[msg_list_id]["url"] or git.ret != 0:
	shutil.rmtree(git_cache_checkout_dir, ignore_errors=True)
	git.clone(repos[msg_list_id]["url"], repos[msg_list_id]["br"], git_cache_bare_dir, "upstream", git_cache_checkout_dir)
git.x(["checkout", "-b", "branch-%s"%msg_quick_name, "--track", "upstream/%s"%repos[msg_list_id]["br"]])
git.xe("am %s" % msg_id_file)
if git.ret != 0:
	git.x("am --abort")
else:
	git.x("push %s/%s HEAD:refs/for/%s" % (gerrit_base_url, repos[msg_list_id]["prj"], repos[msg_list_id]["br"]))
git.x("checkout upstream/%s"%repos[msg_list_id]["br"])
git.x("branch -D branch-%s"%msg_quick_name)

# remove the msg id directory
shutil.rmtree(msg_id_dir, ignore_errors=True)

