from pathlib import Path

list_content = []
for i in Path("../diff/").glob("*.txt"):
    print(i)
    content = i.open().readlines()
    list_content += [x.strip() for x in content if x]

print(list_content)
print(len(list_content))
print(list_content[0].split("/"))

tracks = [x.split("/") for x in list_content]
print(tracks)
tracks_formatted = [f"{x[2]} - {x[-1].split(' ', 1)[1].split('.')[0]}" for x in tracks]

print(tracks_formatted)
# print("\n".join(tracks_formatted))
with open("00-ampache_favorite_tracks.csv", "w") as f:
    f.write("\n".join(tracks_formatted))
