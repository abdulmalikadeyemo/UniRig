import uvicorn
import os
import sys
import argparse

def main():
    """Run the UniRig API server"""
    parser = argparse.ArgumentParser(description="Run the UniRig API server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Print startup message
    print("Starting UniRig API server...")
    print(f"Server will be available at http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
    print("Press Ctrl+C to stop the server")

    # Run the server
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.debug else "info"
    )

if __name__ == "__main__":
    # Change to the directory of this script to ensure correct paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Make sure the app module can be imported
    sys.path.insert(0, script_dir)
    
    main() 