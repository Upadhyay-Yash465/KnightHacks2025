#!/usr/bin/env python3
"""
Simple HTTP server for serving the SpeechCoach AI frontend
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def serve_frontend(port=3000):
    """Serve the frontend on the specified port"""
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    # Create custom handler to serve index.html for all routes
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_GET(self):
            # Serve index.html for all routes (SPA behavior)
            if self.path == '/' or not os.path.exists(self.path[1:]):
                self.path = '/index.html'
            return super().do_GET()
    
    # Start server
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"🚀 Frontend server running at http://localhost:{port}")
        print(f"📁 Serving files from: {frontend_dir}")
        print("Press Ctrl+C to stop the server")
        
        # Open browser automatically
        try:
            webbrowser.open(f'http://localhost:{port}')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    serve_frontend(port)

