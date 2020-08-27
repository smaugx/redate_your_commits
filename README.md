# redate\_your\_commits

## what is redate\_your\_commits?
If you want to rewrite your git repository commits which already pushed to remote, then you maybe need this tool.

This tool helps you to rewrite your commits date from on-work-time to off-work-time. 

(think why? Ha-Ha-Ha, If you laughed, I recommend you to use this tool.)

+ on\-work\-time: meaning workday include reset-day(调休）and from 9:00 to  19:00
+ off\-work\-time: meaning not on\-work\-day, that is holiday and weekend

![](https://cdn.jsdelivr.net/gh/smaugx/MyblogImgHosting_2/redate_your_commits/redate_your_commits_usage.gif)


## REQUIREMENTS
Very few! Just:

+ Python3
+ Git

The list of dependencies is shown in ./requirements.txt, however the installer takes care of installing them for you.


## INSTALL
```
# git clone https://github.com/smaugx/redate_your_commits.git
# cd redate_your_commits
# virtualenv -p python3 venv
# source  venv/bin/activate
# pip install -r requirements.txt

```

## Usage
```
# python run.py  -h
usage: run.py [-h] [-l LOCAL_PATH] -r REMOTE_URL [-p [PUSH]] [-f [FORCE]]

redate_your_commits, rewrite commits date from on-work-time to off-work-time.

optional arguments:
  -h, --help            show this help message and exit
  -l LOCAL_PATH, --local_path LOCAL_PATH
                        local base path to clone your repo
  -r REMOTE_URL, --remote_url REMOTE_URL
                        your remote repo url
  -p [PUSH], --push [PUSH]
                        push to remote repo
  -f [FORCE], --force [FORCE]
                        rewrite commits force or push force
```

example:

```
# python run.py -l /tmp -r https://github.com/smaugx/redate_your_commits.git  -p -f
```

**attention: maybe you should use this tool on a test-repo first, Or you should not use -p params first.**

if you test everything ok, than re-run this tool again with `-p` `-f`. 

Good Luck To You!

## Thanks
+ [免费节假日 API](https://timor.tech/api/holiday/)
+ [GitDoc-Change-Author-Info](https://docs.github.com/en/github/using-git/changing-author-info)
+ [git-scm](https://git-scm.com/docs/git-filter-branch)

## License
This is BSD licensed (see LICENSE.md)