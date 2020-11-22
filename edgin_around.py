#!/usr/bin/env python

import argparse

import src


class Config:
    def __init__(self, resource_dir: str) -> None:
        self.resource_dir = resource_dir

    @staticmethod
    def from_arguments() -> "Config":
        parser = argparse.ArgumentParser(description="Desktop version of EdginAround.")
        parser.add_argument(
            "--res",
            dest="resource_dir",
            type=str,
            default="/usr/share/edgin_around/resources/",
            help="Path to resources",
        )

        args = parser.parse_args()
        return Config(args.resource_dir)


if __name__ == "__main__":
    config = Config.from_arguments()
    src.Game(resource_dir=config.resource_dir).run()
