#!/usr/bin/env bash
rsync -azvhP --stats --inplace --zc=zstd --zl=3 playlists/ ~/nfs/WDC14/Musique/00_Playlists/
