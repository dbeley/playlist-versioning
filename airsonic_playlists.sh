#!/usr/bin/env bash
rsync -azvhP --stats --inplace --zc=zstd --zl=3 playlists/ ~/nfs/Expansion/docker/airsonic_Playlists/
