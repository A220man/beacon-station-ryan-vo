import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class TestResult:
    passed: int
    failed: int
    skipped: int
    total: int
    duration_ms: Optional[float] = None
    raw_summary: str = ""
    exit_code: Optional[int] = None

    def to_ledger_string(self) -> str:
        parts = []
        if self.total > 0:
            parts.append(f"{self.passed}/{self.total} pass")
        if self.failed:
            parts.append(f"{self.failed} fail")
        if self.skipped:
            parts.append(f"{self.skipped} skipped")
        if self.duration_ms is not None:
            parts.append(f"{self.duration_ms:.1f}ms")
        return "; ".join(parts) if parts else "no tests"


class TestResultParser:
    PARSERS = [
        "parse_node_test",
        "parse_pytest",
        "parse_npm_test",
        "parse_cargo_test",
        "parse_go_test",
        "parse_jest",
        "parse_vitest",
    ]

    @classmethod
    def parse(cls, output: str, exit_code: int, command: str) -> TestResult:
        for parser_name in cls.PARSERS:
            parser = getattr(cls, parser_name)
            result = parser(output, exit_code)
            if result.total > 0 or result.raw_summary:
                return result

        return TestResult(
            passed=0,
            failed=0,
            skipped=0,
            total=0,
            raw_summary=cls._last_meaningful_line(output),
            exit_code=exit_code,
        )

    @classmethod
    def parse_node_test(cls, output: str, exit_code: int) -> TestResult:
        passed = failed = skipped = 0
        duration_ms = None

        pass_match = re.search(r"#\s+pass\s+(\d+)", output)
        if pass_match:
            passed = int(pass_match.group(1))

        fail_match = re.search(r"#\s+fail\s+(\d+)", output)
        if fail_match:
            failed = int(fail_match.group(1))

        skip_match = re.search(r"#\s+(?:skipped|skip)\s+(\d+)", output)
        if skip_match:
            skipped = int(skip_match.group(1))

        duration_match = re.search(r"#\s+duration_ms\s+([\d.]+)", output)
        if duration_match:
            duration_ms = float(duration_match.group(1))

        total = passed + failed + skipped
        if total == 0:
            return TestResult(0, 0, 0, 0, exit_code=exit_code)

        return TestResult(
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            duration_ms=duration_ms,
            raw_summary=f"{passed}/{total} pass" + (f"; {failed} fail" if failed else "") + (f"; {skipped} skipped" if skipped else ""),
            exit_code=exit_code,
        )

    @classmethod
    def parse_pytest(cls, output: str, exit_code: int) -> TestResult:
        passed = failed = skipped = 0

        summary_match = re.search(r"=+ (\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?", output)
        if summary_match:
            passed = int(summary_match.group(1) or 0)
            failed = int(summary_match.group(2) or 0)
            skipped = int(summary_match.group(3) or 0)
        else:
            passed = len(re.findall(r"\bPASSED\b", output))
            failed = len(re.findall(r"\bFAILED\b", output))
            skipped = len(re.findall(r"\bSKIPPED\b", output))

        duration_match = re.search(r"in ([\d.]+)s", output)
        duration_ms = float(duration_match.group(1)) * 1000 if duration_match else None

        total = passed + failed + skipped
        if total == 0:
            return TestResult(0, 0, 0, 0, exit_code=exit_code)

        return TestResult(
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            duration_ms=duration_ms,
            raw_summary=f"{passed}/{total} pass" + (f"; {failed} fail" if failed else "") + (f"; {skipped} skipped" if skipped else ""),
            exit_code=exit_code,
        )

    @classmethod
    def parse_npm_test(cls, output: str, exit_code: int) -> TestResult:
        for parser in [cls.parse_jest, cls.parse_vitest, cls.parse_mocha]:
            result = parser(output, exit_code)
            if result.total > 0:
                return result
        return TestResult(0, 0, 0, 0, exit_code=exit_code)

    @classmethod
    def parse_jest(cls, output: str, exit_code: int) -> TestResult:
        passed = failed = skipped = 0
        tests_line_match = re.search(r"Tests:\s+(.+)", output)
        if tests_line_match:
            line = tests_line_match.group(1)
            p = re.search(r"(\d+)\s+passed", line, re.IGNORECASE)
            f = re.search(r"(\d+)\s+failed", line, re.IGNORECASE)
            s = re.search(r"(\d+)\s+skipped", line, re.IGNORECASE)
            if p:
                passed = int(p.group(1))
            if f:
                failed = int(f.group(1))
            if s:
                skipped = int(s.group(1))
        total = passed + failed + skipped
        if total == 0:
            return TestResult(0, 0, 0, 0, exit_code=exit_code)
        return TestResult(
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            raw_summary=f"{passed}/{total} pass" + (f"; {failed} fail" if failed else "") + (f"; {skipped} skipped" if skipped else ""),
            exit_code=exit_code,
        )

    @classmethod
    def parse_vitest(cls, output: str, exit_code: int) -> TestResult:
        passed = failed = skipped = 0
        match = re.search(r"Tests\s+(\d+)\s+passed", output)
        if match:
            passed = int(match.group(1))
        fail_match = re.search(r"(\d+)\s+failed", output)
        if fail_match:
            failed = int(fail_match.group(1))
        skip_match = re.search(r"(\d+)\s+skipped", output)
        if skip_match:
            skipped = int(skip_match.group(1))
        total = passed + failed + skipped
        if total == 0:
            return TestResult(0, 0, 0, 0, exit_code=exit_code)
        return TestResult(
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            raw_summary=f"{passed}/{total} pass" + (f"; {failed} fail" if failed else ""),
            exit_code=exit_code,
        )

    @classmethod
    def parse_mocha(cls, output: str, exit_code: int) -> TestResult:
        match = re.search(r"(\d+) passing(?: \([\d.]+s\))?(?:, (\d+) failing)?(?:, (\d+) pending)?", output)
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2) or 0)
            skipped = int(match.group(3) or 0)
            total = passed + failed + skipped
            return TestResult(
                passed=passed,
                failed=failed,
                skipped=skipped,
                total=total,
                raw_summary=f"{passed}/{total} pass" + (f"; {failed} fail" if failed else "") + (f"; {skipped} pending" if skipped else ""),
                exit_code=exit_code,
            )
        return TestResult(0, 0, 0, 0, exit_code=exit_code)

    @classmethod
    def parse_cargo_test(cls, output: str, exit_code: int) -> TestResult:
        match = re.search(r"test result: (\w+). (\d+) passed; (\d+) failed; (\d+) ignored;", output)
        if match:
            passed = int(match.group(2))
            failed = int(match.group(3))
            skipped = int(match.group(4))
            total = passed + failed + skipped
            return TestResult(
                passed=passed,
                failed=failed,
                skipped=skipped,
                total=total,
                raw_summary=f"{passed}/{total} pass" + (f"; {failed} fail" if failed else "") + (f"; {skipped} ignored" if skipped else ""),
                exit_code=exit_code,
            )
        return TestResult(0, 0, 0, 0, exit_code=exit_code)

    @classmethod
    def parse_go_test(cls, output: str, exit_code: int) -> TestResult:
        passed = len(re.findall(r"^--- PASS:", output, re.MULTILINE))
        failed = len(re.findall(r"^--- FAIL:", output, re.MULTILINE))
        skipped = len(re.findall(r"^--- SKIP:", output, re.MULTILINE))
        total = passed + failed + skipped

        duration_match = re.search(r"ok\s+\S+\s+([\d.]+)s", output)
        duration_ms = float(duration_match.group(1)) * 1000 if duration_match else None

        if total == 0:
            return TestResult(0, 0, 0, 0, exit_code=exit_code)

        return TestResult(
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            duration_ms=duration_ms,
            raw_summary=f"{passed}/{total} pass" + (f"; {failed} fail" if failed else "") + (f"; {skipped} skipped" if skipped else ""),
            exit_code=exit_code,
        )

    @classmethod
    def _last_meaningful_line(cls, output: str) -> str:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        for line in reversed(lines):
            if not line.startswith("#"):
                return line[:200]
        return lines[-1][:200] if lines else ""


def parse_test_output(output: str, exit_code: int, command: str = "") -> TestResult:
    return TestResultParser.parse(output, exit_code, command)