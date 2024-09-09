#!/usr/bin/env bash
rsync -azvhP --stats --inplace --zc=zstd --zl=3 mpd_playlists/ ~/.config/mpd/playlists/
