# post-rail

Local UI available to all devices on the network to upload, delete, and download images from a folder of the server running the UI.

Also supports modifying configuration variables for a companion app.

# Development

## Usage

```sh
uv run -- flask run -p 8000
uv run gunicorn -w 4 -b 127.0.0.1:8000 'app:app'
```
