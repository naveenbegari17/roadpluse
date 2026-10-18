from app import app

# Vercel Serverless WSGI Handler entry point
# Exports 'app' for Vercel's Python runtime
handler = app
