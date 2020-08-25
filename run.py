#!/usr/bin/env python
#-*- coding:utf8 -*-


import os
import sys
import time
import requests
import datetime
import json
from git.repo import Repo
from git.repo.fun import is_git_dir

year_holiday = {}

# date : 2020-01-2 13:00:30 +0800
def workdaytime_check(date):
    global year_holiday
    dt = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S +0800')
    year = dt.year
    month = dt.month
    day = dt.day
    weekday = dt.weekday()  # 0 is sunday
    hour = dt.hour
    minute = dt.minute
    second = dt.second

    if hour < 9 or hour > 19:
        # not working time
        return None

    new_hour   = 22
    new_minute = 60 - (22 - hour) * 3 
    new_second = minute
    new_date = '{0}-{1}-{2} {3}:{4}:{5} +0800'.format(year,month,day,new_hour,new_minute,new_second)

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
            return None
        else:
            # tiao xiu, it's work day
            return new_date
    # not holiday or tiaoxiu ,just judge weekday
    if 1 <= weekday and weekday <= 5:
        # weekday 1 ~ 5, it's work day
        return new_date
    else:
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
        commit_log = self.repo.git.log('--pretty={"commit":"%H","author":"%an","summary":"%s","date":"%cd"}',
                                       max_count=50,
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

    def rewrite_commit_demo(self, commit_sha):
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

    def rewrite_commits_date(self, commits, force=False):
        cmd = ""
        for commit_item in commits:
            commit_sha = commit_item.get('commit')
            old_date = commit_item.get('date')
            new_date = workdaytime_check(old_date)
            if not new_date:
                print("ignore commit:{0} because of safe time:{1}".format(commit_sha, old_date))
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
        print("ready to push...")
   

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

    #repo.rewrite_commit_demo("fjdl")

    repo.rewrite_commits_date(commit_list, False)


if __name__ == '__main__':
    local_path = '/Users/smaug/temp'
    remote_path='https://github.com/smaugx/temp.git'
    repo_name = remote_path.split('/')[-1].split('.')[0]
    local_path = os.path.join(local_path, repo_name)
    main(remote_path, local_path)
