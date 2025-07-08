#!/usr/bin/env python3
"""
ZestAPI CLI Tool
This module provides command-line interface tools for ZestAPI projects.
"""
import argparse
import os
import sys


def init_project() -> None:
    """Initialize a new ZestAPI project"""
    print("Initializing ZestAPI project...")
    if (
        os.path.exists("app")
        and os.path.exists("main.py")
        and os.path.exists("config.py")
    ):
        print("Project structure already exists.")
    else:
        os.makedirs("app/routes", exist_ok=True)
        os.makedirs("app/plugins", exist_ok=True)

        # Create main.py with ZestAPI app
        main_content = """from zestapi import ZestAPI, route, ORJSONResponse
import os

app_instance = ZestAPI(
    routes_dir=os.path.join(os.path.dirname(__file__), "app", "routes"),
    plugins_dir=os.path.join(os.path.dirname(__file__), "app", "plugins"),
)

@route("/")
async def homepage(request):
    return ORJSONResponse({
        "message": "Welcome to ZestAPI!",
        "version": "1.0.0"
    })

app = app_instance.app

if __name__ == "__main__":
    app_instance.run()
"""
        with open("main.py", "w") as f:
            f.write(main_content)

        # Create .env file
        env_content = """# ZestAPI Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT=100/minute
"""
        with open(".env", "w") as f:
            f.write(env_content)

        print("Basic project structure created.")
        print("Run 'python main.py' to start your ZestAPI server!")


def generate_route(name: str) -> None:
    """Generate a new route file"""
    print(f"Generating route: {name}.py")
    route_path = os.path.join("app", "routes", f"{name}.py")

    # Ensure routes directory exists
    os.makedirs(os.path.dirname(route_path), exist_ok=True)

    route_content = f"""from zestapi import route, ORJSONResponse

@route("/{name}", methods=["GET"])
async def {name}_index(request):
    return ORJSONResponse({{"{name}": "Hello from {name} route!"}})

@route("/{name}/{{item_id}}", methods=["GET"])
async def {name}_get_item(request):
    item_id = request.path_params["item_id"]
    return ORJSONResponse({{
        "id": item_id,
        "type": "{name}",
        "message": f"Getting {name} item {{item_id}}"
    }})

@route("/{name}", methods=["POST"])
async def {name}_create(request):
    # Get JSON data from request
    data = await request.json()
    return ORJSONResponse({{
        "message": f"Created new {name}",
        "data": data
    }}, status_code=201)
"""
    with open(route_path, "w") as f:
        f.write(route_content)
    print(f"Route {name}.py created at {route_path}")


def view_route_map() -> None:
    """View the ZestAPI route map"""
    print("ZestAPI Route Map:")
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    try:
        from zestapi.core.routing import discover_routes

        routes_dir = os.path.join(os.getcwd(), "app", "routes")
        if not os.path.exists(routes_dir):
            print("  No routes directory found. Run 'zest init' first.")
            return
        discovered_routes = discover_routes(routes_dir)

        if not discovered_routes:
            print("  No routes discovered.")
            return
        for route_obj in discovered_routes:
            methods = getattr(route_obj, "methods", "N/A")
            if hasattr(methods, "__iter__") and not isinstance(methods, str):
                methods = list(methods)
            path = getattr(route_obj, "path", "Unknown")
            print(f"  Path: {path}, Methods: {methods}")
    except ImportError as e:
        print(f"  Error importing routing module: {e}")
    except Exception as e:
        print(f"  Error discovering routes: {e}")


def generate_plugin(name: str) -> None:
    """Generate a new plugin"""
    print(f"Generating plugin: {name}.py")
    plugin_path = os.path.join("app", "plugins", f"{name}.py")

    # Ensure plugins directory exists
    os.makedirs(os.path.dirname(plugin_path), exist_ok=True)

    plugin_content = f'''from starlette.responses import JSONResponse

class {name.title()}Plugin:
    """
    {name.title()} Plugin for ZestAPI

    This plugin adds {name} functionality to your ZestAPI application.
    """
    def __init__(self, app):
        self.app = app

    def register(self):
        """Register plugin routes and middleware"""
        # Add plugin routes
        @self.app.route("/{name}/status", methods=["GET"])
        async def {name}_status(request):
            return JSONResponse({{
                "plugin": "{name}",
                "status": "active",
                "version": "1.0.0"
            }})

        print(f"{name.title()}Plugin registered successfully.")
'''

    with open(plugin_path, "w") as f:
        f.write(plugin_content)
    print(f"Plugin {name}.py created at {plugin_path}")
    print(
        f"To enable this plugin, add '{name}' to ENABLED_PLUGINS " f"in your .env file"
    )


def main() -> None:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ZestAPI CLI Tool - Build modern APIs with ease"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_project()

    # generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate ZestAPI components"
    )
    generate_subparsers = generate_parser.add_subparsers(dest="component")

    # generate route
    generate_route_parser = generate_subparsers.add_parser(
        "route", help="Generate a new route file"
    )
    generate_route_parser.add_argument("name", type=str, help="Name of the route")

    # generate plugin
    generate_plugin_parser = generate_subparsers.add_parser(
        "plugin", help="Generate a new plugin"
    )
    generate_plugin_parser.add_argument("name", type=str, help="Name of the plugin")

    # route-map command
    subparsers.add_parser("route-map", help="View the ZestAPI route map")

    # version command
    subparsers.add_parser("version", help="Show ZestAPI version")

    args = parser.parse_args()

    if args.command == "init":
        init_project()
    elif args.command == "generate":
        if args.component == "route":
            generate_route(args.name)
        elif args.component == "plugin":
            generate_plugin(args.name)
        else:
            generate_parser.print_help()
    elif args.command == "route-map":
        view_route_map()
    elif args.command == "version":
        from zestapi import __version__

        print(f"ZestAPI {__version__}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
