#!/usr/bin/env sh
{{ ansible_managed | comment }}

alias grep='grep --color=auto --exclude-dir={.bzr,CVS,.git,.hg,.svn}'
export LS_OPTIONS='--color=auto'
eval "`dircolors`"
alias ls='ls $LS_OPTIONS'
alias ll='ls $LS_OPTIONS -l'
alias l='ls $LS_OPTIONS -lA'
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

export EDITOR="vim"
alias vi="vim"

make_cpu_online () {
	cd /sys/devices/system/cpu/
	for F in cpu* ; do echo 1 > "$F/online"; done
}

rescan_disks() {
    for D in $(ls /sys/block); do
        [ -f  /sys/block/${D}/device/rescan ] && echo 1 > /sys/block/${D}/device/rescan;
    done
}