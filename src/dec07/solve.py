#!/usr/bin/env python3

import dataclasses
import sys
from typing import Optional

input = sys.stdin.readlines()


@dataclasses.dataclass(frozen=True)
class File:
    name: str
    size: int


@dataclasses.dataclass(frozen=True)
class Dir:
    name: str
    files: list[File] = dataclasses.field(default_factory=list)
    dirs: list["Dir"] = dataclasses.field(default_factory=list)


def parse() -> Dir:
    def is_cd(line: str) -> bool:
        return line.strip()[:4] == "$ cd"

    def is_cd_up(line: str) -> bool:
        return line.strip() == "$ cd .."

    def is_dir(line: str) -> bool:
        return line.strip()[:3] == "dir"

    def is_file(line: str) -> bool:
        return line.strip().split()[0].isnumeric()

    def dir(input: list[str]) -> tuple[Dir, list[str]]:
        assert is_cd(input[0]), input[0]
        assert not is_cd_up(input[0]), input[0]

        name = input[0].strip().split()[-1]
        files, dirs, rest = listing(input[1:])

        assert not rest or is_cd_up(rest[0]), rest[0]

        return Dir(name, files, dirs), rest[1:]

    def listing(input: list[str]) -> tuple[list[File], list[Dir], list[str]]:
        assert input[0].strip()[:4] == "$ ls", input[0]
        files, dirs, rest = contents(input[1:])

        if not rest or is_cd_up(rest[0]):
            return files, dirs, rest

        d, rest = dir(rest)
        return files, [d, *dirs], rest

    def contents(input: list[str]) -> tuple[list[File], list[Dir], list[str]]:
        if not input:
            return [], [], []

        if is_cd_up(input[0]):
            return [], [], input

        if is_cd(input[0]):
            d, rest = dir(input)
            files, dirs, rest = contents(rest)
            return files, [d, *dirs], rest

        if is_dir(input[0]):
            return contents(input[1:])

        if is_file(input[0]):
            size, name = input[0].strip().split()
            f, d, rest = contents(input[1:])
            return [File(name, int(size)), *f], d, rest

        raise Exception(f"not handled: {input[0]}")

    return dir(input)[0]


def size(d: Dir) -> int:
    return sum(f.size for f in d.files) + sum(size(sd) for sd in d.dirs)


def a():
    def capped_size(d: Dir, cap=100_000) -> int:
        file_size = sum(f.size for f in d.files)
        subdir_size = sum(size(sd) for sd in d.dirs)
        capped_subdir_size = sum(capped_size(sd) for sd in d.dirs)
        return (
            file_size + subdir_size + capped_subdir_size
            if file_size + subdir_size <= cap
            else capped_subdir_size
        )

    return capped_size(parse())


def b():
    capacity = 70000000
    required = 30000000
    tree = parse()

    total_size = size(tree)
    free = capacity - total_size
    missing = required - free

    def smallest_large_enough(d: Dir) -> Optional[int]:
        valid_subdir = min(
            (sd for sd in map(smallest_large_enough, d.dirs) if sd),
            default=None,
        )
        if valid_subdir:
            return valid_subdir

        s = size(d)
        if s >= missing:
            return s

        return None

    return smallest_large_enough(tree)


print("a:", a())
print("b:", b())
