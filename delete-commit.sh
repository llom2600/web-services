#!/bin/bash
# flushes out the commit history without making any changes

git checkout --orphan latest_code
git add *
git commit -am "-"
git branch -D master
git branch -m master
git push -f origin master