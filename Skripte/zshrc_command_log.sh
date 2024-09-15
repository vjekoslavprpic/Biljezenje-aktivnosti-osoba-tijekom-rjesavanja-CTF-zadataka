log_command() {

    local start_time=$(date +"%Y-%m-%d_%H-%M-%S")
    local log_file="$HOME/.command_output_${start_time}.log"
    local command="$*"

    script -q "$log_file" -c "$command" 

    sleep 1

    local timestamp=$(date +"%Y-%m-%d %T")

    local json_output
    json_output=$(cat "$log_file" | sed 's/"/\\"/g' | tr '\n' '\\n' | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g")

    printf '{"timestamp": "%s", "command": "%s", "output": "%s"}\n' \
        "$timestamp" "$(echo "$command" | sed 's/"/\\"/g')" "$json_output" >> "$HOME/.command_output_func.log"
        
    rm -f "$log_file"
}


preexec() {
    if [[ -n "$1" ]]; then
        log_command "$1" >/dev/null
    fi
}

preexec_functions+=(preexec)