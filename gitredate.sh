#!/bin/sh

remote_repo=''
local_repo=''

clone_repo()
{
    local_repo=` echo $1 |awk -F '/' '{print $NF}' `
    remote_repo=$1
    echo "clone remote_repo:$remote_repo to local_repo:$local_repo"

    # usage: git clone --bare https://github.com/smaugx/temp.git
    git clone --bare $remote_repo $local_repo
}

rewrite_commits_demo()
{
    cd $local_repo
    pwd
    git filter-branch --env-filter '

OLD_EMAIL="old@gmail.com"
CORRECT_NAME="myname"
CORRECT_EMAIL="new@gmail.com"

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
' -f  --  --branches --tags
    cd -
}

rewrite_commits_date()
{
    cd $local_repo
    pwd
    git filter-branch --env-filter '

OLD_EMAIL="old@gmail.com"
CORRECT_NAME="myname"
CORRECT_EMAIL="new@gmail.com"

commit_date=$GIT_COMMITTER_DATE

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
' -f  --  --branches --tags
}
