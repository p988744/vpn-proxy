cleanup() {
  echo "removing $tmpdir"
  rm -rf "$tmpdir"
  echo "temp dir $tmpdir removed"
}
# set git repo url
git_repo_url=$(git config --get remote.origin.url)
# set production server name
target_server=
# set production server user
target_user=rd2
# set production server path
target_path="~/services/vpn-proxy"
# set flag for do deploy
do_deploy=true # default is false

source .env

echo "Deploying to $target_server as $target_user in $target_path"
echo "Git repo url: $git_repo_url"
echo "do_deploy: $do_deploy"

# create a temp directory to clone current repo git repository
tmpdir=$(mktemp -d)
echo "temp dir $tmpdir created"
# check tmpdir is created
if [ ! -d "$tmpdir" ]; then
  echo "temp dir $tmpdir not created"
  exit 1
fi

# clone the git repo to temp directory
echo "git clone $git_repo_url $tmpdir"
git clone "$git_repo_url" "$tmpdir"

# export requirements.txt for python via poetry
poetry export -f requirements.txt --output "$tmpdir/requirements.txt" --without-hashes

ls -alFh "$tmpdir"

# copy .env file from production server to temp directory if any dotenv file is exist
if ssh "$target_user@$target_server" "test -f $target_path/.env"; then
  echo "copying .env file from production server"
  scp "$target_user@$target_server:$target_path/.env" "$tmpdir"
fi

# copy squid/squid.passwd file from production server to temp directory if any squid file is exist
if ssh "$target_user@$target_server" "test -f $target_path/squid/squid.passwd"; then
  echo "copying squid.passwd file from production server"
  scp "$target_user@$target_server:$target_path/squid/squid.passwd" "$tmpdir"
fi

# copy sql_app.db file from production server to temp directory if any sql_app.db file is exist
if ssh "$target_user@$target_server" "test -f $target_path/sql_app.db"; then
  echo "copying sql_app.db file from production server"
  scp "$target_user@$target_server:$target_path/sql_app.db" "$tmpdir"
fi

# rsync the temp directory to production server
echo "rsync with $target_user@$target_server:$target_path"
rsync -avz --exclude .git --delete "$tmpdir/" "$target_user@$target_server:$target_path"

# do deploy if flag is true
if [ "$do_deploy" = true ]; then
  echo "deploying to production server"

  # create virtualenv and install python dependencies
  ssh "$target_user@$target_server" "cd $target_path && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

#  # stop previous uvicorn process if any service is running can be found in process list
#  if ssh "$target_user@$target_server" "ps -ef | grep uvicorn | grep -v grep"; then
#    echo "stopping previous uvicorn process"
#    ssh "$target_user@$target_server" "pkill -f uvicorn"
#  fi
#
#  # close tmux session if any session is exist
#  if ssh "$target_user@$target_server" "tmux ls | grep vpn-proxy"; then
#    echo "closing previous tmux session"
#    ssh "$target_user@$target_server" "tmux kill-session -t vpn-proxy"
#  fi

  # create tmux session and execute run fastapi service command
  ssh "$target_user@$target_server" "tmux new-session -d -s vpn-proxy 'cd $target_path && source venv/bin/activate && uvicorn web_apis:app --host 0.0.0.0 --port 8080 --workers 4'"
fi

trap cleanup EXIT

# The rest of the script goes here.
