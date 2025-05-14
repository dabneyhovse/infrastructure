docker run --rm -i -t \
  --network host \
  --user 1000:1000 \
  -p 12345:12345 \
  -v /home/comptroller/.config/kanidm:/data/config:ro \
  -v /home/comptroller/infrastructure/services/idm/keys/:/home/comptroller/infrastructure/services/idm/keys/:ro \
  -v ./ipa-sync.toml:/data/ipa-sync.toml \
  kanidm/tools:latest \
  kanidm-ipa-sync -i /data/ipa-sync.toml