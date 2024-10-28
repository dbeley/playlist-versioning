#!/usr/bin/env bash
rsync -azvhP --stats --inplace --zc=zstd --zl=3 mpd_playlists/ ~/.config/mpd/playlists/
rsync -azvhP --stats --inplace --zc=zstd --zl=3 jazz_standards/jazz_standards_mpd.m3u ~/.config/mpd/playlists/
