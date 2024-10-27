#!/usr/bin/env bash
rsync -azvhP --stats --inplace --zc=zstd --zl=3 playlists/ ~/nfs/WDC14/Musique/00_Playlists/
rsync -azvhP --stats --inplace --zc=zstd --zl=3 jazz_standards/jazz_standards.m3u ~/nfs/WDC14/Musique/00_Playlists/
