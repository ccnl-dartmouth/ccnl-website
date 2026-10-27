"""Collects build errors and warnings so a member sees all of them at once."""


class BuildFailed(Exception):
    """Raised when the build found errors and must not produce a site."""


class Problems:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, message):
        self.errors.append(f"{where}: {message}")

    def warn(self, where, message):
        self.warnings.append(f"{where}: {message}")

    def report(self):
        for w in self.warnings:
            print(f"WARNING  {w}")
        for e in self.errors:
            print(f"ERROR    {e}")
        if self.errors:
            print(f"\n{len(self.errors)} error(s). The site was NOT updated; fix the file(s) above and commit again.")

    def raise_if_errors(self):
        if self.errors:
            raise BuildFailed()
