#!/bin/bash
#
# moOde audio player (C) 2014 Tim Curtis
# http://moodeaudio.org
#
# This Program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This Program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

VER="7.5.0"
GPIO_TOGGLE_PAUSE_PLAY="gpio5"

if [[ $1 = "--help" ]]; then
echo -e "Usage: $0 [TIME]
Plays/pauses (mpc toggle) but if pressed again for [TIME] seconds, powers off
the system (shutdown / halt). If not specified, the default is 5 seconds.

 --version\tprint the program version
 --help\t\tprint this help text"

	exit 1
fi

if [[ $1 = "--version" ]]; then
	echo "Version: "$VER
	exit 1
fi

# Function to be run in a separate process, and wait checking for a possible shutdown long-press
function wait_shutdown()
{
	TICKS=${1:-5}
	# echo "($PPID) $$ wait_shutdown() starts with $TICKS ticks, at $(date)"

	for i in $(seq $TICKS)
	do
		sleep 1
		VAL=$(sudo cat /sys/class/gpio/$GPIO_TOGGLE_PAUSE_PLAY/value)
		# 0 means pressed
		# [[ $VAL != 0 ]] && echo "($PPID) $$ break after not pressed"
		[[ $VAL != 0 ]] && break
		# echo "($PPID) $$ still pressed"
	done

	if [[ $VAL == 0 ]]
	then
		sudo systemctl stop tft-moodecoverart &
		sudo mpc vol 0
		sudo mpc stop
		# echo "($PPID) $$ power off"
		sudo poweroff
	fi
}

if [[ $1 = "--spawn" ]]; then
	shift
	wait_shutdown "$@"
	# echo "($PPID) $$ exit after wait_shutdown()"
	exit 0
fi

# DEBUG: Leave trace of this script's output. See: https://unix.stackexchange.com/a/145654
# exec &> >(tee -a /tmp/shutdown_or_toggle.log)

# echo "($PPID) $$ starts at $(date)"

mpc toggle > /dev/null

"$0" --spawn "$@" &

# sleep 1

# echo "($PPID) $$ exit after spawning"

