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
			self.x("remote remove %s"%remote_name)
		if self.ret != 0 or (self.stdout.strip() != remote_url and self.ret == 0):
			self.x("remote add --mirror=%s %s %s" % (remote_type, remote_name, remote_url))

	def clone(self, url, branch, reference, origin, checkout_dir):
		self.clone_url=url
		self.clone_branch=branch
		self.clone_reference=reference
		self.clone_origin=origin
		self.clone_dir=checkout_dir
		self.xw(["clone", url, "--branch", branch, "--reference", reference, "--origin", origin, checkout_dir])

class M():
	def __init__(self, msg_dir):
		self.id="%.2f"%time.time()
		self.msg_dir=msg_dir
		self.quick_name="%s.eml"%self.id
		self.quick_path=os.path.join(self.msg_dir, self.quick_name)
		self.msg=str()
		self.msg_refs=list()

		self._get_stdin()
		if len(self.msg)==0:
			print >>sys.stderr, "Refusing to create empty files"
			os.remove(self.quick_path)
			sys.exit(1)

		if not self._get_mailinfo():
			print >>sys.stderr, "Message doesn't contain a patch."
			sys.exit(0)

		self._get_email_properties()

		if self.msg_list_id == None:
			print >>sys.stderr, "Could not determine list ID. Giving up..."
			sys.exit(4)

	def _get_stdin(self):
		if not os.path.isdir(self.msg_dir):
			os.makedirs(self.msg_dir)
		msg_file=open(self.quick_path, "w")
		while True:
			buf=sys.stdin.read()
			if len(buf)==0:
				break
			self.msg+=buf
			msg_file.write(buf)
		msg_file.close()

	def _get_mailinfo(self):
		git=G()
		git.stdin=open(self.quick_path)
		git.x("mailinfo %s-msg %s-patch"%(self.quick_path,self.quick_path))
		if os.stat("%s-patch"%self.quick_path).st_size == 0:
			os.remove(self.quick_path)
			os.remove("%s-msg"%self.quick_path)
			os.remove("%s-patch"%self.quick_path)
			return False
		return True

	def _get_email_properties(self):
		msg = email.message_from_string(self.msg)
		self.msg_subj="".join([x[0] for x in email.header.decode_header(msg["subject"])])
		if msg["references"] != None:
			self.msg_refs=[x.strip("<>") for x in msg["references"].split()]
		self.msg_id=msg["message-id"].strip("<>")
		self.msg_list_id=msg["X-BeenThere"]

	def move_msg_id(self):
		self.msg_id_dir=os.path.join(self.msg_dir, self.msg_list_id, self.msg_id)
		self.msg_id_file=os.path.join(self.msg_id_dir, "eml")

		if os.path.exists(self.msg_id_dir):
			print >>sys.stderr, "Something went wrong, already existent msg id directory:", self.msg_id_dir
			sys.exit(2)

		os.makedirs(self.msg_id_dir)
		os.rename(self.quick_path, self.msg_id_file)
		os.rename("%s-msg"%self.quick_path, os.path.join(self.msg_id_dir, "git-mailinfo-msg"))
		os.rename("%s-patch"%self.quick_path, os.path.join(self.msg_id_dir, "git-mailinfo-patch"))

	def remove_msg_id(self):
		# remove the msg id directory
		shutil.rmtree(self.msg_id_dir, ignore_errors=True)

if __name__=="__main__":
	m=M(msg_dir)
	m.move_msg_id()

	git_cache_bare_dir=os.path.join(git_cache_dir, "bare", m.msg_list_id)
	git=G(bare=git_cache_bare_dir, wd=git_cache_bare_dir, init=True)

	git.remote("upstream", repos[m.msg_list_id]["url"], "fetch")
	git.remote("downstream", "%s/%s" % (gerrit_base_url, repos[m.msg_list_id]["prj"]), "push")
	git.x("fetch upstream")
	git.x("push downstream")

	git_cache_checkout_dir=os.path.join(git_cache_dir, "checkout", m.msg_list_id)
	git=G(wd=git_cache_checkout_dir)
	if not os.path.isdir(git_cache_checkout_dir):
		git.clone(repos[m.msg_list_id]["url"], repos[m.msg_list_id]["br"], git_cache_bare_dir, "upstream", git_cache_checkout_dir)
	git.xe("config --get remote.upstream.url")
	if git.stdout.strip() != repos[m.msg_list_id]["url"] or git.ret != 0:
		shutil.rmtree(git_cache_checkout_dir, ignore_errors=True)
		git.clone(repos[m.msg_list_id]["url"], repos[m.msg_list_id]["br"], git_cache_bare_dir, "upstream", git_cache_checkout_dir)
	git.x(["checkout", "-b", "branch-%s"%m.quick_name, "--track", "upstream/%s"%repos[m.msg_list_id]["br"]])
	git.xe("am %s" % m.msg_id_file)
	if git.ret != 0:
		git.x("am --abort")
	else:
		git.x("push %s/%s HEAD:refs/for/%s" % (gerrit_base_url, repos[m.msg_list_id]["prj"], repos[m.msg_list_id]["br"]))
	git.x("checkout upstream/%s"%repos[m.msg_list_id]["br"])
	git.x("branch -D branch-%s"%m.quick_name)

	m.remove_msg_id()

