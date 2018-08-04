IF NOT EXIST tweetf0rm (
git clone https://github.com/bianjiang/tweetf0rm.git
)
cd tweetf0rm
pip install -r requirements.txt
python twitter_tracker.py -c ../config.json -cmd search -o ../../data/eleicoes -cc ../eleicoes.json -w 300