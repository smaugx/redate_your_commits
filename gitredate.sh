#!/bin/sh

git filter-branch --env-filter '

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
' -f --prune-empty -- --branches="*" --tags="list*"
