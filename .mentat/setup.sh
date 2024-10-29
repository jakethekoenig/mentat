apt update
apt install -y universal-ctags
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
. "$HOME/.cargo/env"
pip3 install --user -e .
pip3 install --user -r requirements.txt
pip3 install --user -r dev-requirements.txt