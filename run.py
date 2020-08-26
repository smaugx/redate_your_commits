#!/usr/bin/env python
#-*- coding:utf8 -*-


import os
import sys
import time
import requests
from datetime import datetime
import pytz
import tzlocal
import json
from git.repo import Repo
from git.repo.fun import is_git_dir

year_holiday = {}

def workdaytime_check(timestamp):
    """
    Check date(format: 2020-01-2 13:00:30 +0800) is workdaytime or not, using
    public api:http://timor.tech/api/holiday/year/{year}/, thanks to the author.
    workday meaning date is weekday and reset-day of weekend,
    and workdaytime meaning workday from 9:00 to 19:00.
    if date is workdaytime, than return a new date(not workdaytime), usually same day but hour after 22.
    
    :param timestamp: int
        unix timestamp
    :return: None or new_date(string)
    :note:
        if workdaytime_check true, then return a new_date, otherwise return None
    """

    global year_holiday
    # datetime.datetime(2017, 11, 6, 15, 23, 20, tzinfo=<DstTzInfo 'Asia/Shanghai' CST+8:00:00 STD>)
    dt = datetime.fromtimestamp(timestamp, tz=tzlocal.get_localzone())
    # '2017-11-06 15:23:20+08:00'
    dt_str = '{0}'.format(dt.astimezone(tzlocal.get_localzone()))

    year = dt.year
    month = dt.month
    day = dt.day
    weekday = dt.weekday() + 1 # attention: weekday 0 is monday
    hour = dt.hour
    minute = dt.minute
    second = dt.second

    if hour < 9 or hour >= 19:
        # not working time
        return None

    new_hour   = 22
    new_minute = 60 - (22 - hour) * 3 
    new_second = minute
    new_date = datetime(year, month, day, new_hour, new_minute, new_second, tzinfo=tzlocal.get_localzone())
    # convert to string again with timezone
    # '2017-11-06 15:23:20+08:00'
    new_date = '{0}'.format(new_date.astimezone(tzlocal.get_localzone()))
    #print("old:{0} new:{1}".format(dt_str, new_date))

    if not year_holiday.get(year):
        url = 'http://timor.tech/api/holiday/year/{0}/'.format(year)
        my_headers =  {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,fr;q=0.8,en;q=0.7,en-US;q=0.6',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                #'Cookie': '__cfduid=d0c7c504e17ff584c84a580feb27e56c51598234397; Hm_lvt_f497f00a5871b6ed9078f87ab818d62d=1598234616; Hm_lpvt_f497f00a5871b6ed9078f87ab818d62d=1598344096',
                'Host': 'timor.tech',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
                }
        holiday = {}
        try:
            r = requests.get(url, headers = my_headers)
            if r.status_code == 200:
                rdata = r.text
                rdata = json.loads(rdata)
                if rdata.get('code') == 0:
                    holiday = rdata.get('holiday')
        except Exception as e:
            print('catch exception:{0}'.format(e))

        if not holiday:
            # no need to run 
            sys.exit(-1)
        year_holiday[year] = holiday
    
    # begin check
    holiday = year_holiday.get(year)
    mon_day = ''
    if month < 10:
        if day < 10:
            mon_day = '0{0}-0{1}'.format(month, day)
        else:
            mon_day = '0{0}-{1}'.format(month, day)
    else:
        if day < 10:
            mon_day = '{0}-0{1}'.format(month, day)
        else:
            mon_day = '{0}-{1}'.format(month, day)
    holiday_info = holiday.get(mon_day)
    if holiday_info:
        if holiday_info.get('holiday'):
            # it's holiday, not work day
            #print("year:{0} mon_day:{1} is holiday".format(year, mon_day))
            return None
        else:
            # tiao xiu, it's work day
            #print("year:{0} mon_day:{1} is tiaoxiu".format(year, mon_day))
            return new_date
    # not holiday or tiaoxiu ,just judge weekday
    if 1 <= weekday and weekday <= 5:
        # weekday 1 ~ 5, it's work day
        #print("year:{0} mon_day:{1} is weekday".format(year, mon_day))
        return new_date
    else:
        #print("year:{0} mon_day:{1} is weekend".format(year, mon_day))
        return None

    # should not come here
    return new_date




class GitRepository(object):
    """
    git仓库管理
    """

    def __init__(self, local_path, repo_url, branch='master'):
        self.local_path = local_path
        self.repo_url = repo_url
        self.repo = None
        self.initial(repo_url, branch)

    def initial(self, repo_url, branch):
        """
        初始化git仓库
        :param repo_url:
        :param branch:
        :return:
        """
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)

        git_local_path = os.path.join(self.local_path, '.git')
        if not is_git_dir(git_local_path):
            self.repo = Repo.clone_from(repo_url, to_path=self.local_path, branch=branch)
        else:
            self.repo = Repo(self.local_path)

    def pull(self):
        """
        从线上拉最新代码
        :return:
        """
        self.repo.git.pull()

    def branches(self):
        """
        获取所有分支
        :return:
        """
        branches = self.repo.remote().refs
        return [item.remote_head for item in branches if item.remote_head not in ['HEAD', ]]

    def commits(self):
        """
        获取所有提交记录
        :return:
        """
        commit_log = self.repo.git.log('--pretty={"commit":"%H","author":"%an","summary":"%s","date":"%cd", "timestamp":"%ct"}',
                                       #max_count=50,
                                       date="iso")
        log_list = commit_log.split("\n")
        return [eval(item) for item in log_list]

    def tags(self):
        """
        获取所有tag
        :return:
        """
        return [tag.name for tag in self.repo.tags]

    def change_to_branch(self, branch):
        """
        切换分值
        :param branch:
        :return:
        """
        self.repo.git.checkout(branch)

    def change_to_commit(self, branch, commit):
        """
        切换commit
        :param branch:
        :param commit:
        :return:
        """
        self.change_to_branch(branch=branch)
        self.repo.git.reset('--hard', commit)

    def change_to_tag(self, tag):
        """
        切换tag
        :param tag:
        :return:
        """
        self.repo.git.checkout(tag)

    def push_to_remote_branch(self):
        """
        push commits to remote repo

        :param branch: string
            branch name of remote repo
        return:
        """

        self.repo.git.push("-f")

    def rewrite_commit_demo(self, commit_sha):
        """
        demo of rewrite a commit using commit sha

        :param commit_sha: string
            format: something like this: d87187b4e8cbb3ef51eab3c136cb999ff0ccc129
        :return:
        :note:
            this is a demo of rewrite commit, you should rewrite this function
        """

        cmd = """
OLD_EMAIL="linuxcode2niki@gmail.com"
CORRECT_NAME="smaug"
CORRECT_EMAIL="smaug@gmail.com"
if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
"""
        
        r = self.repo.git.filter_branch("--env-filter", cmd,  "--", "--all")
        #r = self.repo.git.filter_branch("--env-filter", cmd)
        print(r)

    def rewrite_commit_date(self, commit_sha, old_date, force=False):
        """
        rewrite a commit date using commit sha

        :param commit_sha: string
            the hash of a commit,something like this: d87187b4e8cbb3ef51eab3c136cb999ff0ccc129
        :param old_date: string
            the datetime of this commit, format: 2020-01-2 13:00:30 +0800
        :param force: True/False
            force rewrite or stop rewrite when something goes wrong
        :return:
        """

        new_date = workdaytime_check(old_date)
        if not new_date:
            print("ignore commit:{0} because of safe time:{1}".format(commit_sha, old_date))
            return
        else:
            print("rewrite commit:{0} from old_date:{1} to safe time:{2}".format(commit_sha, old_date, new_date))

        cmd = """
if [ $GIT_COMMIT = "{0}" ]
then
    export GIT_AUTHOR_DATE="{1}"
    export GIT_COMMITTER_DATE="{2}"
fi
""".format(commit_sha, new_date, new_date)

        r = None
        if force:
            r = self.repo.git.filter_branch("--env-filter", cmd, '-f', "--", "--all")
        else:
            r = self.repo.git.filter_branch("--env-filter", cmd,  "--", "--all")
        print(r)

    def rewrite_commits_date(self, commits, force=False, push=False):
        """
        rewrite all commits date of a giving list of commit info

        :param commits: list
            a list of commit info, something like this: {'commit': '9d9edffda19ffe79c0ccbc65c2f898e7c01451e8', 'author': 'smaugx', 'summary': 'update Readme; update argsparse', 'date': '2020-08-24 22:26:53 +0800'}
        :param force: True/False
            force rewrite or stop rewrite when something goes wrong
        :return:
        """

        cmd = ""
        for commit_item in commits:
            commit_sha = commit_item.get('commit')
            old_date   = commit_item.get('date')
            old_timestamp = int(commit_item.get('timestamp'))
            new_date = workdaytime_check(old_timestamp)
            if not new_date:
                print("ignore commit:{0} because of safe time:{1} timestamp:{2}".format(commit_sha, old_date, old_timestamp))
                continue

            print("rewrite commit:{0} from old_date:{1} to safe time:{2}".format(commit_sha, old_date, new_date))
            part_cmd = """
if [ $GIT_COMMIT = "{0}" ]
then
    export GIT_AUTHOR_DATE="{1}"
    export GIT_COMMITTER_DATE="{2}"
fi
""".format(commit_sha, new_date, new_date)

            cmd += part_cmd

        r = None
        if force:
            r = self.repo.git.filter_branch("--env-filter", cmd, '-f', "--", "--all")
        else:
            r = self.repo.git.filter_branch("--env-filter", cmd,  "--", "--all")
        print(r)
        print("rewrite commits date done\n")

        if not push:
            return

        yes_and_no = input("will push rewrite-commits to remote repo, are you sure?[Y/N]")
        yes_and_no = yes_and_no.lower()
        if yes_and_no == 'y':
            # will push to remote
            print("push to remote")
            self.push_to_remote_branch()
        else:
            print("cancel push operation, you can push manually later!")
            yes_and_no = input("Or you can check new commits log?[Y/N]")
            yes_and_no = yes_and_no.lower()
            if yes_and_no == 'n':
                print('stop operation')
                return

            new_commits = self.commits()
            for commit_item in new_commits:
                commit_sha = commit_item.get('commit')
                date = commit_item.get('date')
                print('commit:{0} date:{1}'.format(commit_sha, date))

            yes_and_no = input("\nif everything is right, push to remote repo?[Y/N]")
            yes_and_no = yes_and_no.lower()
            if yes_and_no == 'n':
                print("stop operation")
                return
            print("push to remote")
            self.push_to_remote_branch()
        return

   

def main(remote_path, local_path):
    repo = GitRepository(local_path,remote_path)
    branch_list = repo.branches()
    print("list all branch:")
    print(branch_list)
    branch_name = 'master'
    while True:
        branch_name = input("please select your branch:")
        if branch_name in branch_list:
            break

    repo.change_to_branch(branch_name)
    repo.pull()

    # list of {'commit': '3e14f7158ebafe53228efb0e8bd62baa66f805ec', 'author': 'smaugx', 'summary': 'add zip', 'date': '2020-07-31 10:18:30 +0800'}
    commit_list = repo.commits()
    print("fetch {0} commits".format(len(commit_list)))
    #repo.rewrite_commits_date(commit_list, False)
    repo.rewrite_commits_date(commit_list, True, True)


if __name__ == '__main__':
    local_path = '/root/temp'
    remote_path='https://github.com/smaugx/dailytools.git'
    repo_name = remote_path.split('/')[-1].split('.')[0]
    local_path = os.path.join(local_path, repo_name)
    main(remote_path, local_path)
