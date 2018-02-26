CONFIG_FILE=uwsgi.ini

main() {
    cd $(dirname $0)
    sh configure.sh > $CONFIG_FILE
    . ./environ.sh
    uwsgi --ini $CONFIG_FILE
}

main $@
