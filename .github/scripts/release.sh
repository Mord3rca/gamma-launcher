#!/bin/bash
SCRIPT_NAME="$(command -v gamma-launcher)"

if [[ "${RUNNER_OS}" == "Windows" ]]; then
	# No idea how to fix that properly, don't want to lose time
	# for this crap. Just gonna put runner script generated
	# by pip and hope for the best. I like cat btw :)
	SCRIPT_NAME="${PWD}/gamma-launcher.py"
	cat >"${SCRIPT_NAME}" <<EOF
import re
import sys
from launcher.cli import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
EOF
	fi

pyinstaller --distpath './artifacts' --onefile "${SCRIPT_NAME}"

