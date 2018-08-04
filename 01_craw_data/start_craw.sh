[[ -d tweetf0rm ]] || git clone git://github.com/bianjiang/tweetf0rm.git
cd tweetf0rm
pip install -r requirements.txt
python twitter_tracker.py -c ../config.json -cmd search -o ../../data/eleicoes -cc ../eleicoes.json -w 60
