#!/usr/bin/env bash
today=`date +%Y-%m-%d-%H:%M:%S`

# Check the folders ###########################################################
if [[ ! -d {app_log_dir} ]]; then
    echo "creating log dir"
    mkdir -p {app_log_dir}
    chown {chown_log_dir} {app_log_dir}/
else
    chown -R {chown_log_dir} {app_log_dir}
fi
###############################################################################

if [[ ! -d {instance_dirname} ]]; then
    mkdir {instance_dirname}
fi

if [[ ! -e {instance_dirname}/env.sh ]]; then
    echo "creating {instance_dirname} env vars file"
    echo "export NEST_PRODUCT_ID=" > {instance_dirname}/env.sh
    echo "export NEST_PRODUCT_SECRET=" > {instance_dirname}/env.sh
    echo "export MAILGUN_API_KEY=" > {instance_dirname}/env.sh
    echo "export MAILGUN_DOMAIN_NAME=" > {instance_dirname}/env.sh
    echo "export MAILGUN_FROM=" > {instance_dirname}/env.sh
    echo "export MAILGUN_TO=" > {instance_dirname}/env.sh
    echo "eval \"$(_GCAL_NEST_COMPLETE=source gcal-nest)\"" > {instance_dirname}/env.sh
    chmod +x {instance_dirname}/env.sh

    echo "WARNING: '{instance_dirname}/env.sh' needs to be modified!"
fi

# Check the circus config######################################################
if [[ (! -e {instance_dirname}/circus.ini) || (-n `diff _build/circus.ini {instance_dirname}/circus.ini`) ]]; then
    echo "changes detected in '{instance_dirname}/circus.ini'"
    cp -f _build/circus.ini {instance_dirname}
else
    echo "no changes detected in circus.ini"
fi
###############################################################################

# Check the service ###########################################################
if [[ ! -e {service_path}/{service_name} ]]; then
    echo "creating the service"
    cp _build/gcal-nest-systemd.service {service_path}/{service_name}
    chmod 755 {service_path}/{service_name}
    systemctl daemon-reload
    systemctl enable {service_name}
elif [[ -n `diff _build/gcal-nest-systemd.service {service_path}/{service_name}` ]]; then
    echo "backing up existing service file"
    mv {service_path}/{service_name} {service_path}/{service_name}.$today

    echo "deploying the service"
    cp _build/gcal-nest-systemd.service {service_path}/{service_name}
    chmod {service_chmod} {service_path}/{service_name}
    systemctl daemon-reload
else
    echo "no change detected in {service_path}/{service_name}"
fi

# We always want to restart the service to pick up the code changes.
echo "restarting the service"
systemctl restart {service_name}
