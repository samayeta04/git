"""Reads test users (user IDs / e-mails + passwords) from an Excel sheet.

Expected columns (header row, case-insensitive):
    TestID | Email | Password | Expected | Description

Expected = valid   -> login must succeed
Expected = invalid -> login must be rejected
"""
from dataclasses import dataclass
from typing import List

from openpyxl import load_workbook

import config


@dataclass
class UserRecord:
    test_id: str
    email: str
    password: str
    expected: str          # "valid" | "invalid"
    description: str = ""

    @property
    def is_placeholder(self) -> bool:
        return any(
            str(v).startswith(config.PLACEHOLDER_PREFIXES)
            for v in (self.email, self.password)
        )


def _clean(value) -> str:
    return "" if value is None else str(value).strip()


def read_users(path=None, sheet=None) -> List[UserRecord]:
    path = path or config.EXCEL_PATH
    sheet = sheet or config.EXCEL_SHEET
    wb = load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet in wb.sheetnames else wb.active

    rows = ws.iter_rows(values_only=True)
    headers = [_clean(h).lower() for h in next(rows)]
    idx = {name: headers.index(name) for name in headers if name}

    def col(row, name):
        return _clean(row[idx[name]]) if name in idx and idx[name] < len(row) else ""

    records = []
    for n, row in enumerate(rows, start=2):
        if not any(row):
            continue
        records.append(
            UserRecord(
                test_id=col(row, "testid") or f"ROW{n}",
                email=col(row, "email") or col(row, "userid"),
                password=col(row, "password"),
                expected=(col(row, "expected") or "valid").lower(),
                description=col(row, "description"),
            )
        )
    return records


def users_by_expectation(expected: str) -> List[UserRecord]:
    return [u for u in read_users() if u.expected == expected]
