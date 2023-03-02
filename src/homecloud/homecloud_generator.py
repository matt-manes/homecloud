import argparse
from pathlib import Path

root = Path(__file__).parent

""" Class and CLI for generating the files needed to integrate homecloud into a project. """


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "app_name",
        type=str,
        nargs="?",
        default=Path.cwd().parent,
        help=""" The name of the app to generate files for.
        If a value isn't provided, the folder name
        of the current working directory will be used.""",
    )

    parser.add_argument(
        "-r",
        "--routes",
        type=str,
        nargs="*",
        default=[],
        help=""" The routes to generate files for in addition to 'get' and 'post' routes.""",
    )

    parser.add_argument(
        "-d",
        "--destination",
        type=str,
        default=Path.cwd(),
        help=""" The directory to save the generated files to.
        By default, uses the current working directory. """,
    )

    args = parser.parse_args()
    args.destination = Path(args.destination)

    return args


class HomeCloudGenerator:
    def __init__(self, app_name: str, destination: Path, routes: list[str] = []):
        """Initialize homecloud generator object.

        :param app_name: The app name to use.

        :param destination: The destination to write the generated files to.

        :param routes: List of routes to generate files for
        in addition to 'get' and 'post' routes."""
        self.app_name = app_name
        self.destination = destination
        self.routes = ["get", "post"] + routes

    def generate_routes(self):
        """Generate route files."""
        for route in self.routes:
            if route not in ["get", "post"]:
                file = root / "router_template.py"
            else:
                file = root / f"{route}_routes.py"
            content = file.read_text().replace("$app_name", self.app_name)
            (self.destination / f"{self.app_name}_{route}_routes.py").write_text(
                content
            )

    def generate_server(self):
        """Generate the server file."""
        content = (root / "server.py").read_text()
        routes = [
            route.stem
            for route in self.destination.glob(f"{self.app_name}_*_routes.py")
        ]
        imports = "\n".join([f"import {route}" for route in routes])
        includes = "\n".join(
            [f"app.include_router({route}.router)" for route in routes]
        )
        for sub in [
            ('"$app_name"', self.app_name),
            ('"$router_imports"', imports),
            ('"$router_includes"', includes),
        ]:
            content = content.replace(sub[0], sub[1])
        (self.destination / f"{self.app_name}_server.py").write_text(content)

    def generate_client(self):
        """Generate the client file."""
        content = (root / "client_subclass.py").read_text()
        content = content.replace(
            "app_nameClient", f"{self.app_name.capitalize()}Client"
        )
        content = content.replace("$app_name", self.app_name)
        (self.destination / f"{self.app_name}_client.py").write_text(content)

    def generate_request_models(self):
        """Generate the request_models file."""
        (self.destination / f"{self.app_name}_request_models.py").write_text(
            (root / "request_models.py").read_text()
        )

    def generate_config(self):
        """Generate the homecloud_config file."""
        (self.destination / "homecloud_config.toml").write_text(
            (root / "homecloud_config.toml").read_text()
        )

    def generate_all(self):
        """Generate all files."""
        self.generate_routes()
        # generate_routes() should be called before generate_server()
        # because the latter will scan the project directory
        # for route files to determine some of the server file content
        self.generate_server()
        self.generate_client()
        self.generate_request_models()
        self.generate_config()


def main(args: argparse.Namespace = None):
    if not args:
        args = get_args()
    generator = HomeCloudGenerator(args.app_name, args.destination, args.routes)
    generator.generate_all()


if __name__ == "__main__":
    main(get_args())
