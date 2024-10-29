apt update
apt install -y universal-ctags
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
. "$HOME/.cargo/env"
pip3 install --upgrade pip
pip3 install -e .
pip3 install -r requirements.txt
pip3 install -r dev-requirements.txt