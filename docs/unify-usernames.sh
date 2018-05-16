#!/bin/sh

git filter-branch --env-filter '

n=$GIT_AUTHOR_NAME
m=$GIT_AUTHOR_EMAIL

case ${GIT_AUTHOR_NAME} in
        Michael) n="michigraber" ; m="michigraber@gmail.com" ;;
        "Michael Graber") n="michigraber" ; m="michigraber@gmail.com" ;;
        "Andreas Kotowicz") n="koto" ; m="code@bithole.de" ;;
        "kotowicz") n="koto" ; m="code@bithole.de" ;;
        "Virtual DB user") n="koto" ; m="code@bithole.de" ;;        
        "database user") n="koto" ; m="code@bithole.de" ;;
        db) n="koto" ; m="code@bithole.de" ;;
        jk) n="joergenk" ; m="joergen.kornfeld@gmail.com" ;;                          
        jmrk) n="joergenk" ; m="joergen.kornfeld@gmail.com" ;;                          
esac

export GIT_AUTHOR_NAME="$n"
export GIT_AUTHOR_EMAIL="$m"
export GIT_COMMITTER_NAME="$n"
export GIT_COMMITTER_EMAIL="$m"
'


