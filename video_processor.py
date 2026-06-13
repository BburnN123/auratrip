import videodb

# Connect using environment variable
conn = videodb.connect()

# Or pass API key directly
conn = videodb.connect(api_key="sk-ORakb92RnST4eZsLgPQ7Y6EQuBmfHlOSy6gxKhLg-Kw")

videos = conn.list_videos()
for v in videos:
    print(v['title'], v['url']);
