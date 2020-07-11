#!/bin/sh

function usage() {
    echo 'Commands:'
    echo ' - mypy - runs mypy checker in the main app'
    echo ' - mypy-tests - runs mypy checker in unit tests'
    echo ' - tests - runs unit tests'
}

if (( $# > 0 )); then
    command=$1
    shift

    case $command in
        'mypy')
            python -m mypy egida.py --show-error-codes $@
            ;;
        'mypy-tests')
            python -m mypy test/test_*.py --show-error-codes $@
            ;;
        'tests')
            python -m unittest $@
            ;;
        *)
            echo "Command \"$command\" unknown."
            echo
            usage
            ;;
    esac
else
    echo 'Please give a command.'
    echo
    usage
fi
