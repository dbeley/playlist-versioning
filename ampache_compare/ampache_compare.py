from pathlib import Path

list_content = []
for i in Path("../ampache_backup_formatted/").glob("*.txt"):
    content = i.open().readlines()
    list_content += [x.strip() for x in content if x]

tracks = [x.split("/") for x in list_content]
tracks_formatted = [f"{x[2]} - {x[-1].split(' ', 1)[1].split('.')[0]}" for x in tracks]

with open("00-ampache_favorite_tracks.csv", "w") as f:
    f.write("\n".join(tracks_formatted))
